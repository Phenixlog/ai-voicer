"""Desktop control layer for local daemon lifecycle and SaaS auth."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ..config import load_config
from ..saas_client import SaasAuthManager
from .permissions import PermissionState, get_permission_state, open_privacy_settings, request_permission


LogFn = Callable[[str], None]


@dataclass
class DesktopStatus:
    backend_url: str
    hotkey: str
    trigger_mode: str
    is_logged_in: bool
    email: str
    daemon_running: bool


@dataclass
class DesktopDiagnostics:
    backend_url: str
    hotkey: str
    trigger_mode: str
    is_logged_in: bool
    email: str
    daemon_running: bool
    autostart_installed: bool
    credentials_file: str
    daemon_log_file: str
    permissions: PermissionState


class DesktopAppController:
    """Manage desktop login status and daemon process lifecycle."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.python_bin = self._resolve_python_bin()
        self._daemon_proc: Optional[subprocess.Popen[str]] = None
        self._daemon_log_thread: Optional[threading.Thread] = None
        self._log_fn: Optional[LogFn] = None
        self.config_dir = Path.home() / "Library" / "Application Support" / "Theoria"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_config_file = self.config_dir / "desktop_app.json"
        self.daemon_log_file = self.config_dir / "daemon.log"
        self._permissions_cache: Optional[PermissionState] = None
        self._permissions_cached_at: float = 0.0

        prefs = self._load_desktop_prefs()
        persisted_backend = prefs.get("backend_url")
        try:
            config = load_config()
            default_backend = config.backend_url
            default_hotkey = config.hotkey
            default_trigger_mode = config.trigger_mode
        except Exception:
            default_backend = None
            default_hotkey = "f8"
            default_trigger_mode = "hold"
        self.backend_url = persisted_backend or default_backend or "http://127.0.0.1:8090"
        self.hotkey = str(prefs.get("hotkey") or default_hotkey or "f8").lower()
        self.trigger_mode = str(prefs.get("trigger_mode") or default_trigger_mode or "hold").lower()
        self.auth = SaasAuthManager(self.backend_url)

    def _resolve_python_bin(self) -> str:
        venv_python = self.root_dir / ".venv" / "bin" / "python"
        if venv_python.exists():
            return str(venv_python)
        return "python3"

    def set_backend_url(self, backend_url: str) -> str:
        url = backend_url.strip()
        if not url:
            raise ValueError("Backend URL is required.")
        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"

        self.backend_url = url.rstrip("/")
        self.auth = SaasAuthManager(self.backend_url)
        self._save_desktop_prefs()
        return self.backend_url

    def set_local_settings(self, hotkey: str, trigger_mode: str) -> tuple[str, str]:
        normalized_hotkey = hotkey.strip().lower()
        normalized_mode = trigger_mode.strip().lower()
        if not normalized_hotkey:
            raise ValueError("Hotkey is required.")
        if normalized_mode not in {"hold", "toggle"}:
            raise ValueError("Trigger mode must be hold or toggle.")
        self.hotkey = normalized_hotkey
        self.trigger_mode = normalized_mode
        self._save_desktop_prefs()
        return self.hotkey, self.trigger_mode

    def login(self, email: str) -> bool:
        success = self.auth.login(email=email.strip())
        if success:
            self._save_desktop_prefs()
            # If an autostart daemon is already running from before login,
            # restart it so it picks up fresh credentials immediately.
            if self._list_daemon_pids():
                self.reset_daemon_instances()
        return success

    def logout(self) -> None:
        self.auth.logout()

    def status(self) -> DesktopStatus:
        creds = self.auth._load_credentials()
        daemon_running = bool(self._list_daemon_pids())
        return DesktopStatus(
            backend_url=self.backend_url,
            hotkey=self.hotkey,
            trigger_mode=self.trigger_mode,
            is_logged_in=self.auth.is_logged_in(),
            email=creds.email or "",
            daemon_running=daemon_running,
        )

    def start_daemon(self, log_fn: LogFn) -> None:
        if self._list_daemon_pids():
            raise RuntimeError(
                "Daemon is already running (autostart or terminal instance). "
                "Stop existing daemon before starting a new one."
            )
        if not self.auth.is_logged_in():
            raise RuntimeError("Login required before starting daemon.")

        env = {
            "PYTHONPATH": str(self.root_dir / "src"),
            "AI_VOICER_BACKEND_URL": self.backend_url,
            "AI_VOICER_HOTKEY": self.hotkey,
            "AI_VOICER_TRIGGER_MODE": self.trigger_mode,
        }

        # Keep system env and override only required values.
        merged_env = {**os.environ, **env}
        command = [self.python_bin, str(self.root_dir / "run_saas_daemon.py"), "run"]
        self._daemon_proc = subprocess.Popen(
            command,
            cwd=str(self.root_dir),
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self._log_fn = log_fn
        self._daemon_log_thread = threading.Thread(target=self._stream_daemon_logs, daemon=True)
        self._daemon_log_thread.start()

    def _stream_daemon_logs(self) -> None:
        proc = self._daemon_proc
        if not proc or not proc.stdout:
            return
        self.daemon_log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.daemon_log_file.open("a", encoding="utf-8") as log_file:
            log_file.write("=== daemon session start ===\n")
            log_file.flush()
        for line in proc.stdout:
            with self.daemon_log_file.open("a", encoding="utf-8") as log_file:
                log_file.write(line)
            if self._log_fn:
                self._log_fn(line.rstrip())
        with self.daemon_log_file.open("a", encoding="utf-8") as log_file:
            log_file.write("=== daemon session end ===\n")
        if self._log_fn:
            self._log_fn("Daemon stopped.")

    def stop_daemon(self) -> None:
        proc = self._daemon_proc
        if not proc:
            return
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        self._daemon_proc = None

    def install_autostart(self) -> str:
        script = self.root_dir / "install_launch_agent.sh"
        result = subprocess.run(
            ["/bin/bash", str(script)],
            cwd=str(self.root_dir),
            text=True,
            capture_output=True,
            check=False,
            env={
                **os.environ,
                "AI_VOICER_BACKEND_URL": self.backend_url,
                "AI_VOICER_HOTKEY": self.hotkey,
                "AI_VOICER_TRIGGER_MODE": self.trigger_mode,
                "THEORIA_ROOT_DIR": str(self.root_dir),
            },
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Failed to install LaunchAgent.")
        return result.stdout.strip()

    def uninstall_autostart(self) -> str:
        script = self.root_dir / "uninstall_launch_agent.sh"
        result = subprocess.run(
            ["/bin/bash", str(script)],
            cwd=str(self.root_dir),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Failed to remove LaunchAgent.")
        return result.stdout.strip()

    def is_autostart_installed(self) -> bool:
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.keyvan.theoria-saas-daemon.plist"
        return plist_path.exists()

    def get_permission_state(self) -> PermissionState:
        now = time.time()
        if self._permissions_cache and (now - self._permissions_cached_at) < 5.0:
            return self._permissions_cache
        state = get_permission_state()
        self._permissions_cache = state
        self._permissions_cached_at = now
        return state

    def request_permission(self, permission: str) -> PermissionState:
        state = request_permission(permission)
        self._permissions_cache = state
        self._permissions_cached_at = time.time()
        return state

    def open_permission_settings(self, section: str) -> None:
        open_privacy_settings(section)

    def diagnostics(self) -> DesktopDiagnostics:
        status = self.status()
        return DesktopDiagnostics(
            backend_url=status.backend_url,
            hotkey=status.hotkey,
            trigger_mode=status.trigger_mode,
            is_logged_in=status.is_logged_in,
            email=status.email,
            daemon_running=status.daemon_running,
            autostart_installed=self.is_autostart_installed(),
            credentials_file=str(self.auth.credentials_file),
            daemon_log_file=str(self.daemon_log_file),
            permissions=self.get_permission_state(),
        )

    def reset_daemon_instances(self) -> str:
        """Reset duplicate daemon/hud processes and restart launch agent if installed."""
        root_pattern = f"{self.root_dir}/run_saas_daemon.py run"
        subprocess.run(["pkill", "-f", root_pattern], check=False)
        subprocess.run(["pkill", "-f", "ai_voicer/hud_process.py"], check=False)
        if self.is_autostart_installed():
            uid = str(os.getuid())
            domain = f"gui/{uid}/com.keyvan.theoria-saas-daemon"
            subprocess.run(["launchctl", "kickstart", "-k", domain], check=False)
            return "Daemon reset done. LaunchAgent restarted."
        return "Daemon reset done. Start daemon manually from the app."

    def _list_daemon_pids(self) -> list[int]:
        pattern = f"{self.root_dir}/run_saas_daemon.py run"
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        pids: list[int] = []
        for raw in result.stdout.splitlines():
            try:
                pids.append(int(raw.strip()))
            except ValueError:
                continue
        return pids

    def _load_desktop_prefs(self) -> dict:
        if not self.desktop_config_file.exists():
            return {}
        try:
            payload = json.loads(self.desktop_config_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            return {}
        return {}

    def _save_desktop_prefs(self) -> None:
        payload = {
            "backend_url": self.backend_url.rstrip("/"),
            "hotkey": self.hotkey,
            "trigger_mode": self.trigger_mode,
        }
        self.desktop_config_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
