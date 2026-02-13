"""Desktop control layer for local daemon lifecycle and SaaS auth."""

from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ..config import load_config
from ..saas_client import SaasAuthManager


LogFn = Callable[[str], None]


@dataclass
class DesktopStatus:
    backend_url: str
    is_logged_in: bool
    email: str
    daemon_running: bool


class DesktopAppController:
    """Manage desktop login status and daemon process lifecycle."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.python_bin = self._resolve_python_bin()
        self._daemon_proc: Optional[subprocess.Popen[str]] = None
        self._daemon_log_thread: Optional[threading.Thread] = None
        self._log_fn: Optional[LogFn] = None

        try:
            config = load_config()
            default_backend = config.backend_url
        except Exception:
            default_backend = None
        self.backend_url = default_backend or "http://127.0.0.1:8090"
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
        return self.backend_url

    def login(self, email: str) -> bool:
        return self.auth.login(email=email.strip())

    def logout(self) -> None:
        self.auth.logout()

    def status(self) -> DesktopStatus:
        creds = self.auth._load_credentials()
        daemon_running = bool(self._daemon_proc and self._daemon_proc.poll() is None)
        return DesktopStatus(
            backend_url=self.backend_url,
            is_logged_in=self.auth.is_logged_in(),
            email=creds.email or "",
            daemon_running=daemon_running,
        )

    def start_daemon(self, log_fn: LogFn) -> None:
        if self._daemon_proc and self._daemon_proc.poll() is None:
            raise RuntimeError("Daemon is already running.")
        if not self.auth.is_logged_in():
            raise RuntimeError("Login required before starting daemon.")

        env = {
            "PYTHONPATH": str(self.root_dir / "src"),
            "AI_VOICER_BACKEND_URL": self.backend_url,
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
        for line in proc.stdout:
            if self._log_fn:
                self._log_fn(line.rstrip())
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
            env={**os.environ, "AI_VOICER_BACKEND_URL": self.backend_url},
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
