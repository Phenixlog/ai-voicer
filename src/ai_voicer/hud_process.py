from __future__ import annotations

import json
import threading
from typing import Any

from AppKit import (
    NSApp,
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSApplicationActivationPolicyProhibited,
    NSBackingStoreBuffered,
    NSColor,
    NSFont,
    NSScreen,
    NSStatusWindowLevel,
    NSTextField,
    NSView,
    NSWindow,
    NSWindowStyleMaskBorderless,
)
from Foundation import NSMakeRect
from PyObjCTools import AppHelper


class HUDController:
    def __init__(self):
        self._hide_gen = 0
        self._state = "idle"
        self.window = None
        self.label = None
        self.dot = None
        self.content = None
        self._build_window()

    def _build_window(self) -> None:
        width = 160
        height = 36
        screen = NSScreen.mainScreen().frame()
        visible = NSScreen.mainScreen().visibleFrame()
        # Position just below menu bar / notch, centered horizontally
        x = (screen.size.width - width) / 2.0
        y = visible.origin.y + visible.size.height - height - 6

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, width, height),
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(True)
        self.window.setLevel_(NSStatusWindowLevel)
        self.window.setIgnoresMouseEvents_(True)
        self.window.orderOut_(None)

        content: NSView = self.window.contentView()
        self.content = content
        content.setWantsLayer_(True)
        content.layer().setCornerRadius_(18.0)
        content.layer().setMasksToBounds_(True)
        content.layer().setBorderWidth_(1.0)
        content.layer().setBorderColor_(
            NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.08).CGColor()
        )
        content.layer().setBackgroundColor_(
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1, 0.1, 0.1, 0.75).CGColor()
        )

        # Small colored dot (8x8, fully rounded)
        self.dot = NSView.alloc().initWithFrame_(NSMakeRect(14, 14, 8, 8))
        self.dot.setWantsLayer_(True)
        self.dot.layer().setCornerRadius_(4.0)
        self.dot.layer().setBackgroundColor_(
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.9, 0.45, 1.0).CGColor()
        )
        content.addSubview_(self.dot)

        # Short label next to the dot
        self.label = NSTextField.labelWithString_("Pret")
        self.label.setFrame_(NSMakeRect(30, 8, 116, 20))
        self.label.setTextColor_(
            NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.9)
        )
        self.label.setFont_(NSFont.systemFontOfSize_(12))
        content.addSubview_(self.label)

    def apply_event(self, payload: dict[str, Any]) -> None:
        state = payload.get("state", "idle")
        text = payload.get("text")

        if state == "close":
            NSApp().terminate_(None)
            return
        if state == "recording":
            self._show(text or "Ecoute...")
            return
        if state == "transcribing":
            self._show(text or "Transcription...")
            return
        if state == "ready":
            self._show(text or "Collé")
            self._auto_hide(1.0)
            return
        if state == "error":
            self._show(text or "Erreur")
            self._auto_hide(1.8)
            return

        self._hide()

    def _show(self, text: str) -> None:
        self._hide_gen += 1
        self._state = "active"
        self.label.setStringValue_(text)
        self._apply_palette(text)
        # Do not steal focus (prevents menu-bar title flicker).
        self.window.orderFront_(None)

    def _hide(self) -> None:
        self._hide_gen += 1
        self._state = "idle"
        self.window.orderOut_(None)

    def _apply_palette(self, text: str) -> None:
        if not self.dot:
            return
        low = text.lower()
        if "ecoute" in low:
            dot_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.3, 0.3, 1.0)
        elif "transcription" in low:
            dot_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.7, 0.3, 1.0)
        elif "erreur" in low or "echec" in low:
            dot_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.3, 0.3, 1.0)
        else:
            dot_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.9, 0.45, 1.0)
        self.dot.layer().setBackgroundColor_(dot_color.CGColor())

    def _auto_hide(self, seconds: float) -> None:
        token = self._hide_gen

        def worker() -> None:
            import time

            time.sleep(seconds)
            AppHelper.callAfter(self._hide_if_token, token)

        threading.Thread(target=worker, daemon=True).start()

    def _hide_if_token(self, token: int) -> None:
        if token == self._hide_gen:
            self._hide()


def _stdin_reader(controller: HUDController) -> None:
    import sys

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        AppHelper.callAfter(controller.apply_event, payload)

    AppHelper.callAfter(controller.apply_event, {"state": "close"})


def main() -> None:
    app = NSApplication.sharedApplication()
    # Keep only the floating center HUD; do not appear as an app in UI chrome.
    app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)

    controller = HUDController()
    reader = threading.Thread(target=_stdin_reader, args=(controller,), daemon=True)
    reader.start()
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()
