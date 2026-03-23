"""Unit tests for tools/ollama_preflight.py (mocked HTTP)."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from tools.ollama_preflight import check_ollama_reachable


def test_check_ollama_ok():
  payload = json.dumps({"models": []}).encode()
  mock_resp = MagicMock()
  mock_resp.status = 200
  mock_resp.read = lambda: payload
  mock_resp.__enter__ = lambda s: s
  mock_resp.__exit__ = lambda *a: None

  with patch("urllib.request.urlopen", return_value=mock_resp):
    ok, msg = check_ollama_reachable("http://localhost:11434")
  assert ok is True
  assert msg == ""


def test_check_ollama_bad_json():
  mock_resp = MagicMock()
  mock_resp.status = 200
  mock_resp.read = lambda: b"not json"
  mock_resp.__enter__ = lambda s: s
  mock_resp.__exit__ = lambda *a: None

  with patch("urllib.request.urlopen", return_value=mock_resp):
    ok, msg = check_ollama_reachable("http://localhost:11434")
  assert ok is False
  assert "Unexpected response" in msg
