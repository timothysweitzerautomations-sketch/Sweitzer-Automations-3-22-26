#!/usr/bin/env bash
# Optional local checks when Android SDK / Xcode are installed.
# Usage: bash scripts/verify_local_platforms.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== 1/3 demo_video_ready (Python + Ollama + pytest + build_crew) ==="
bash "$REPO_ROOT/scripts/demo_video_ready.sh"
echo ""

echo "=== 2/3 Android (assembleDebug) ==="
if [[ -n "${ANDROID_HOME:-}" ]] || [[ -d "${HOME}/Library/Android/sdk" ]]; then
  bash "$REPO_ROOT/scripts/write_android_local_properties.sh"
  if [[ -f android/local.properties ]]; then
    (cd "$REPO_ROOT/android" && ./gradlew assembleDebug --no-daemon)
    echo "Android OK: app/build/outputs/apk/debug/app-debug.apk"
  else
    echo "SKIP: no android/local.properties — install Android Studio or set ANDROID_HOME."
  fi
else
  echo "SKIP: Android SDK not found (ANDROID_HOME or ~/Library/Android/sdk)."
fi
echo ""

echo "=== 3/3 Xcode (macOS build) ==="
if command -v xcodebuild >/dev/null 2>&1 && xcodebuild -version >/dev/null 2>&1; then
  (cd "$REPO_ROOT/apple/SweitzerAutomations" && \
    xcodebuild -project SweitzerAutomations.xcodeproj \
      -scheme SweitzerAutomations \
      -configuration Debug \
      -destination 'platform=macOS' \
      CODE_SIGNING_ALLOWED=NO \
      build)
  echo "Xcode OK."
else
  echo "SKIP: full Xcode required (not only Command Line Tools). Open Xcode once, or rely on GitHub Actions xcode job."
fi

echo ""
echo "Windows .exe: build on a Windows PC (windows_app/build_exe.bat) or use the CI windows_exe job."
