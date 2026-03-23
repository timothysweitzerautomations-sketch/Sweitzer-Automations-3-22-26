#!/usr/bin/env bash
# Sweitzer Automations 3-22-26 — Desktop shortcuts + brand icons + Android SDK hint.
# Run on macOS from anywhere:
#   bash "/path/to/Sweitzer Automations 3-22-26/scripts/setup_platform_apps.sh"
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP="${HOME}/Desktop"
LABEL="Sweitzer Automations 3-22-26"

echo "Repo: $REPO_ROOT"

mkdir -p "$DESKTOP"

# Remove legacy Desktop aliases (old names without the 3-22-26 snapshot)
for old in \
  "Sweitzer Automations - Windows" \
  "Sweitzer Automations - Android" \
  "Sweitzer Automations - Apple"
do
  if [[ -L "$DESKTOP/$old" ]] || [[ -e "$DESKTOP/$old" ]]; then
    rm -f "$DESKTOP/$old"
    echo "Removed old Desktop alias: $old"
  fi
done

ln -sf "$REPO_ROOT" "$DESKTOP/${LABEL} - Project"
ln -sf "$REPO_ROOT/windows" "$DESKTOP/${LABEL} - Windows"
ln -sf "$REPO_ROOT/android" "$DESKTOP/${LABEL} - Android"
ln -sf "$REPO_ROOT/apple" "$DESKTOP/${LABEL} - Apple"
echo "Desktop shortcuts → \"${LABEL} - Project|Windows|Android|Apple\""

bash "$REPO_ROOT/scripts/write_android_local_properties.sh"

if ! python3 -c "import PIL" 2>/dev/null; then
  echo "Installing Pillow for icon generation..."
  python3 -m pip install -q pillow
fi

python3 "$REPO_ROOT/tools/generate_brand_icons.py"

echo ""
echo "Next steps:"
echo "  • Windows: copy the repo to a PC; run windows/BUILD.bat or windows_app/build_exe.bat."
echo "  • Android: install Android Studio + SDK; open the android folder; build or ./gradlew assembleDebug."
echo "  • Apple: install Xcode; open apple/SweitzerAutomations/SweitzerAutomations.xcodeproj; Run."
echo "Done."
