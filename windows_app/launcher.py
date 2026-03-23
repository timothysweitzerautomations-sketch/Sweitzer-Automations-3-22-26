"""
Desktop launcher: serves revenue_pulse/ on localhost, opens the browser,
and can show sample JSON reports (flip + revenue engines).

Run with Python, or bundle as .exe with PyInstaller (see README_BUILD.md).

Python 3.9+ (stdlib: http, threading, webbrowser, tkinter, json).
"""
from __future__ import annotations

import functools
import http.server
import json
import os
import socketserver
import sys
import threading
import webbrowser


def repo_root() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def ensure_import_path() -> None:
    r = repo_root()
    if r not in sys.path:
        sys.path.insert(0, r)


def static_dir() -> str:
    return os.path.join(repo_root(), "revenue_pulse")


def find_port(start: int = 8765, attempts: int = 30) -> int:
    import socket

    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("Could not find a free port on 127.0.0.1")


class ServerThread:
    def __init__(self, directory: str, port: int) -> None:
        self.directory = directory
        self.port = port
        self._httpd: socketserver.TCPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler,
            directory=self.directory,
        )
        self._httpd = socketserver.TCPServer(("127.0.0.1", self.port), handler)
        self._httpd.allow_reuse_address = True
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None


def flip_sample_json_text() -> str:
    ensure_import_path()
    from pathlib import Path

    from revenue_pulse.flip_engine import DEFAULT_FEE_PERCENT, analyze_flips, detect_flip_columns
    from revenue_pulse.revenue_engine import load_csv

    path = Path(repo_root()) / "revenue_pulse" / "sample_flips.csv"
    fieldnames, rows = load_csv(path)
    cols = detect_flip_columns(fieldnames)
    result = analyze_flips(rows, cols)
    result["_detected_columns"] = cols
    result["_default_fee_percent_if_no_column"] = DEFAULT_FEE_PERCENT
    return json.dumps(result, indent=2)


def revenue_sample_json_text() -> str:
    ensure_import_path()
    from pathlib import Path

    from revenue_pulse.revenue_engine import analyze_rows, detect_columns, load_csv

    path = Path(repo_root()) / "revenue_pulse" / "sample_sales.csv"
    fieldnames, rows = load_csv(path)
    cols = detect_columns(fieldnames)
    result = analyze_rows(rows, cols)
    result["_detected_columns"] = cols
    return json.dumps(result, indent=2)


def show_json_window(parent: object, title: str, body: str) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("720x520")
    win.minsize(480, 320)

    txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10), height=24)
    txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    txt.insert(tk.END, body)
    txt.configure(state=tk.DISABLED)

    bar = ttk.Frame(win, padding=(8, 0, 8, 8))
    bar.pack(fill=tk.X)

    def save_as() -> None:
        path = filedialog.asksaveasfilename(
            parent=win,
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            initialfile=title.lower().replace(" ", "_").replace("(", "").replace(")", "") + ".json",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
        except OSError as e:
            messagebox.showerror("Save failed", str(e), parent=win)
            return
        messagebox.showinfo("Saved", path, parent=win)

    ttk.Button(bar, text="Save as…", command=save_as).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(bar, text="Close", command=win.destroy).pack(side=tk.LEFT)


def main() -> None:
    root = static_dir()
    if not os.path.isdir(root):
        print(f"Missing folder: {root}", file=sys.stderr)
        sys.exit(1)

    port = find_port()
    server = ServerThread(root, port)
    server.start()
    base = f"http://127.0.0.1:{port}"

    try:
        import tkinter as tk
        from tkinter import messagebox
        from tkinter import ttk
    except ImportError:
        webbrowser.open(f"{base}/index.html")
        print(f"Open: {base}/index.html (Tkinter not available for GUI)")
        input("Press Enter to stop the server...")
        server.stop()
        return

    def open_url(path: str) -> None:
        webbrowser.open(f"{base}{path}")

    def on_quit() -> None:
        server.stop()
        win.destroy()

    def open_flip_json() -> None:
        try:
            text = flip_sample_json_text()
        except Exception as e:
            messagebox.showerror("Flip sample", str(e), parent=win)
            return
        show_json_window(win, "Flip sample (JSON)", text)

    def open_revenue_json() -> None:
        try:
            text = revenue_sample_json_text()
        except Exception as e:
            messagebox.showerror("Revenue sample", str(e), parent=win)
            return
        show_json_window(win, "Revenue sample (JSON)", text)

    win = tk.Tk()
    win.title("Sweitzer Automations 3-22-26")
    win.resizable(True, True)
    try:
        win.attributes("-topmost", True)
        win.after(800, lambda: win.attributes("-topmost", False))
    except tk.TclError:
        pass

    pad = {"padx": 14, "pady": 8}
    frm = ttk.Frame(win, padding=16)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        frm,
        text="Revenue Pulse & Flip tracker",
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor=tk.W, **pad)
    ttk.Label(
        frm,
        text=f"Running locally at {base}\nYour data stays in this browser session.",
        wraplength=400,
        justify=tk.LEFT,
    ).pack(anchor=tk.W, padx=14, pady=(0, 8))

    bf = ttk.Frame(frm)
    bf.pack(fill=tk.X, **pad)
    ttk.Button(bf, text="Open Revenue Pulse", command=lambda: open_url("/index.html")).pack(
        fill=tk.X, pady=4
    )
    ttk.Button(bf, text="Open Flip profit tracker", command=lambda: open_url("/flip_tracker.html")).pack(
        fill=tk.X, pady=4
    )

    ttk.Label(frm, text="Sample reports (JSON)", font=("Segoe UI", 10, "bold")).pack(
        anchor=tk.W, padx=14, pady=(12, 4)
    )
    rf = ttk.Frame(frm)
    rf.pack(fill=tk.X, **pad)
    ttk.Button(rf, text="View flip sample (JSON)", command=open_flip_json).pack(fill=tk.X, pady=4)
    ttk.Button(rf, text="View revenue sample (JSON)", command=open_revenue_json).pack(
        fill=tk.X, pady=4
    )

    ttk.Button(frm, text="Quit", command=on_quit).pack(fill=tk.X, pady=(16, 0), padx=14)

    win.protocol("WM_DELETE_WINDOW", on_quit)
    win.mainloop()


if __name__ == "__main__":
    main()
