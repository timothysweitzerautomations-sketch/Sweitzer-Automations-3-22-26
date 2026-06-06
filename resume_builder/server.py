"""Static local preview server for the on-device Resume Builder app.

Run:
    python3 -m resume_builder.server

Then open:
    http://127.0.0.1:8090
"""
from __future__ import annotations

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent


class ResumeBuilderHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler naming
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8090"))
    server = ThreadingHTTPServer((host, port), ResumeBuilderHandler)
    print(f"AI Resume Builder static preview running at http://{host}:{port}")
    print("Resume analysis runs on-device in the browser; this server only serves files.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()
