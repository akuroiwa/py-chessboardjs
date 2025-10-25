import os
import webview
import chess
from chess_ant import chess_ant
# import chess_ant
import chess
import chess.engine
import chess.pgn
import json
import configparser
from pathlib import Path
from collections import deque
import concurrent.futures
import argparse
import threading
import asyncio
import queue

"""
Chess GUI using pywebview and chessboard.js.
"""


class EngineWorker(threading.Thread):
    def __init__(self, api_callback):
        super().__init__()
        self.daemon = True
        self.tasks = queue.Queue()
        self.api_callback = api_callback
        self.loop = None
        self.engine = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())
        self.loop.close()

    async def main(self):
        while True:
            task, data = self.tasks.get()
            if task == 'play':
                await self.play_move(data)
            elif task == 'quit':
                break
        await self.shutdown_engine()

    async def play_move(self, data):
        board = data['board']
        limit = data['limit']
        if not self.engine:
            await self.init_engine(data['uci_path'])
        
        if self.engine:
            try:
                result = await self.engine.play(board, limit)
                self.api_callback(board.fen(), result.move)
            except Exception as e:
                print(f"Engine error: {e}")

    async def init_engine(self, uci_path):
        try:
            _, self.engine = await chess.engine.popen_uci(uci_path)
        except Exception as e:
            print(f"Failed to init engine: {e}")

    async def shutdown_engine(self):
        if self.engine:
            await self.engine.quit()
            self.engine = None

    def submit_task(self, task, data=None):
        self.tasks.put((task, data))


