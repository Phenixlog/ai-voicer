#!/bin/bash
set -e

echo "=== AI Voicer - Installation ==="
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Install it:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "  brew install python@3.12"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python $PYTHON_VERSION found."

# Setup directory
INSTALL_DIR="$HOME/.ai-voicer"
APP_DIR="$INSTALL_DIR/app"

mkdir -p "$INSTALL_DIR"

# Copy app files
echo "Installing to $APP_DIR..."
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
fi
mkdir -p "$APP_DIR"

# Copy only what's needed
cp -r src "$APP_DIR/"
cp run_daemon.py "$APP_DIR/"
cp requirements.txt "$APP_DIR/"

# Create venv and install deps
echo "Setting up Python environment..."
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

# Setup .env if not present
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo ""
    echo "Enter your Mistral API key (get one at https://console.mistral.ai):"
    read -r MISTRAL_KEY
    cat > "$INSTALL_DIR/.env" << EOF
MISTRAL_API_KEY=$MISTRAL_KEY

AI_VOICER_HOTKEY=option
AI_VOICER_TRIGGER_MODE=hold
AI_VOICER_LANGUAGE=fr
AI_VOICER_ENABLE_STRUCTURING=true
AI_VOICER_HUD_ENABLED=true
AI_VOICER_DUCK_OUTPUT_AUDIO=true
AI_VOICER_LOG_LEVEL=INFO
EOF
    echo ".env created."
else
    echo ".env already exists, keeping it."
fi

# Symlink .env into app dir
ln -sf "$INSTALL_DIR/.env" "$APP_DIR/.env"

# Create launch script
cat > "$INSTALL_DIR/start.sh" << 'SCRIPT'
#!/bin/bash
cd "$HOME/.ai-voicer/app"
exec .venv/bin/python3 run_daemon.py
SCRIPT
chmod +x "$INSTALL_DIR/start.sh"

# Create LaunchAgent for auto-start on login
PLIST="$HOME/Library/LaunchAgents/com.aivoicer.daemon.plist"
cat > "$PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aivoicer.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/.ai-voicer/app/.venv/bin/python3</string>
        <string>$HOME/.ai-voicer/app/run_daemon.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$HOME/.ai-voicer/app</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.ai-voicer/daemon-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.ai-voicer/daemon-stderr.log</string>
</dict>
</plist>
PLIST

echo ""
echo "=== Installation complete! ==="
echo ""
echo "Start now:          ~/.ai-voicer/start.sh"
echo "Auto-start on login: already configured"
echo "Logs:               ~/.ai-voicer/transcriptions.log"
echo "Config:             ~/.ai-voicer/.env"
echo ""
echo "First time? Grant these permissions in System Settings > Privacy:"
echo "  - Microphone"
echo "  - Accessibility"
echo "  - Input Monitoring"
echo ""
echo "Starting AI Voicer..."
launchctl load "$PLIST" 2>/dev/null || true
launchctl start com.aivoicer.daemon 2>/dev/null || true
echo "Done! Hold [Option] and speak."
