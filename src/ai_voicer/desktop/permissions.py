"""macOS permission checks/requests for desktop onboarding."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
import threading


@dataclass
class PermissionState:
    microphone: str
    accessibility: str
    input_monitoring: str


def _normalize_state(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"granted", "denied", "unknown"}:
        return lowered
    return "unknown"


def _check_microphone() -> str:
    try:
        from AVFoundation import AVCaptureDevice, AVMediaTypeAudio  # type: ignore

        # AVAuthorizationStatus:
        # 0=notDetermined, 1=restricted, 2=denied, 3=authorized
        status = int(AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio))
        if status == 3:
            return "granted"
        if status in {1, 2}:
            return "denied"
        return "unknown"
    except Exception:
        return "unknown"


def _request_microphone() -> str:
    try:
        from AVFoundation import AVCaptureDevice, AVMediaTypeAudio  # type: ignore

        done = threading.Event()

        def callback(granted: bool) -> None:
            del granted
            done.set()

        AVCaptureDevice.requestAccessForMediaType_completionHandler_(AVMediaTypeAudio, callback)
        done.wait(timeout=2.0)
        return _check_microphone()
    except Exception:
        open_privacy_settings("Microphone")
        return "unknown"


def _check_accessibility() -> str:
    try:
        from Quartz import AXIsProcessTrusted  # type: ignore

        return "granted" if AXIsProcessTrusted() else "denied"
    except Exception:
        return "unknown"


def _request_accessibility() -> str:
    try:
        from Quartz import AXIsProcessTrustedWithOptions  # type: ignore
        from Quartz import kAXTrustedCheckOptionPrompt  # type: ignore

        AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True})
        time.sleep(0.1)
        return _check_accessibility()
    except Exception:
        open_privacy_settings("Accessibility")
        return "unknown"


def _check_input_monitoring() -> str:
    try:
        from Quartz import CGPreflightListenEventAccess  # type: ignore

        return "granted" if CGPreflightListenEventAccess() else "denied"
    except Exception:
        return "unknown"


def _request_input_monitoring() -> str:
    try:
        from Quartz import CGRequestListenEventAccess  # type: ignore

        CGRequestListenEventAccess()
        time.sleep(0.1)
        return _check_input_monitoring()
    except Exception:
        open_privacy_settings("ListenEvent")
        return "unknown"


def get_permission_state() -> PermissionState:
    return PermissionState(
        microphone=_normalize_state(_check_microphone()),
        accessibility=_normalize_state(_check_accessibility()),
        input_monitoring=_normalize_state(_check_input_monitoring()),
    )


def request_permission(permission: str) -> PermissionState:
    name = permission.strip().lower()
    if name == "microphone":
        _request_microphone()
    elif name == "accessibility":
        _request_accessibility()
    elif name in {"input", "input_monitoring", "input-monitoring"}:
        _request_input_monitoring()
    return get_permission_state()


def open_privacy_settings(section: str) -> None:
    suffix = section.strip()
    uri = f"x-apple.systempreferences:com.apple.preference.security?Privacy_{suffix}"
    subprocess.run(["open", uri], check=False)

