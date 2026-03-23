#!/usr/bin/env bash
# Write android/local.properties with sdk.dir when an SDK directory is found.
# Checks: ANDROID_HOME, ANDROID_SDK_ROOT, ~/Library/Android/sdk (macOS), ~/Android/Sdk (common Linux).
# Usage: bash scripts/write_android_local_properties.sh
# Exit 0 always; prints whether the file was written.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROP="$REPO_ROOT/android/local.properties"

resolve_sdk() {
  local d
  for d in "${ANDROID_HOME:-}" "${ANDROID_SDK_ROOT:-}" "${HOME}/Library/Android/sdk" "${HOME}/Android/Sdk"; do
    if [[ -n "$d" && -d "$d" ]]; then
      printf '%s' "$d"
      return 0
    fi
  done
  return 1
}

if SDK="$(resolve_sdk)"; then
  printf 'sdk.dir=%s\n' "$SDK" > "$PROP"
  echo "Wrote android/local.properties (sdk.dir=$SDK)."
else
  echo "No Android SDK directory found (checked ANDROID_HOME, ANDROID_SDK_ROOT, ~/Library/Android/sdk, ~/Android/Sdk)."
  echo "Install Android Studio or set ANDROID_HOME, then re-run: bash scripts/write_android_local_properties.sh"
  echo "Or copy android/local.properties.example → android/local.properties and edit sdk.dir."
fi
