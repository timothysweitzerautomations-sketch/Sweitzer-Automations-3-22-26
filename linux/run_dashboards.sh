#!/usr/bin/env bash
# Sweitzer Automations — open the same desktop launcher as Windows (Tk + local server).
# Requires: Python 3.9+ and Tk — on Debian/Ubuntu: sudo apt install python3-tk
# Usage: bash linux/run_dashboards.sh   OR   ./linux/run_dashboards.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python 3, then see LINUX.md." >&2
  exit 1
fi

if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "Tkinter not available (need python3-tk for the graphical launcher)." >&2
  echo "  Debian/Ubuntu: sudo apt install python3-tk" >&2
  echo "  Fedora: sudo dnf install python3-tkinter" >&2
  echo "Or run the browser-only server: bash linux/serve_dashboards.sh" >&2
  exit 1
fi

exec python3 "$ROOT/windows_app/launcher.py"
