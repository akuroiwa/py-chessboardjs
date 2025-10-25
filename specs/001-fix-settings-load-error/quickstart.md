# Quickstart: Verifying the AttributeError Fix

This guide explains how to verify that the `AttributeError` on startup has been resolved.

## Verification Steps

1.  **Checkout the branch**:
    ```bash
    git checkout 001-fix-settings-load-error
    ```

2.  **Run the application**:
    - It is recommended to run the application from within a virtual environment.
    - Execute the following command from the root of the repository:
    ```bash
    python py_chessboardjs/start.py --gtk
    ```

3.  **Confirm Success**:
    - The application's main GUI window should appear.
    - Check the terminal output. There should be no `AttributeError: 'NoneType' object has no attribute 'lower'` traceback.

## Testing the Edge Case (Optional)

To ensure the application correctly handles a missing settings file:

1.  **Delete the settings file**:
    ```bash
    rm ~/.cache/py-chessboardjs/settings.ini
    ```

2.  **Re-run the application**:
    ```bash
    python py_chessboardjs/start.py --gtk
    ```

3.  **Confirm Success**:
    - The application should start successfully.
    - A new `settings.ini` file should be created in `~/.cache/py-chessboardjs/` with default values.
