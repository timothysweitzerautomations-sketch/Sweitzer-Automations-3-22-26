#!/usr/bin/env bash
# Copy packaged dashboard assets into chrome_extension/revenue_pulse/ (excludes .py sources).
# Source of truth: revenue_pulse/ — this folder is gitignored; run after clone or edits.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/chrome_extension/revenue_pulse"
mkdir -p "${DEST}"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude '__pycache__/' \
    --exclude '*.py' \
    "${ROOT}/revenue_pulse/" "${DEST}/"
else
  ROOT="${ROOT}" DEST="${DEST}" python3 - <<'PY'
import os
import shutil
from pathlib import Path

src = Path(os.environ["ROOT"]) / "revenue_pulse"
dest = Path(os.environ["DEST"])
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True, exist_ok=True)
for path in src.rglob("*"):
    rel = path.relative_to(src)
    if "__pycache__" in rel.parts or path.suffix == ".py":
        continue
    target = dest / rel
    if path.is_dir():
        target.mkdir(parents=True, exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
PY
fi
echo "Synced ${ROOT}/revenue_pulse/ -> ${DEST}/"
