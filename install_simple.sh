#!/bin/bash
# Installation du daemon AI Voicer (version simple)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCH_AGENT_NAME="ai-voicer-simple"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$LAUNCH_AGENT_NAME.plist"
LOG_DIR="$HOME/Library/Logs/ai-voicer"

echo "🎙️  AI Voicer Simple - Installation"
echo "===================================="

# Vérifier le venv
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "❌ Virtualenv non trouvé. Run d'abord:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Vérifier le .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ Fichier .env manquant. Crée-le avec:"
    echo "   MISTRAL_API_KEY=ton_api_key"
    exit 1
fi

# Créer le répertoire de logs
mkdir -p "$LOG_DIR"

# Créer le plist
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LAUNCH_AGENT_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/.venv/bin/python</string>
        <string>$SCRIPT_DIR/run_simple.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/simple_out.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/simple_err.log</string>
</dict>
</plist>
EOF

# Charger le service
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Le daemon tourne maintenant en arrière-plan."
echo "Appuie sur F8 pour parler."
echo ""
echo "Commandes utiles:"
echo "  Voir les logs:   tail -f $LOG_DIR/simple_err.log"
echo "  Arrêter:         launchctl unload $PLIST_PATH"
echo "  Redémarrer:      launchctl unload $PLIST_PATH && launchctl load $PLIST_PATH"
echo ""
