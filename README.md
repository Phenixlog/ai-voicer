# AI Voicer (SaaS-first + daemon client)

Architecture orientee SaaS:

- **API centrale** FastAPI (`/v1/transcribe`) qui fait transcription + structuration.
- **Client daemon local** macOS (push-to-talk) qui capture l'audio, appelle l'API, puis colle le texte dans le champ actif.

Ainsi, la logique metier existe une seule fois (backend), et le daemon est un client mince.

## 1) Prerequisites

- macOS (pour le daemon client)
- Python 3.10+
- Mistral API key

## 2) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure `.env`:

- `MISTRAL_API_KEY=...`
- `AI_VOICER_BACKEND_URL=http://127.0.0.1:8090` (local dev)
- `AI_VOICER_HOTKEY=f8`
- Optionnel: `AI_VOICER_API_AUTH_TOKEN=...` + `AI_VOICER_BACKEND_API_KEY=...`
- `AI_VOICER_DUCK_OUTPUT_AUDIO=true` coupe le son systeme pendant l'ecoute puis le restaure

## 3) Lancer l'API (coeur SaaS)

```bash
source .venv/bin/activate
python run_api.py
```

Health check:

```bash
curl http://127.0.0.1:8090/health
```

## 4) Lancer le daemon client en local

Premier run manuel (pour accorder les permissions macOS):

```bash
source .venv/bin/activate
python run_daemon.py
```

Permissions a accepter:

- Microphone
- Accessibility (capture touche + Cmd+V)
- Automation (System Events)

## 5) Installer le daemon en background (launchd)

```bash
chmod +x install_launch_agent.sh uninstall_launch_agent.sh
./install_launch_agent.sh
```

Logs:

```bash
tail -f "$HOME/Library/Logs/ai-voicer/out.log"
tail -f "$HOME/Library/Logs/ai-voicer/err.log"
```

Uninstall:

```bash
./uninstall_launch_agent.sh
```

Optionnel: lancer aussi l'API locale en launchd:

```bash
chmod +x install_api_launch_agent.sh uninstall_api_launch_agent.sh
./install_api_launch_agent.sh
```

Pour retirer l'API launchd:

```bash
./uninstall_api_launch_agent.sh
```

## 6) Usage

1. Focus un champ texte.
2. Maintiens la hotkey.
3. Parle.
4. Relache.
5. Le daemon envoie l'audio a l'API, recupere le texte structure, puis colle.

## Endpoints API

- `GET /health`
- `POST /v1/transcribe` (multipart `audio`, query `structured=true|false`)
  - Reponse: `{ "transcript": "...", "text": "..." }`
  - Header optionnel: `x-api-key` (si `AI_VOICER_API_AUTH_TOKEN` configure)

Exemple:

```bash
curl -X POST "http://127.0.0.1:8090/v1/transcribe?structured=true" \
  -H "x-api-key: YOUR_TOKEN_IF_ENABLED" \
  -F "audio=@/path/to/audio.wav"
```
