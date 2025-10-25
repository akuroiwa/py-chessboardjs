# Quickstart: Testing the Engine Concurrency Fix

**Feature**: Fix Engine Concurrency Error

This document provides the steps to verify that the concurrency issues have been resolved and the application is stable under stress.

## Verification Steps

### 1. Setup

- Ensure you are on the feature branch: `003-fix-engine-concurrency`.
- Make sure all dependencies are installed.

### 2. Execution

Run the application using the following command from the repository root:

```bash
python py_chessboardjs/start.py --gtk
```

### 3. Test Cases

#### Test Case 1: Basic Stability

1.  Play a complete game against the UCI engine.
2.  Use various UI features throughout the game (back/forward, reset board, open PGN).
3.  **Expected Result**: The application completes the game and all UI interactions without any crashes or errors in the console related to `CancelledError` or `EngineTerminatedError`.

#### Test Case 2: Concurrency Stress Test

This test is designed to intentionally create race conditions to verify the fix is robust.

1.  Start a new game with the UCI engine playing as one color.
2.  As soon as you make a move for the human player, immediately and repeatedly click the **Reset Board** button for 5-10 seconds.
3.  **Expected Result**: The application should remain responsive. It should either reset the board cleanly or complete the engine move and then reset the board. It **must not** crash.
4.  Repeat the test using the **Open PGN** button and the back/forward navigation arrows instead of the Reset button.
5.  **Expected Result**: In all cases, the application remains stable and responsive.

#### Test Case 3: Clean Shutdown

1.  Play several moves against the engine.
2.  While the engine is in the middle of thinking (e.g., set a high depth to be sure), close the application window.
3.  **Expected Result**: The application closes cleanly without any errors in the console.
4.  Using a system process monitor (like `ps aux | grep stockfish` on Linux), verify that no orphaned chess engine processes are left running after the application has closed.
