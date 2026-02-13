#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This build script is macOS-only."
  exit 1
fi

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Virtualenv not found. Run ./setup_saas.sh first."
  exit 1
fi

PYTHON=".venv/bin/python"

echo "Installing desktop build tools..."
"$PYTHON" -m pip install --upgrade pyinstaller >/dev/null

echo "Building Theoria Desktop app..."
"$PYTHON" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "TheoriaDesktop" \
  --paths "src" \
  run_desktop_app.py

APP_PATH="$ROOT_DIR/dist/TheoriaDesktop.app"
ZIP_PATH="$ROOT_DIR/dist/TheoriaDesktop-mac.zip"

if [[ ! -d "$APP_PATH" ]]; then
  echo "Build failed: app bundle not found."
  exit 1
fi

echo "Packaging zip artifact..."
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

echo "Build completed."
echo "App: $APP_PATH"
echo "Zip: $ZIP_PATH"
