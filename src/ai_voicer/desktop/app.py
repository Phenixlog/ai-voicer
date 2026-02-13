"""Tkinter desktop app for controlling Theoria local daemon."""

from __future__ import annotations

import queue
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

from .controller import DesktopAppController


class DesktopControlApp:
    def __init__(self, root: tk.Tk, project_root: Path):
        self.root = root
        self.controller = DesktopAppController(project_root)
        self.log_queue: queue.Queue[str] = queue.Queue()

        self.root.title("Theoria Desktop")
        self.root.geometry("860x620")
        self.root.minsize(760, 540)

        self.backend_var = tk.StringVar(value=self.controller.backend_url)
        self.email_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Session: not logged in")
        self.daemon_var = tk.StringVar(value="Daemon: stopped")

        self._build_ui()
        self._refresh_status_once()
        self.root.after(150, self._flush_logs)
        self.root.after(1000, self._tick_status_refresh)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        main = tk.Frame(self.root, padx=12, pady=12)
        main.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(main, text="Theoria Desktop Control Center", font=("Helvetica", 16, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(
            main,
            text="Connect account, start daemon, and manage autostart without terminal.",
            fg="#555",
        )
        subtitle.pack(anchor="w", pady=(2, 12))

        cfg = tk.LabelFrame(main, text="Connection", padx=10, pady=10)
        cfg.pack(fill=tk.X)

        tk.Label(cfg, text="Backend URL").grid(row=0, column=0, sticky="w")
        tk.Entry(cfg, textvariable=self.backend_var, width=64).grid(row=0, column=1, sticky="we", padx=(8, 8))
        tk.Button(cfg, text="Apply URL", command=self._apply_backend_url).grid(row=0, column=2, sticky="e")

        tk.Label(cfg, text="Email").grid(row=1, column=0, sticky="w", pady=(8, 0))
        tk.Entry(cfg, textvariable=self.email_var, width=64).grid(row=1, column=1, sticky="we", padx=(8, 8), pady=(8, 0))
        auth_buttons = tk.Frame(cfg)
        auth_buttons.grid(row=1, column=2, sticky="e", pady=(8, 0))
        tk.Button(auth_buttons, text="Login", command=self._login).pack(side=tk.LEFT)
        tk.Button(auth_buttons, text="Logout", command=self._logout).pack(side=tk.LEFT, padx=(6, 0))
        cfg.columnconfigure(1, weight=1)

        status_frame = tk.Frame(main)
        status_frame.pack(fill=tk.X, pady=(10, 8))
        tk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(fill=tk.X)
        tk.Label(status_frame, textvariable=self.daemon_var, anchor="w").pack(fill=tk.X, pady=(4, 0))

        daemon_box = tk.LabelFrame(main, text="Daemon Controls", padx=10, pady=10)
        daemon_box.pack(fill=tk.X)
        tk.Button(daemon_box, text="Start daemon", command=self._start_daemon).pack(side=tk.LEFT)
        tk.Button(daemon_box, text="Stop daemon", command=self._stop_daemon).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(daemon_box, text="Install autostart", command=self._install_autostart).pack(
            side=tk.LEFT, padx=(18, 0)
        )
        tk.Button(daemon_box, text="Remove autostart", command=self._uninstall_autostart).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        tk.Button(daemon_box, text="Refresh status", command=self._refresh_status_once).pack(side=tk.RIGHT)

        logs = tk.LabelFrame(main, text="Runtime Logs", padx=10, pady=10)
        logs.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        self.log_widget = scrolledtext.ScrolledText(logs, height=16, state=tk.DISABLED, wrap=tk.WORD)
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def _append_log(self, line: str) -> None:
        self.log_queue.put(line)

    def _flush_logs(self) -> None:
        updated = False
        while not self.log_queue.empty():
            line = self.log_queue.get_nowait()
            self.log_widget.configure(state=tk.NORMAL)
            self.log_widget.insert(tk.END, line + "\n")
            self.log_widget.see(tk.END)
            self.log_widget.configure(state=tk.DISABLED)
            updated = True
        if updated:
            self.log_widget.update_idletasks()
        self.root.after(150, self._flush_logs)

    def _apply_backend_url(self) -> None:
        try:
            normalized = self.controller.set_backend_url(self.backend_var.get())
            self.backend_var.set(normalized)
            self._append_log(f"Backend URL applied: {normalized}")
            self._refresh_status_once()
        except Exception as exc:
            messagebox.showerror("Backend URL", str(exc))

    def _login(self) -> None:
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("Login", "Email is required.")
            return
        self._apply_backend_url()
        success = self.controller.login(email)
        if success:
            self._append_log(f"Login successful: {email}")
            self._refresh_status_once()
            return
        messagebox.showerror("Login", "Login failed. Check your email and backend URL.")

    def _logout(self) -> None:
        self.controller.logout()
        self._append_log("Logged out.")
        self._refresh_status_once()

    def _start_daemon(self) -> None:
        self._apply_backend_url()
        try:
            self.controller.start_daemon(self._append_log)
            self._append_log("Daemon start requested.")
            self._refresh_status_once()
        except Exception as exc:
            messagebox.showerror("Start daemon", str(exc))

    def _stop_daemon(self) -> None:
        self.controller.stop_daemon()
        self._append_log("Daemon stop requested.")
        self._refresh_status_once()

    def _install_autostart(self) -> None:
        self._apply_backend_url()
        try:
            out = self.controller.install_autostart()
            self._append_log("Autostart installed.")
            if out:
                self._append_log(out)
        except Exception as exc:
            messagebox.showerror("Install autostart", str(exc))

    def _uninstall_autostart(self) -> None:
        try:
            out = self.controller.uninstall_autostart()
            self._append_log("Autostart removed.")
            if out:
                self._append_log(out)
        except Exception as exc:
            messagebox.showerror("Remove autostart", str(exc))

    def _refresh_status_once(self) -> None:
        status = self.controller.status()
        if status.is_logged_in:
            self.status_var.set(f"Session: logged in as {status.email}")
        else:
            self.status_var.set("Session: not logged in")
        self.daemon_var.set("Daemon: running" if status.daemon_running else "Daemon: stopped")

    def _tick_status_refresh(self) -> None:
        self._refresh_status_once()
        self.root.after(1000, self._tick_status_refresh)

    def _on_close(self) -> None:
        try:
            self.controller.stop_daemon()
        except Exception:
            pass
        self.root.destroy()


def launch_desktop_app(project_root: Path) -> None:
    root = tk.Tk()
    DesktopControlApp(root, project_root=project_root)
    root.mainloop()
