#!/usr/bin/env bash
# Quick check that Ollama's HTTP API is up (default http://localhost:11434).
# Usage:
#   bash scripts/check_ollama.sh
#   OLLAMA_BASE_URL=http://127.0.0.1:11434 bash scripts/check_ollama.sh
set -euo pipefail

BASE="${OLLAMA_BASE_URL:-http://localhost:11434}"
BASE="${BASE%/}"

if command -v curl >/dev/null 2>&1; then
  curl -sfS --max-time 5 "${BASE}/api/tags" >/dev/null
else
  export OLLAMA_BASE_URL="$BASE"
  python3 - <<'PY'
import json
import os
import urllib.request

base = os.environ["OLLAMA_BASE_URL"].rstrip("/")
with urllib.request.urlopen(base + "/api/tags", timeout=5) as r:
    data = json.loads(r.read().decode())
if not isinstance(data, dict) or "models" not in data:
    raise SystemExit("Unexpected response (not Ollama /api/tags JSON).")
PY
fi

echo "Ollama is reachable at ${BASE}"
