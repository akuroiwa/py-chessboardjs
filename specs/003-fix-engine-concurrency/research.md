# Research: Engine Concurrency Refactor

**Feature**: Fix Engine Concurrency Error

## 1. Thread-Safe `pywebview` and `asyncio` Integration

- **Task**: Research thread-safe patterns for bridging `pywebview`'s synchronous API calls with an `asyncio` event loop used by a background library like `python-chess`.

- **Findings**: `pywebview` creates a new thread for each API call, which is not suitable for managing a persistent `asyncio` event loop. The `CancelledError` likely occurs when this thread is garbage collected or terminated, cancelling the future it was waiting on. The standard and most robust solution for this "sync-to-async" bridge is to run the `asyncio` event loop in its own dedicated, long-lived background thread. Communication with this thread should be done in a thread-safe manner.

- **Decision**: Implement a dedicated engine worker thread. This thread will start and manage a new `asyncio` event loop. All engine-related tasks will be submitted to this loop from the main application or `pywebview` API threads using `asyncio.run_coroutine_threadsafe()`.

- **Rationale**: This decouples the `asyncio` event loop's lifecycle from `pywebview`'s API threads. The loop runs continuously in a stable context, preventing tasks from being cancelled unexpectedly. `run_coroutine_threadsafe()` is the recommended, thread-safe way to submit work to an `asyncio` loop from another thread.

- **Alternatives Considered**:
  - **`queue.Queue`**: Using a standard `queue.Queue` to pass tasks to the worker thread. This is a valid pattern, but `run_coroutine_threadsafe()` is more direct as it's designed specifically for this `asyncio` use case and returns a future to track completion if needed.

## 2. New Engine Lifecycle Management

- **Task**: Design a new, thread-safe lifecycle management pattern for the chess engine.

- **Findings**: With a dedicated worker thread, the engine process can also be managed by that thread's `asyncio` loop. The engine can be started once and persist for the lifetime of the application. Shutdown must be handled gracefully by submitting a "quit" task to the loop when the application window closes.

- **Decision**: The `Api` class will be refactored. On initialization, it will spawn the `EngineWorker` thread. The `uci_engine_move` method will no longer block; it will be an async-dispatcher that submits the calculation to the worker thread. The worker thread, upon completing the calculation, will use a thread-safe callback (or `window.evaluate_js`) to push the result to the UI. The `on_closed` method will be simplified to signal the worker thread to shut down the engine and terminate its loop.

- **Rationale**: This creates a clear separation of concerns. The `Api` class handles UI interaction, and the `EngineWorker` handles all aspects of engine communication and lifecycle. This is a much more stable and scalable architecture.

- **Alternatives Considered**:
  - **Global Engine Object**: A global engine object could be used, but this would require careful locking and would not solve the underlying `asyncio` event loop problem. The worker thread pattern solves both issues at once.
