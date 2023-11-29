import os
import webview
import chess
from chess_ant import chess_ant
# import chess_ant
import chess
import chess.engine
import chess.pgn
# import json
import configparser
from pathlib import Path
from collections import deque
import concurrent.futures
import argparse

"""
Chess GUI using pywebview and chessboard.js.
"""


class Api():
    def __init__(self):
        self.engine = None
        self.load_settings()  # Load configuration when creating instance
        self.pgn = None
        self.fen = None
        self.stack = []
        self.board = None
        self.games = []
        self.current_game_index = 0

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
        self.board.push_san(san)

    # def chess_ant_move(self, fen):
    def chess_ant_move(self):
        fen = self.board.fen()
        board = chess.Board(fen)
        print(f'Population: {self.population}')
        print(f'Generation: {self.generation}')
        # pop, hof, stats, move, uci = chess_ant.main(fen=fen, population=self.population, generation=self.generation)
        result_dict = chess_ant.main(fen=fen, population=self.population, generation=self.generation)

        # san = board.san(move)
        # print(san)
        # self.board.push(move)
        # return san

        best_move = result_dict["best_move"]
        san = board.san(best_move)
        print(san)
        self.board.push(best_move)
        return san

    # def uci_engine_move(self, fen):
    def uci_engine_move(self):
        fen = self.board.fen()
        print(fen)
        board = chess.Board(fen)
        if not self.engine:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.uci_engine)
        # result = self.engine.play(board, chess.engine.Limit(self.depth))
        try:
            result = self.engine.play(board, chess.engine.Limit(self.depth))
            san = board.san(result.move)
            print(san)
            # self.board.push_san(san)
            self.board.push(result.move)
            return san
        except concurrent.futures.CancelledError:
            # Processing when CanceledError occurs
            self.on_closed()
            print("concurrent.futures.CancelledError caused.  Quit UCI engine.")
        # finally:
        #     self.engine.quit()  # Make sure to shut down the engine

        # return san

    def on_closed(self):
        if self.engine:
            self.engine.quit()
            print("Quit UCI engine.")
        self.engine = None
        # chess_ant.ant.exit()

    def open_pgn_dialog(self):
        self.on_closed()
        file_types = ('PGN File (*.pgn)', 'All files (*.*)')
        file_path = self.window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types)[0]

        if os.path.exists(file_path):
            self.pgn = open(file_path)
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
        self.on_closed()
        # file_path = self.window.create_file_dialog(webview.SAVE_DIALOG)[0]
        file_types = ('PGN File (*.pgn)', 'All files (*.*)')
        file_path = self.window.create_file_dialog(webview.SAVE_DIALOG, file_types=file_types)[0]
        dir_path = os.path.dirname(file_path)
        pgn = self.board_to_game(self.board)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'a') as f:
            f.write('\n\n')  # Add blank line to separate new games
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
        while True:
            game = chess.pgn.read_game(self.pgn)
            if game is None:
                break
            self.games.append(game)

    def load_current_game_fen(self):
        if 0 <= self.current_game_index < len(self.games):
            game = self.games[self.current_game_index]
            self.board = game.board()
            self.stack = [move for move in game.mainline_moves()]
            return self.board.fen()
        return None

    def switch_to_previous_game(self):
        self.on_closed()
        if self.current_game_index > 0:
            self.current_game_index -= 1
        return self.load_current_game_fen()

    def switch_to_next_game(self):
        self.on_closed()
        if self.current_game_index < len(self.games) - 1:
            self.current_game_index += 1
        return self.load_current_game_fen()

    def backward_icon(self):
        self.on_closed()
        self.board.pop()
        return self.board.fen()

    def forward_icon(self):
        self.on_closed()
        move = self.stack[len(self.board.move_stack)]
        self.board.push(move)
        return self.board.fen()

    def can_backward(self):
        return len(self.board.move_stack) > 0

    def can_forward(self):
        return len(self.board.move_stack) < len(self.stack)

    def register_uci_engine(self):
        file_path = self.window.create_file_dialog(webview.OPEN_DIALOG)[0]
        print(file_path)
        if os.path.exists(file_path):
            self.uci_engine = file_path

    def load_settings(self):
        # Get configuration file path to user folder
        if os.name == 'posix':
            self.config_path = Path(Path.home(), '.cache/py-chessboardjs/settings.ini')
            # self.config_path = Path.home() / '.cache/py-chessboardjs/settings.ini'
        elif os.name == 'nt':
            self.config_path = Path(Path.home(), 'py-chessboardjs', 'settings.ini')
        else:
            self.config_path = Path('py-chessboardjs', 'settings.ini')

        if self.config_path.exists():
            config = configparser.ConfigParser()
            config.read(self.config_path)
            self.uci_engine = config['Settings']['uci_engine']
            self.depth = int(config['Settings']['depth'])
            self.population = int(config['Settings']['population'])
            self.generation = int(config['Settings']['generation'])
        else:
            # Default value if configuration file does not exist
            self.uci_engine = '/usr/games/stockfish'
            self.depth = 20
            self.population = 500
            self.generation = 15

            # Create the configuration file if it does not exist
            self.config_path.parents[0].mkdir(parents=True, exist_ok=True)
            self.config_path.touch()
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
