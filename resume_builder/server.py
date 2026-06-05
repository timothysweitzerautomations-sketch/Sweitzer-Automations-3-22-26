"""Local server for the AI Resume Builder app.

Run:
    python3 -m resume_builder.server

Then open:
    http://127.0.0.1:8090
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from resume_builder.resume_engine import build_ai_prompt, build_fallback_response

APP_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = os.environ.get("RESUME_BUILDER_MODEL") or os.environ.get("OLLAMA_MODEL") or "llama3.1"
DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2).encode("utf-8")


def call_ollama(prompt: str, model: str = DEFAULT_MODEL, timeout: float = 45.0) -> str:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.25},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        DEFAULT_OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return str(payload.get("response", "")).strip()


class ResumeBuilderHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler naming
        if self.path == "/api/health":
            self._send_json({"ok": True, "model": DEFAULT_MODEL})
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler naming
        if self.path != "/api/resume/coach":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object.")
        except (json.JSONDecodeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        response = build_fallback_response(payload)
        if os.environ.get("RESUME_BUILDER_DISABLE_OLLAMA") == "1":
            self._send_json(response)
            return

        prompt = build_ai_prompt(payload, response["analysis"])
        try:
            ai_text = call_ollama(prompt)
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
            response["ollama_error"] = str(exc)
            self._send_json(response)
            return

        if ai_text:
            response["source"] = "ollama"
            response["model"] = DEFAULT_MODEL
            response["ai_response"] = ai_text
        self._send_json(response)

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8090"))
    server = ThreadingHTTPServer((host, port), ResumeBuilderHandler)
    print(f"AI Resume Builder running at http://{host}:{port}")
    print(f"Ollama model: {DEFAULT_MODEL} ({DEFAULT_OLLAMA_URL})")
    print("Set RESUME_BUILDER_DISABLE_OLLAMA=1 for deterministic-only coaching.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()

