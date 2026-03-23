"""Connectivity check for Ollama before running main.py (stdlib only)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def normalize_base_url(url: str) -> str:
  u = (url or "").strip()
  return u.rstrip("/")


def check_ollama_reachable(base_url: str, timeout: float = 5.0) -> tuple[bool, str]:
  """
  Returns (ok, message). Message is empty when ok; otherwise a short error for humans.
  """
  base = normalize_base_url(base_url)
  if not base:
    return False, "OLLAMA_BASE_URL is empty."
  url = f"{base}/api/tags"
  try:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
      if resp.status != 200:
        return False, f"Ollama at {base_url} returned HTTP {resp.status}."
      body = resp.read()
  except urllib.error.HTTPError as e:
    return False, f"Ollama at {base_url} returned HTTP {e.code}: {e.reason}."
  except urllib.error.URLError as e:
    return False, f"Cannot reach Ollama at {base_url} ({e.reason})."
  except TimeoutError:
    return False, f"Timed out connecting to Ollama at {base_url}."
  except OSError as e:
    return False, f"Cannot reach Ollama at {base_url} ({e})."

  # Optional: ensure JSON so we didn't hit a random server on :11434
  try:
    data = json.loads(body.decode())
    if not isinstance(data, dict) or "models" not in data:
      return False, f"Unexpected response from {url} (not Ollama /api/tags JSON)."
  except (json.JSONDecodeError, UnicodeDecodeError):
    return False, f"Unexpected response from {url} (not JSON)."

  return True, ""


def require_ollama_or_exit(base_url: str, timeout: float = 5.0) -> None:
  ok, msg = check_ollama_reachable(base_url, timeout=timeout)
  if ok:
    return
  print(msg, file=sys.stderr)
  print(
    "Hint: start Ollama (menu app or `ollama serve`), then `ollama pull llama3` "
    "or match OLLAMA_MODEL to `ollama list`.",
    file=sys.stderr,
  )
  print("To skip this check: SKIP_OLLAMA_CHECK=1 python main.py", file=sys.stderr)
  raise SystemExit(1)
