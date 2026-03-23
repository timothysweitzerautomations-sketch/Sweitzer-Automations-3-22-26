#!/usr/bin/env bash
# Create .venv and install Python deps. CrewAI needs Python 3.10+ (macOS /usr/bin/python3 is often 3.9).
# Usage: bash scripts/setup_venv.sh
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
else
  PY="$(command -v python3.11 2>/dev/null || command -v python3.12 2>/dev/null || command -v python3.13 2>/dev/null || true)"
fi
if [[ -z "$PY" ]]; then
  echo "No python3.11+ found. Install one, e.g.: brew install python@3.11" >&2
  exit 1
fi

"$PY" -c 'import sys; assert sys.version_info >= (3, 10), "Need Python 3.10+"'

rm -rf .venv
"$PY" -m venv .venv
# shellcheck source=/dev/null
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
echo ""
echo "OK: activate with: source .venv/bin/activate"
