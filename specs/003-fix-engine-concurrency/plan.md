# Implementation Plan: Fix Engine Concurrency Error

**Branch**: `003-fix-engine-concurrency` | **Date**: 2025-10-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-fix-engine-concurrency/spec.md`

## Summary

This plan addresses the root cause of application instability: a `concurrent.futures.CancelledError` that occurs due to conflicts between `pywebview`'s threading model and the `python-chess` library's `asyncio`-based engine communication. The previous approach of simply catching exceptions was insufficient.

The new technical approach involves a significant architectural refactor: a dedicated worker thread will be created to host an `asyncio` event loop for all engine communication. This decouples the engine's lifecycle from the short-lived `pywebview` API threads, preventing the race conditions that lead to the `CancelledError`.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `pywebview`, `python-chess`, `threading`, `asyncio`
**Storage**: N/A
**Testing**: `pytest`
**Target Platform**: Linux (GTK), Windows, macOS
**Project Type**: Single project (Desktop GUI application).
**Constraints**: The solution must be thread-safe and prevent race conditions between the UI thread and the engine worker thread.
**NEEDS CLARIFICATION**: What is the most robust and maintainable pattern for managing a dedicated `asyncio` event loop in a separate thread while safely communicating with it from a multi-threaded, synchronous environment like `pywebview`?

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- The project constitution is a template. This plan, involving a refactor for stability, aligns with general principles of building robust software.

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-engine-concurrency/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
# The fix will involve significant refactoring of the Api class
# and engine handling logic within this file.
py_chessboardjs/
└── start.py

# The frontend will need to be adapted to handle asynchronous
# engine moves pushed from the backend.
py_chessboardjs/js/
└── my-script.js
```

**Structure Decision**: The existing single-project structure will be maintained. The core changes will be a refactoring within `py_chessboardjs/start.py` to introduce a thread-safe engine communication architecture.

## Complexity Tracking

N/A