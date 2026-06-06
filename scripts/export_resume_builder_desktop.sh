#!/usr/bin/env bash
# Export the AI Resume Builder project package to the Mac Desktop.
#
# Usage from the repo root on your Mac:
#   bash scripts/export_resume_builder_desktop.sh
#
# Optional:
#   DEST="$HOME/Desktop/My Resume Builder Export" bash scripts/export_resume_builder_desktop.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${DEST:-$HOME/Desktop/AI Resume Builder Project}"
SCREENSHOT_GLOB="${SCREENSHOT_GLOB:-Screenshot_20260605_2043*_AI Resume Builder.jpg}"
ADB="${ADB:-$HOME/Library/Android/sdk/platform-tools/adb}"

cd "$REPO_ROOT"

mkdir -p "$DEST"

echo "Exporting AI Resume Builder project to:"
echo "  $DEST"
echo ""

echo "Copying Android project..."
rsync -a --delete \
  --exclude "build/" \
  --exclude ".gradle/" \
  --exclude "local.properties" \
  android "$DEST/"

echo "Copying resume builder source..."
rsync -a --delete resume_builder "$DEST/"

echo "Copying docs..."
mkdir -p "$DEST/docs"
cp README.md "$DEST/"
cp docs/google_play_resume_builder.md "$DEST/docs/"

cat > "$DEST/NEXT_STEPS.txt" <<'EOF'
AI Resume Builder - Next Steps

Current app:
- On-device only
- No Android Internet permission
- Resume text is not sent to a server by this app
- Android package ID: com.sweitzer.resumebuilder
- Android app name: AI Resume Builder

Before Google Play submission:
1. Replace launcher icons with resume-builder-specific branding.
2. Pick 3-5 best screenshots from "Google Play Screenshots".
3. Create a privacy policy URL that says resume text stays on device.
4. In Android Studio, build a signed Android App Bundle (.aab).
5. Upload the .aab to Google Play Console internal testing first.
6. Complete the Play Data safety form to match the on-device-only build.

Helpful docs:
- docs/google_play_resume_builder.md
- README.md
EOF

cat > "$DEST/PLAY_LISTING_DRAFT.txt" <<'EOF'
App name:
AI Resume Builder

Short description:
Improve your resume with private, on-device coaching, keyword gaps, and stronger bullet drafts.

Full description starter:
AI Resume Builder helps job seekers tailor a resume to a target role without sending resume text to a server. Paste your current resume and a job description to see a readiness score, missing keywords, clearer bullet drafts, and next-step coaching. The app is designed to avoid inventing employers, degrees, dates, or metrics; it prompts you to add truthful proof where details are missing.

Suggested category:
Productivity or Business

Privacy note:
This on-device MVP does not collect or share resume text.
EOF

echo "Collecting screenshots from connected Android phone, if available..."
mkdir -p "$DEST/Google Play Screenshots"

if [[ -x "$ADB" ]]; then
  mapfile -t SCREENSHOTS < <(
    "$ADB" shell "find /sdcard/Pictures /sdcard/DCIM -type f -name '$SCREENSHOT_GLOB' 2>/dev/null" \
      | tr -d '\r' \
      | sed '/^$/d'
  )

  if (( ${#SCREENSHOTS[@]} > 0 )); then
    for file in "${SCREENSHOTS[@]}"; do
      echo "  Pulling $file"
      "$ADB" pull "$file" "$DEST/Google Play Screenshots/" >/dev/null
    done
  else
    echo "  No matching screenshots found on the phone."
    echo "  Expected pattern: $SCREENSHOT_GLOB"
  fi
else
  echo "  ADB not found at: $ADB"
  echo "  Screenshots were not copied. Install Android SDK Platform-Tools or set ADB=/path/to/adb."
fi

echo ""
echo "Done. Opening export folder..."
open "$DEST" 2>/dev/null || true

