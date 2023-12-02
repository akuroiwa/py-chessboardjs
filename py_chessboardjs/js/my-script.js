// <script>
// --- Begin Example JS --------------------------------------------------------
// NOTE: this example uses the chess.js library:
// https://github.com/jhlywa/chess.js

var board = null
var game = new Chess()

var whiteEngineSelect = document.getElementById('white-engine-select');
var blackEngineSelect = document.getElementById('black-engine-select');

function onDragStart (source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false

    // only pick up pieces for White
    // if (piece.search(/^b/) !== -1) return false

    // or if it's not that side's turn
    if (
	(game.turn() === 'w' && piece.search(/^b/) !== -1) ||
	    (game.turn() === 'b' && piece.search(/^w/) !== -1)
    ) {
	return false;
    }
}

function makeRandomMove () {
    var possibleMoves = game.moves()

    // game over
    if (possibleMoves.length === 0) return

    var randomIdx = Math.floor(Math.random() * possibleMoves.length)
    game.move(possibleMoves[randomIdx])
}

function makeComputerMove() {
    var possibleMoves = game.moves();

    // game over
    if (possibleMoves.length === 0) return;

    var selectedEngine = game.turn() === 'w' ? whiteEngineSelect.value : blackEngineSelect.value;
    // var fen = game.fen();

    switch (selectedEngine) {
    case 'chess-ant':
	// const population = 500;
	// const generation = 15;
	// var population = parseInt(document.getElementsByName('population')[0].value);
	// var generation = parseInt(document.getElementsByName('generation')[0].value);

	// pywebview.api.chess_ant_move(fen).then(function(move_str) {
	pywebview.api.chess_ant_move().then(function(move_str) {
            game.move(move_str);
            board.position(game.fen());
	});
	break;
    case 'uci':
	// var uciEnginePath = '/usr/games/stockfish';
	// var uciDepth = 8;
	// var uciEnginePath = document.getElementById('uciEnginePath').value
	// var uciDepth = document.getElementById('uciDepth').value

	// pywebview.api.uci_engine_move(fen).then(function(move_str) {
	pywebview.api.uci_engine_move().then(function(move_str) {
            game.move(move_str);
            board.position(game.fen());
	});
	break;
    default:
	makeRandomMove();
	break;
    }
}

function makeUserMove(source, target) {
    var promotionSelect = document.getElementById('promotion-select');
    var selectedPromotion = promotionSelect.value;
    // see if the move is legal
    var move = game.move({
	from: source,
	to: target,
	// promotion: 'q' // NOTE: always promote to a queen for example simplicity
	promotion: selectedPromotion
    })

    // illegal move
    // if (move === null) return 'snapback'
    if (move === null) {return 'snapback'}
    else {
	// let array = game.history();
	// let last = array.slice(-1)[0];
	let history = game.history({ verbose: true });
	let lastMove = history[history.length - 1].san;

	console.log(lastMove)
	// pywebview.api.update_game_board(last);
	pywebview.api.update_game_board(lastMove);
    }

    // console.log('game fen')
    // console.log(game.fen())

    // // move is legal, update board
    // board.position(game.fen());
}

function onDrop(source, target) {
    makeUserMove(source, target);
}

let isCastlingInProgress = false;

function onChange(oldPos, newPos) {
    console.log('Position changed:')
    console.log('Old position: ' + Chessboard.objToFen(oldPos))
    console.log('New position: ' + Chessboard.objToFen(newPos))
    console.log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    let lastMove;

    if (!game.game_over()) {
        if ((game.turn() === 'w' && whiteEngineSelect.value !== 'user') ||
            (game.turn() === 'b' && blackEngineSelect.value !== 'user')) {
            if (!isCastlingInProgress) {
                // Check if the move is a castling move
                let history = game.history({ verbose: true });
		if (history.length !== 0) {
                    lastMove = history[history.length - 1].san;
		} else {
		    lastMove = '';
		}

                if (lastMove === 'O-O' || lastMove === 'O-O-O') {
		    // Mark that castling is in progress
		    isCastlingInProgress = true;
                } else {
		    // Make the computer move immediately for non-castling moves
		    // makeComputerMove();
		    window.setTimeout(makeComputerMove, 250);
                }
            } else {
                // Delay the computer move for castling
                window.setTimeout(() => {
                    makeComputerMove();
                    // Reset the flag for castling completion
                    isCastlingInProgress = false;
                }, 250);
            }
        }
    }
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen())
}

