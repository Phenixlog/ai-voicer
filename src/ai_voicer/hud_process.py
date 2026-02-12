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
    NSProgressIndicator,
    NSProgressIndicatorStyleBar,
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
        self.progress = None
        self.content = None
        self._build_window()

    def _build_window(self) -> None:
        width = 360
        height = 84
        screen = NSScreen.mainScreen().frame()
        x = (screen.size.width - width) / 2.0
        y = (screen.size.height - height) / 2.0

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
        content.layer().setCornerRadius_(22.0)
        content.layer().setMasksToBounds_(True)
        content.layer().setBorderWidth_(1.0)
        content.layer().setBorderColor_(NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.12).CGColor())
        content.layer().setBackgroundColor_(NSColor.colorWithCalibratedWhite_alpha_(0.08, 0.93).CGColor())

        self.label = NSTextField.labelWithString_("Pret")
        self.label.setFrame_(NSMakeRect(24, 50, 312, 20))
        self.label.setTextColor_(NSColor.colorWithCalibratedWhite_alpha_(0.96, 1.0))
        self.label.setFont_(NSFont.systemFontOfSize_(15))
        content.addSubview_(self.label)

        self.progress = NSProgressIndicator.alloc().initWithFrame_(NSMakeRect(24, 22, 312, 14))
        self.progress.setStyle_(NSProgressIndicatorStyleBar)
        self.progress.setIndeterminate_(True)
        self.progress.setDisplayedWhenStopped_(False)
        self.progress.setUsesThreadedAnimation_(True)
        self.progress.setWantsLayer_(True)
        self.progress.layer().setCornerRadius_(7.0)
        self.progress.layer().setMasksToBounds_(True)
        self.progress.layer().setBackgroundColor_(NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.10).CGColor())
        content.addSubview_(self.progress)

    def apply_event(self, payload: dict[str, Any]) -> None:
        state = payload.get("state", "idle")
        text = payload.get("text")

        if state == "close":
            NSApp().terminate_(None)
            return
        if state == "recording":
            self._show(text or "Ecoute...", animate=True)
            return
        if state == "transcribing":
            self._show(text or "Transcription...", animate=True)
            return
        if state == "ready":
            self._show(text or "Pret", animate=False)
            self._auto_hide(1.0)
            return
        if state == "error":
            self._show(text or "Erreur", animate=False)
            self._auto_hide(1.8)
            return

        self._hide()

    def _show(self, text: str, animate: bool) -> None:
        self._hide_gen += 1
        self._state = "active"
        self.label.setStringValue_(text)
        self._apply_palette(text)
        if animate:
            self.progress.startAnimation_(None)
        else:
            self.progress.stopAnimation_(None)
        # Do not steal focus (prevents menu-bar title flicker).
        self.window.orderFront_(None)

    def _hide(self) -> None:
        self._hide_gen += 1
        self._state = "idle"
        self.progress.stopAnimation_(None)
        self.window.orderOut_(None)

    def _apply_palette(self, text: str) -> None:
        if not self.content:
            return
        low = text.lower()
        if "ecoute" in low:
            bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.22, 0.08, 0.10, 0.93)
            border = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.32, 0.32, 0.42)
        elif "transcription" in low:
            bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.22, 0.16, 0.06, 0.93)
            border = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.72, 0.30, 0.42)
        elif "erreur" in low or "echec" in low:
            bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.24, 0.07, 0.07, 0.93)
            border = NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.30, 0.30, 0.45)
        else:
            bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.08, 0.20, 0.11, 0.93)
            border = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.35, 0.92, 0.50, 0.45)
        self.content.layer().setBackgroundColor_(bg.CGColor())
        self.content.layer().setBorderColor_(border.CGColor())

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
