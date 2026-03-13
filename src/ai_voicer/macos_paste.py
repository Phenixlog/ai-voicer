import logging
import subprocess
import time


def paste_text_to_active_app(text: str) -> None:
    """Copy text to clipboard, simulate Cmd+V, then restore previous clipboard."""
    previous_clipboard = subprocess.run(
        ["pbpaste"], capture_output=True, text=True, check=False
    ).stdout

    subprocess.run(["pbcopy"], input=text, text=True, check=True)

    for attempt in range(2):
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to keystroke "v" using command down',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            break
        logging.warning("Paste attempt %d failed: %s", attempt + 1, result.stderr.strip())
        time.sleep(0.3)

    # Wait for the target app to process the paste before restoring clipboard.
    time.sleep(0.4)
    subprocess.run(["pbcopy"], input=previous_clipboard, text=True, check=True)
