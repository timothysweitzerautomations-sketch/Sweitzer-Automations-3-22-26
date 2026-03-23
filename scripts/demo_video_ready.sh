#!/usr/bin/env bash
# Pre-recording check: Ollama reachable, tests pass, crew builds.
# Usage: bash scripts/demo_video_ready.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Sweitzer Automations — demo video readiness ==="
echo "Repo: $REPO_ROOT"
echo ""

if [[ ! -d .venv ]]; then
  echo "FAIL: no .venv — run: bash scripts/setup_venv.sh" >&2
  exit 1
fi
# shellcheck source=/dev/null
. .venv/bin/activate

echo "1/3 Ollama (scripts/check_ollama.sh) ..."
bash "$REPO_ROOT/scripts/check_ollama.sh"
echo ""

echo "2/3 pytest ..."
pytest tests/ -q
echo ""

echo "3/3 build_crew() ..."
python -c "from main import build_crew; c = build_crew(); print('  build_crew OK:', len(c.tasks), 'tasks')"
echo ""

echo "All checks passed. Safe to record (browser server + main.py are separate)."
echo "See: Desktop/Sweitzer_Demo_Video_Runbook.txt and docs/video/VIDEO_PREP.txt"
