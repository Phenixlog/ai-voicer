#!/bin/bash
# Théoria launcher - uses correct Python from venv

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Virtual environment not found. Run: ./setup_saas.sh"
    exit 1
fi

# Get command
COMMAND=${1:-"saas-daemon"}
shift || true

case $COMMAND in
    saas-api|sa)
        echo "⚙️  Starting Théoria SaaS API..."
        exec "$PYTHON" "$SCRIPT_DIR/run_saas_api.py" "$@"
        ;;
    saas-daemon|sd)
        echo "🎙️  Starting Théoria SaaS Daemon..."
        exec "$PYTHON" "$SCRIPT_DIR/run_saas_daemon.py" "$@"
        ;;
    desktop|ui)
        echo "🖥️  Starting Théoria Desktop App..."
        exec "$PYTHON" "$SCRIPT_DIR/run_desktop_app.py" "$@"
        ;;
    login|l)
        echo "🔑 Login to Théoria SaaS..."
        exec "$PYTHON" "$SCRIPT_DIR/run_saas_daemon.py" login "$@"
        ;;
    status|s)
        echo "📊 Théoria Status..."
        exec "$PYTHON" "$SCRIPT_DIR/run_saas_daemon.py" status "$@"
        ;;
    test)
        echo "🧪 Running tests..."
        exec "$PYTHON" -m pytest "$SCRIPT_DIR/src/ai_voicer/saas/" -v 2>/dev/null || echo "No tests yet"
        ;;
    --help|-h|help)
        cat << 'EOF'
Théoria Launcher

Usage: ./run.sh <command> [args]

Commands:
  saas-api, sa    Run SaaS API (auth/billing/usage)
  saas-daemon, sd Run SaaS daemon (needs login)
  desktop, ui     Run desktop control app (no terminal workflow)
  login, l        Login to SaaS (./run.sh login email@example.com)
  status, s       Show SaaS status
  test            Run tests
  help            Show this help

Examples:
  ./run.sh saas-api            # Start SaaS API server
  ./run.sh login user@test.com # Login
  ./run.sh sd run              # Run SaaS daemon
  ./run.sh desktop             # Open desktop control app
EOF
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run './run.sh help' for usage"
        exit 1
        ;;
esac
