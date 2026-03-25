#!/usr/bin/env bash
# Copy packaged dashboard assets into chrome_extension/revenue_pulse/ (excludes .py sources).
# Source of truth: revenue_pulse/ — this folder is gitignored; run after clone or edits.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/chrome_extension/revenue_pulse"
mkdir -p "${DEST}"
rsync -a --delete \
  --exclude '__pycache__/' \
  --exclude '*.py' \
  "${ROOT}/revenue_pulse/" "${DEST}/"
echo "Synced ${ROOT}/revenue_pulse/ -> ${DEST}/"
