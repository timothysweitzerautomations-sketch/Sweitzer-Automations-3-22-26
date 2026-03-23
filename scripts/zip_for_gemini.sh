#!/usr/bin/env bash
# Create a zip next to the repo folder for uploading to Gemini / Google AI Studio.
# Usage: from anywhere:  bash "/path/to/Sweitzer Automations 3-22-26/scripts/zip_for_gemini.sh"
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(dirname "$REPO_ROOT")"
NAME="$(basename "$REPO_ROOT")"
OUT="${PARENT}/${NAME}-for-Gemini.zip"
cd "$PARENT"
rm -f "$OUT"
# Excludes keep the archive small enough for Gemini uploads; source stays complete.
zip -r "$OUT" "$NAME" \
  -x "${NAME}/.git/*" \
  -x "${NAME}/.venv/*" \
  -x "${NAME}/*/__pycache__/*" \
  -x "${NAME}/*/*/__pycache__/*" \
  -x "${NAME}/.pytest_cache/*" \
  -x "${NAME}/android/.gradle/*" \
  -x "${NAME}/android/build/*" \
  -x "${NAME}/android/app/build/*" \
  -x "${NAME}/dist/*" \
  -x "${NAME}/build/*"
echo "Created: $OUT"
ls -lh "$OUT"
