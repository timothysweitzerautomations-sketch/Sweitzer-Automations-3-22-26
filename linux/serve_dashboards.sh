#!/usr/bin/env bash
# Browser-only: serve revenue_pulse/ and open your default browser (no Tk).
# Good for headless servers or if you have not installed python3-tk.
# Usage: bash linux/serve_dashboards.sh
# Stop with Ctrl+C. Override port: PORT=9888 bash linux/serve_dashboards.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8765}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3." >&2
  exit 1
fi

URL="http://127.0.0.1:${PORT}/"
echo "Serving Revenue Pulse + flip tracker at ${URL}"
echo "Press Ctrl+C to stop."
(
  sleep 1
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser "$URL" || true
  else
    echo "Open this URL in a browser: $URL"
  fi
) &
exec python3 -m http.server "$PORT" --directory "$ROOT/revenue_pulse"
