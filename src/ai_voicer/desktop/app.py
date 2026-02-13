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
        self.hotkey_var = tk.StringVar(value=self.controller.hotkey)
        self.trigger_mode_var = tk.StringVar(value=self.controller.trigger_mode)
        self.status_var = tk.StringVar(value="Session: not logged in")
        self.daemon_var = tk.StringVar(value="Daemon: stopped")
        self.mic_perm_var = tk.StringVar(value="Microphone: unknown")
        self.ax_perm_var = tk.StringVar(value="Accessibility: unknown")
        self.input_perm_var = tk.StringVar(value="Input monitoring: unknown")
        self.diagnostics_var = tk.StringVar(value="Diagnostics: loading...")

        self._build_ui()
        self.root.after(120, self._refresh_status_once)
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

        tk.Label(cfg, text="Hotkey").grid(row=2, column=0, sticky="w", pady=(8, 0))
        tk.Entry(cfg, textvariable=self.hotkey_var, width=24).grid(row=2, column=1, sticky="w", padx=(8, 8), pady=(8, 0))
        settings_buttons = tk.Frame(cfg)
        settings_buttons.grid(row=2, column=2, sticky="e", pady=(8, 0))
        tk.OptionMenu(settings_buttons, self.trigger_mode_var, "hold", "toggle").pack(side=tk.LEFT)
        tk.Button(settings_buttons, text="Save keys", command=self._save_hotkey_settings).pack(side=tk.LEFT, padx=(6, 0))
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
        tk.Button(daemon_box, text="Reset daemon", command=self._reset_daemon).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(daemon_box, text="Refresh status", command=self._refresh_status_once).pack(side=tk.RIGHT)

        onboarding = tk.LabelFrame(main, text="Permissions Onboarding (macOS)", padx=10, pady=10)
        onboarding.pack(fill=tk.X, pady=(12, 0))
        tk.Label(onboarding, textvariable=self.mic_perm_var, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Button(
            onboarding,
            text="Request microphone",
            command=lambda: self._request_permission("microphone"),
        ).grid(row=0, column=1, sticky="e")
        tk.Button(
            onboarding,
            text="Open settings",
            command=lambda: self._open_permission_settings("Microphone"),
        ).grid(row=0, column=2, sticky="e", padx=(6, 0))

        tk.Label(onboarding, textvariable=self.ax_perm_var, anchor="w").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tk.Button(
            onboarding,
            text="Request accessibility",
            command=lambda: self._request_permission("accessibility"),
        ).grid(row=1, column=1, sticky="e", pady=(6, 0))
        tk.Button(
            onboarding,
            text="Open settings",
            command=lambda: self._open_permission_settings("Accessibility"),
        ).grid(row=1, column=2, sticky="e", padx=(6, 0), pady=(6, 0))

        tk.Label(onboarding, textvariable=self.input_perm_var, anchor="w").grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Button(
            onboarding,
            text="Request input monitoring",
            command=lambda: self._request_permission("input_monitoring"),
        ).grid(row=2, column=1, sticky="e", pady=(6, 0))
        tk.Button(
            onboarding,
            text="Open settings",
            command=lambda: self._open_permission_settings("ListenEvent"),
        ).grid(row=2, column=2, sticky="e", padx=(6, 0), pady=(6, 0))
        onboarding.columnconfigure(0, weight=1)

        diagnostics = tk.LabelFrame(main, text="Diagnostics", padx=10, pady=10)
        diagnostics.pack(fill=tk.X, pady=(12, 0))
        tk.Label(diagnostics, textvariable=self.diagnostics_var, justify=tk.LEFT, anchor="w").pack(fill=tk.X)

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

    def _save_hotkey_settings(self) -> None:
        try:
            hotkey, mode = self.controller.set_local_settings(
                self.hotkey_var.get(),
                self.trigger_mode_var.get(),
            )
            self.hotkey_var.set(hotkey)
            self.trigger_mode_var.set(mode)
            self._append_log(f"Local daemon settings saved: hotkey={hotkey}, mode={mode}")
            self._refresh_status_once()
        except Exception as exc:
            messagebox.showerror("Settings", str(exc))

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

    def _reset_daemon(self) -> None:
        try:
            out = self.controller.reset_daemon_instances()
            self._append_log(out)
            self._refresh_status_once()
        except Exception as exc:
            messagebox.showerror("Reset daemon", str(exc))

    def _refresh_status_once(self) -> None:
        status = self.controller.status()
        if status.is_logged_in:
            self.status_var.set(f"Session: logged in as {status.email}")
        else:
            self.status_var.set("Session: not logged in")
        autostart = "enabled" if self.controller.is_autostart_installed() else "disabled"
        daemon_state = "running" if status.daemon_running else "stopped"
        self.daemon_var.set(f"Daemon: {daemon_state} | Autostart: {autostart}")
        self._refresh_permissions()
        self._refresh_diagnostics()

    def _tick_status_refresh(self) -> None:
        self._refresh_status_once()
        self.root.after(1000, self._tick_status_refresh)

    def _refresh_permissions(self) -> None:
        state = self.controller.get_permission_state()
        self.mic_perm_var.set(f"Microphone: {state.microphone}")
        self.ax_perm_var.set(f"Accessibility: {state.accessibility}")
        self.input_perm_var.set(f"Input monitoring: {state.input_monitoring}")

    def _request_permission(self, name: str) -> None:
        state = self.controller.request_permission(name)
        self.mic_perm_var.set(f"Microphone: {state.microphone}")
        self.ax_perm_var.set(f"Accessibility: {state.accessibility}")
        self.input_perm_var.set(f"Input monitoring: {state.input_monitoring}")
        self._append_log(f"Permission request attempted: {name}")

    def _open_permission_settings(self, section: str) -> None:
        self.controller.open_permission_settings(section)
        self._append_log(f"Opened macOS settings: Privacy_{section}")

    def _refresh_diagnostics(self) -> None:
        d = self.controller.diagnostics()
        auth = "logged_in" if d.is_logged_in else "logged_out"
        self.diagnostics_var.set(
            (
                f"Auth={auth} | Backend={d.backend_url}\n"
                f"Hotkey={d.hotkey} | Trigger mode={d.trigger_mode}\n"
                f"Autostart={'yes' if d.autostart_installed else 'no'} | "
                f"Credentials={d.credentials_file}\n"
                f"Log file={d.daemon_log_file}"
            )
        )

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
