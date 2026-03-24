#!/usr/bin/env bash
# Quick DNS check for sweitzerautomations.com (Netlify / registrar debugging).
# Requires: dig (macOS: preinstalled)
set -euo pipefail

DOMAIN="${SWEITZER_DOMAIN:-sweitzerautomations.com}"

if ! command -v dig >/dev/null 2>&1; then
  echo "dig not found. On macOS, install Xcode Command Line Tools or use a browser:"
  echo "  https://dnschecker.org/#NS/${DOMAIN}"
  exit 1
fi

echo "=== NS (nameservers) for ${DOMAIN} ==="
dig NS "${DOMAIN}" +noall +answer +ttlunits 2>/dev/null || dig NS "${DOMAIN}" +short

echo ""
echo "=== A (apex) for ${DOMAIN} ==="
dig A "${DOMAIN}" +noall +answer +ttlunits 2>/dev/null || dig A "${DOMAIN}" +short

echo ""
echo "=== A for www.${DOMAIN} ==="
dig A "www.${DOMAIN}" +noall +answer +ttlunits 2>/dev/null || dig A "www.${DOMAIN}" +short

echo ""
echo "Online: https://dnschecker.org/#NS/${DOMAIN}"
