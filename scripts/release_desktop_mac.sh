#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Release script is macOS-only."
  exit 1
fi

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(git rev-parse --short HEAD)"
fi

./scripts/build_desktop_mac.sh

mkdir -p "dist/releases"
SRC_ZIP="dist/TheoriaDesktop-mac.zip"
OUT_ZIP="dist/releases/TheoriaDesktop-mac-${VERSION}.zip"

cp "$SRC_ZIP" "$OUT_ZIP"

echo "Release artifact:"
echo "  $OUT_ZIP"
