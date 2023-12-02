# py-chessboardjs
Chess GUI using pywebview and chessboard.js.

[![Documentation Status](https://readthedocs.org/projects/chess-ant/badge/?version=latest)](https://chess-ant.readthedocs.io/en/latest/?badge=latest)
This is a part of [Chess-Ant](https://github.com/akuroiwa/chess-ant) project.
That manual will be updated soon.

Chess-Ant is currently too slow to function as a chess engine.  To make matters worse, there is a glitch in the call to chess-ant.  It is possible to experiment by loading pgn and having it solve the problem.


## Installation

Please read the [pywebview](https://pywebview.flowrl.com/) and [PyGObject](https://pygobject.readthedocs.io/en/latest/) manuals, and install dependent packages before proceeding.

If you are Ubuntu user:
```bash
sudo apt install python3-venv
python3.11 -m venv ~/.venv3.11
source ~/.venv3.11/bin/activate
which pip
pip install py-chessboardjs[gtk]
```

If you want to install it on local repository:

```bash
cd py-chessboardjs
pip install .[gtk]
```

QT user:
```bash
pip install py-chessboardjs[qt]
```

CEF user:
```bash
pip install py-chessboardjs[cef]
```

Install your favorite UCI engine:
```bash
sudo apt install stockfish
```


## Usage

```bash
py-chessboardjs-gtk
```

```bash
py-chessboardjs-qt
```

```bash
py-chessboardjs-cef
```