class Api():
    def __init__(self):
        self.window = None
        self.engine_worker = EngineWorker(self._engine_move_callback)
        self.engine_worker.start()
        self.load_settings()  # Load configuration when creating instance
        # self.pgn will hold a file path (string) or None; do NOT keep open file objects here
        self.pgn = None
        self.fen = None
        self.stack = []
        self.board = None
        self.games = []
        self.current_game_index = 0

    def _engine_move_callback(self, original_fen, move):
        if move is not None:
            # Check if the board state has changed since the engine started thinking
            if self.board.fen() != original_fen:
                print("Engine move discarded: Board state changed.")
                return

            san = self.board.san(move)
            self.board.push(move)
            if self.window:
                self.window.evaluate_js(f'receiveEngineMove("{san}");')

    # def reset_game_board(self):
    def reset_game_board(self, fen=None):
        game = chess.pgn.Game()
        # self.board = game.board()
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = game.board()
        # self.board = chess.Board()
        self.stack = self.board.move_stack

    def update_game_board(self, san):
        try:
            self.board.push_san(san)
            return self.board.fen()
        except chess.IllegalMoveError as e:
            error_message = f"Illegal move: {san}\n{e}"
            # Use json.dumps to safely escape the error message for JavaScript
            self.window.evaluate_js(f'alert({json.dumps(error_message)});')
            return None

    # def chess_ant_move(self, fen):
    def chess_ant_move(self):
        fen = self.board.fen()
        board = chess.Board(fen)
        print(f'Population: {self.population}')
        print(f'Generation: {self.generation}')
        # pop, hof, stats, move, uci = chess_ant.main(fen=fen, population=self.population, generation=self.generation)
        result_dict = chess_ant.main(fen=fen, population=self.population, generation=self.generation)

        best_move = result_dict["best_move"]
        san = board.san(best_move)
        print(san)
        self.board.push(best_move)
        return san

    # def uci_engine_move(self, fen):
    def uci_engine_move(self):
        if not self.uci_engine or not os.path.exists(self.uci_engine) or not os.access(self.uci_engine, os.X_OK):
            error_message = f"UCI engine path is invalid or not executable: {self.uci_engine}. Please register a valid engine."
            print(error_message)
            self.window.evaluate_js(f'alert("{error_message}");')
            return

        task_data = {
            'board': self.board.copy(),
            'limit': chess.engine.Limit(self.depth),
            'uci_path': self.uci_engine
        }
        self.engine_worker.submit_task('play', task_data)

    def on_closed(self):
        if self.engine_worker:
            self.engine_worker.submit_task('quit')
            self.engine_worker.join()

    def open_pgn_dialog(self):
        file_types = ('PGN File (*.pgn)', 'All files (*.*)')
        result = self.window.create_file_dialog(webview.FileDialog.OPEN, file_types=file_types)
        # create_file_dialog may return None (if cancelled) or an empty list; guard it
        if not result:
            return None
        file_path = result[0]
        if not file_path:
            return None

        if os.path.exists(file_path):
            # Do NOT store an open file object on the Api instance (pywebview will try to inspect it).
            # Store the path (string) and let load_games_from_file open/close the file when needed.
            self.pgn = file_path

            prev_games = self.games[:]  # Save the previous state of self.games
            self.games = []  # Initialize games here to clear previous games
            self.load_games_from_file()

            if self.games:  # Check if games were loaded successfully
                game = self.games[0]
                self.stack = [move for move in game.mainline_moves()]
                self.board = game.board()
                return self.board.fen()
            else:
                # Revert to the previous state of self.games
                self.games = prev_games
                return None
        else:
            return None

    def save_pgn_dialog(self):
        file_types = ('PGN File (*.pgn)', 'All files (*.*)')
        result = self.window.create_file_dialog(webview.FileDialog.SAVE, file_types=file_types)
        if not result:
            return None
        file_path = result[0]
        if not file_path:
            return None
        dir_path = os.path.dirname(file_path)
        pgn = self.board_to_game(self.board)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write('''

''')  # Add blank line to separate new games
            f.write(pgn)

    def board_to_game(self, board):
        """
        This is based on the code of
        `How to create pgn from a game play #63 <https://github.com/niklasf/python-chess/issues/63>`__.
        """
        game = chess.pgn.Game()

        # Undo all moves.
        switchyard = deque()
        while board.move_stack:
            switchyard.append(board.pop())

        game.setup(board)
        node = game

        # Replay all moves.
        while switchyard:
            move = switchyard.pop()
            node = node.add_variation(move)
            board.push(move)

        game.headers["Result"] = board.result()
        return str(game)

    def load_games_from_file(self):
        # load from path stored in self.pgn (string). Do not rely on self.pgn being an open file object.
        if not self.pgn:
            return

        # Ensure it's a path string
        file_path = self.pgn
        try:
            with open(file_path, 'r') as pgn_file:
                while True:
                    game = chess.pgn.read_game(pgn_file)
                    if game is None:
                        break
                    self.games.append(game)
        except Exception as e:
            # On error, leave self.games empty (caller will revert if needed)
            print(f"Failed to load PGN file {file_path}: {e}")

    def load_current_game_fen(self):
        if 0 <= self.current_game_index < len(self.games):
            game = self.games[self.current_game_index]
            self.board = game.board()
            self.stack = [move for move in game.mainline_moves()]
            return self.board.fen()
        return None

    def switch_to_previous_game(self):
        if self.current_game_index > 0:
            self.current_game_index -= 1
        return self.load_current_game_fen()

    def switch_to_next_game(self):
        if self.current_game_index < len(self.games) - 1:
            self.current_game_index += 1
        return self.load_current_game_fen()

    def backward_icon(self):
        self.board.pop()
        return self.board.fen()

    def forward_icon(self):
        move = self.stack[len(self.board.move_stack)]
        self.board.push(move)
        return self.board.fen()

    def can_backward(self):
        return len(self.board.move_stack) > 0

    def can_forward(self):
        return len(self.board.move_stack) < len(self.stack)

    def register_uci_engine(self):
        result = self.window.create_file_dialog(webview.FileDialog.OPEN)
        if not result:
            return None
        file_path = result[0]
        if file_path and os.path.exists(file_path):
            # store as string path
            self.uci_engine = file_path
            # Save the selected engine path to settings
            self.save_settings({'uci_engine': file_path})
            return file_path # Return the path to the frontend
        return None # Return None if no valid file was selected or it doesn't exist

    def load_settings(self):
        # Get configuration file path to user folder
        if os.name == 'posix':
            cfg_path = Path(Path.home(), '.cache/py-chessboardjs/settings.ini')
        elif os.name == 'nt':
            cfg_path = Path(Path.home(), 'py-chessboardjs', 'settings.ini')
        else:
            cfg_path = Path('py-chessboardjs', 'settings.ini')

        # Keep a string path for exposing to pywebview
        self.config_path = str(cfg_path)

        if cfg_path.exists():
            config = configparser.ConfigParser()
            config.read(self.config_path)
            # Protect against missing keys with defaults
            try:
                self.uci_engine = config['Settings']['uci_engine']
                self.depth = int(config['Settings'].get('depth', '20'))
                self.population = int(config['Settings'].get('population', '500'))
                self.generation = int(config['Settings'].get('generation', '15'))
            except Exception:
                # Fallback defaults if config malformed
                self.uci_engine = '/usr/games/stockfish'
                self.depth = 20
                self.population = 500
                self.generation = 15
        else:
            # Default value if configuration file does not exist
            self.uci_engine = '/usr/games/stockfish'
            self.depth = 20
            self.population = 500
            self.generation = 15

            # Create the configuration file if it does not exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = configparser.ConfigParser()
            config['Settings'] = {
                'uci_engine': str(self.uci_engine),
                'depth': str(self.depth),
                'population': str(self.population),
                'generation': str(self.generation)
            }
            with open(self.config_path, 'w') as configfile:
                config.write(configfile)

    def save_settings(self, settings):
        config = configparser.ConfigParser()

        # Load configuration file
        # self.config_path is a string path
        config.read(self.config_path)

        # Create 'Settings' section and add settings
        if 'Settings' not in config:
            config['Settings'] = {}

        for key, value in settings.items():
            config['Settings'][key] = value

        # Write configuration file
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

        # After saving settings, load them immediately
        self.load_settings()


