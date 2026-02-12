import subprocess
import time


def paste_text_to_active_app(text: str) -> None:
    previous_clipboard = subprocess.run(
        ["pbpaste"], capture_output=True, text=True, check=False
    ).stdout
    subprocess.run(["pbcopy"], input=text, text=True, check=True)
    subprocess.run(
        [
            "osascript",
            "-e",
            'tell application "System Events" to keystroke "v" using command down',
        ],
        check=True,
    )
    time.sleep(0.15)
    subprocess.run(["pbcopy"], input=previous_clipboard, text=True, check=True)
