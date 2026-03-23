#!/usr/bin/env bash
# Point this repo at GitHub and push main (HTTPS). You will be prompted for credentials:
#   Username = your GitHub username
#   Password = a Personal Access Token (classic) with "repo" AND "workflow" scopes if this
#   repo contains .github/workflows/*.yml — NOT your GitHub password.
# Usage:
#   bash scripts/setup_github_remote.sh https://github.com/YOUR_USER/YOUR_REPO.git
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Usage: bash scripts/setup_github_remote.sh https://github.com/USER/REPO.git" >&2
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Updating existing origin -> $URL"
  git remote set-url origin "$URL"
else
  echo "Adding origin -> $URL"
  git remote add origin "$URL"
fi

git branch -M main
echo "Pushing main (enter GitHub username + PAT when prompted)..."
git push -u origin main
echo "Done."