html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'index.html'))

def run_gtk_gui():
    api = Api()
    api.window = webview.create_window('Chess-Ant Board', html_path, js_api=api, min_size=(600, 450))
    api.window.events.closed += api.on_closed
    webview.start(gui="gtk")
    # webview.start(gui="gtk", debug=True)

def run_qt_gui():
    api = Api()
    api.window = webview.create_window('Chess-Ant Board', html_path, js_api=api, min_size=(600, 450))
    api.window.events.closed += api.on_closed
    webview.start(gui="qt")
    # webview.start(gui="qt", debug=True)

def run_cef_gui():
    api = Api()
    api.window = webview.create_window('Chess-Ant Board', html_path, js_api=api, min_size=(600, 450))
    api.window.events.closed += api.on_closed
    webview.start(gui="cef")
    # webview.start(gui="cef", debug=True)


if __name__ == '__main__':
    # api = Api()
    # api.window = webview.create_window('Chess-Ant Board', html_path, js_api=api, min_size=(600, 450))
    # # webview.create_window('Chess-Ant Board', html_path, js_api=api, min_size=(600, 450))

    # api.window.events.closed += api.on_closed
    # # webview.start(gui="qt")
    # # webview.start(gui="qt", debug=True)
    # # webview.start(gui="gtk", debug=True)
    # webview.start(gui="gtk")

    parser = argparse.ArgumentParser(description='Run the chessboard GUI.')
    parser.add_argument('--gtk', action='store_true', help='Run the GTK version of the GUI.')
    parser.add_argument('--qt', action='store_true', help='Run the Qt version of the GUI.')
    parser.add_argument('--cef', action='store_true', help='Run the CEF version of the GUI.')

    args = parser.parse_args()

    if args.gtk:
        run_gtk_gui()
    elif args.qt:
        run_qt_gui()
    else:
        print('Please specify --gtk or --qt to run the GUI.')
        run_gtk_gui()