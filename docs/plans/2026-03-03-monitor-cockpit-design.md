# Monitor Cockpit — Design

**Date:** 2026-03-03
**Status:** Approved
**Author:** brainstorming session

---

## Problem

Quand une transcription bug (texte non collé, timeout, mauvais champ actif), l'utilisateur n'a aucun moyen de savoir ce qui s'est passé ni de récupérer le texte perdu. Il faut un "filet de sécurité" — une page toujours accessible pour voir l'activité en temps réel.

---

## Solution

Page `/monitor` dans le frontend React existant. Lecture seule. Polling toutes les 3 secondes sur un nouvel endpoint `/api/monitor/events`.

---

## Architecture

### Backend — 2 changements

**1. Étendre `record_usage`** (`src/ai_voicer/saas/usage.py`)
- Ajouter un champ `transcript_text` (TEXT nullable) à la table `UsageRecord`
- Le daemon passe le texte transcrit lors de l'appel à `record_usage`

**2. Nouveau endpoint** (`src/ai_voicer/saas/routes.py`)
```
GET /api/monitor/events
  → Auth required (JWT)
  → Query params: limit=50, since=<timestamp>
  → Returns: list of {id, timestamp, duration_s, transcript_text, status, error_msg}
```

Les erreurs (paste failure, timeout) sont loggées comme un événement avec `status="error"` et `error_msg`.

### Daemon — 1 changement

Dans `daemon_runtime.py`, `_worker_loop()` :
- Transcription réussie → passer `transcript_text` à `saas_client.transcribe()`
- Saas client → inclure le texte dans le payload `/api/transcribe` → API le store via `record_usage`

### Frontend — 1 nouvelle page

**Route :** `/monitor` (protégée, dans le `Layout` existant)

**Composants :**
- `DaemonStatusCard` — statut (Actif/Inactif), hotkey, mode, uptime estimé, quota bar
- `ActivityFeed` — liste des 50 derniers événements, icône ✅/❌, timestamp, texte tronqué
- `DailyStats` — count transcriptions du jour, durée totale audio, count erreurs
- Badge "● Live" qui clignote + timestamp du dernier refresh

**Data fetching :**
```typescript
// useMonitorEvents.ts
const { data, isLoading } = useQuery({
  queryKey: ['monitor-events'],
  queryFn: () => api.get('/api/monitor/events'),
  refetchInterval: 3000,
});
```

---

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│  DAEMON STATUS                                       │
│  ● Actif  |  Hotkey: F8  |  Mode: hold  |  ~uptime  │
│  ████████░░░░  42 min / 300 min utilisés (14%)       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  ACTIVITÉ RÉCENTE               [● Live - 3s refresh]│
│  14:32:01  ✅  "Bonjour, pouvez-vous confirmer..."  │
│  14:28:44  ✅  "Note pour la réunion de demain..."   │
│  14:15:12  ❌  Erreur : timeout paste               │
│  14:10:03  ✅  "Je voulais te dire que le projet..." │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  STATS DU JOUR                                       │
│  12 transcriptions  |  4 min 22s audio  |  1 erreur  │
└─────────────────────────────────────────────────────┘
```

---

## Scope (YAGNI)

**In scope :**
- Affichage de l'historique des 50 derniers événements
- Statut daemon (via le dernier événement — si > 5 min, considéré inactif)
- Stats journalières
- Auto-refresh 3s

**Out of scope (pour l'instant) :**
- Contrôle du daemon (start/stop/restart)
- Copy button par transcript
- Filtres / recherche
- Notifications push / alertes
- Export CSV

---

## Files to touch

| Fichier | Changement |
|---|---|
| `src/ai_voicer/saas/models.py` | Ajouter `transcript_text` à `UsageRecord` + migration |
| `src/ai_voicer/saas/usage.py` | Accepter `transcript_text` dans `record_usage()` |
| `src/ai_voicer/saas/routes.py` | Ajouter `GET /api/monitor/events` |
| `src/ai_voicer/saas_client.py` | Passer le texte transcrit dans le payload |
| `src/ai_voicer/daemon_runtime.py` | Passer le transcript à `saas_client.transcribe()` |
| `frontend/src/hooks/useMonitorEvents.ts` | Hook React Query pour poll `/api/monitor/events` |
| `frontend/src/pages/Monitor.tsx` | Page principale |
| `frontend/src/components/monitor/` | DaemonStatusCard, ActivityFeed, DailyStats |
| `frontend/src/App.tsx` | Ajouter route `/monitor` |
| `frontend/src/components/layout/Sidebar.tsx` | Ajouter lien Monitor |
