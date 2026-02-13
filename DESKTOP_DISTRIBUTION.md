# Theoria Desktop - Distribution Guide (Sprint 1)

## Goal

Distribute a macOS desktop client that lets users login and run dictation without terminal commands.

## Build artifact locally

```bash
cd /Users/keyvan/Documents/codex/ai-voicer
source .venv/bin/activate
./scripts/build_desktop_mac.sh
```

Output:

- `dist/TheoriaDesktop.app`
- `dist/TheoriaDesktop-mac.zip`

## Installer flow for an external tester

1. Download and unzip `TheoriaDesktop-mac.zip`.
2. Move `TheoriaDesktop.app` to `/Applications`.
3. Open app and set backend URL to your Railway domain.
4. Login with email.
5. Request macOS permissions:
   - Microphone
   - Accessibility
   - Input Monitoring
6. Click "Start daemon".
7. Test hotkey (`F8`) in any text field.
8. Click "Install autostart" to persist daemon at login.

## Runtime diagnostics available in app

- Session/login status
- Daemon running status
- Permission statuses
- Local credential file path
- Local daemon log file path

## Known Sprint 1 limits

- Packaging is macOS-only.
- Auto-update is not implemented yet.
- Authentication flow is still email login v1.

## Next upgrades (Sprint 2+)

- Auth hardening (magic link/OTP)
- Signed installer/notarization
- Auto-update channel