$('#playBtn').on('click', function () {
    var startFenInput = document.getElementsByName('startFen')[0].value
    if (startFenInput) {
	console.log(startFenInput);
	game.load(startFenInput);
	pywebview.api.reset_game_board(game.fen());
    } else if (game.fen() !== 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') {
	console.log('game.fen() changed.')

    // }
    // else if (game.fen()) {
    // 	console.log(game.fen())
    // } else if (game.fen() === '8/8/8/8/8/8/8/8 w - - 0 1') {
    } else if (board.fen() === '8/8/8/8/8/8/8/8') {
	game.reset()
	pywebview.api.reset_game_board();
    // 	pywebview.api.reset_game_board().then(function () {
    // 	    game.reset();
    // 	})
    }
    // board.clear
    console.log('game.fen()')
    console.log(game.fen())
    console.log('board.fen()')
    console.log(board.fen())
    board.clear();
    board.position(game.fen())
    // startFenInput.reset()
})

$('#resetBtn').on('click', function () {
    game.reset();
    board.clear();
    board.position(game.fen());
    pywebview.api.reset_game_board();
    document.getElementsByName('startFen')[0].value = ''; // Also clears user input
})

var config = {
    draggable: true,
    // position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    onChange: onChange
}
var board = Chessboard('myBoard', config)
// $(window).resize(board.resize);

$('#showOrientationBtn').on('click', function () {
    console.log('Board orientation is: ' + board.orientation())
})

$('#flipOrientationBtn').on('click', board.flip)

function changeBoardWidth() {
    var element = document.getElementById("myBoard");
    var boardWidth = document.getElementById('board-width').value;
    element.style.width = boardWidth;
    // element.style.margin = 'auto';
    // $(window).resize(board.resize);
    board.resize(boardWidth);
}

function openPgnDialog() {
    document.getElementsByName('startFen')[0].value = ''; // Clears user input
    pywebview.api.open_pgn_dialog().then(function(fen) {
    if (fen) {
        console.log("FEN String: " + fen);
	game.load(fen)
	board.clear();
	board.position(game.fen());
    }});
}

function savePgnDialog() {
    const filePath = pywebview.api.save_pgn_dialog();
    if (filePath) {
        // Added processing when a file is selected
	console.log("Save PGN to:" + filePath)
    }
}

// Handler when user clicks previous match button
function switchToPreviousGame() {
    pywebview.api.switch_to_previous_game().then(function (fen) {
        if (fen) {
            game.load(fen);
	    board.clear();
	    board.position(game.fen());
        }
    });
}

// Handler when user clicks next match button
function switchToNextGame() {
    pywebview.api.switch_to_next_game().then(function (fen) {
        if (fen) {
            game.load(fen);
	    board.clear();
	    board.position(game.fen());
        }
    });
}

$('#backwardIcon').on('click', function () {
    pywebview.api.can_backward().then(function (canBackward) {
        if (canBackward) {
            pywebview.api.backward_icon().then(function (fen) {
                if (fen) {
                    console.log("FEN String (backward_icon): " + fen);
                    // Do something here with fen or do other things as you wish
		    game.load(fen)
		    board.position(game.fen());
                }
            });
        }
    });
});

$('#forwardIcon').on('click', function () {
    pywebview.api.can_forward().then(function (canForward) {
        if (canForward) {
            pywebview.api.forward_icon().then(function (fen) {
                if (fen) {
                    console.log("FEN String (forward_icon): " + fen);
                    // Do something here with fen or do other things as you wish
		    game.load(fen)
		    board.position(game.fen());
                }
            });
        }
    });
});

function registerUciEngine() {
    const filePath = pywebview.api.register_uci_engine();
    if (filePath) {
        // Added processing when a file is selected
	return filePath
    }
    else {
	return '/usr/games/stockfish'
    }
}

function saveSettings(inputElement) {
    const name = inputElement.name;
    const value = inputElement.value;
    const settings = {};

    // Create settings to pass to Python side
    settings[name] = value;

    // Call a method to save settings on the Python side
    pywebview.api.save_settings(settings);
}

// --- End Example JS ----------------------------------------------------------
// </script>
