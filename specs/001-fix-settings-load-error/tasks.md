# Tasks: Fix AttributeError in settings loading

**Input**: Design documents from `/home/akihiro/文書/develop/git/akuroiwa/py-chessboardjs/specs/001-fix-settings-load-error/`
**Prerequisites**: plan.md, spec.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story (US1, US2, etc.)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*No setup tasks are required for this feature.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*No foundational tasks are required for this feature.*

----- 

## Phase 3: User Story 1 - Application starts without crashing (Priority: P1) 🎯 MVP

**Goal**: Fix the startup crash caused by an `AttributeError` and ensure the UCI engine path is correctly registered and saved using a native file dialog.

**Independent Test**: The application can be launched successfully without crashing, and a valid UCI engine path can be registered via the GUI.

### Implementation for User Story 1

- [x] T001 [US1] Modify the `load_settings` function in `py_chessboardjs/start.py` to correctly parse the configuration file and prevent the `AttributeError`. The fix should also gracefully handle cases where the configuration file or specific keys are missing, falling back to default values.
- [x] T002 [US1] Modify the `register_uci_engine` function in `py_chessboardjs/start.py` to use `self.window.create_file_dialog()` to open a native file dialog, return the selected path, and save this path to the settings file.
- [x] T003 [US1] In `py_chessboardjs/index.html`, replace the `<input type="file" name="uci_engine">` element with a button that triggers the file selection process and add an element to display the selected path.
- [x] T004 [US1] In `py_chessboardjs/js/my-script.js`, create a new JavaScript function (e.g., `selectUciEnginePath`) that calls `pywebview.api.register_uci_engine()` and updates the UI with the selected path.
- [x] T005 [US1] In `py_chessboardjs/start.py`, update the `uci_engine_move` function to include validation for the UCI engine path, preventing crashes if the path is invalid or the engine is not executable, and providing user feedback.
- [x] T006 [US1] Manually verify the fix by following all steps in `specs/001-fix-settings-load-error/quickstart.md`, ensuring the application starts, the UCI engine can be registered correctly, and no longer crashes.

**Checkpoint**: At this point, the application should be stable on startup, and the primary bug will be resolved.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

*No polishing tasks are required for this bugfix.*

---

## Dependencies & Execution Order

- **User Story 1 (P1)**: Tasks T001, T002, T003, T004, T005, T006 are sequential.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1.  Complete Phase 3: User Story 1.
2.  **STOP and VALIDATE**: Test the fix independently using the `quickstart.md` guide.