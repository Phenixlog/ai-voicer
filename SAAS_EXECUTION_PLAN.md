# Theoria - Plan d'Execution SaaS (B2C)

## 1) But du document

Ce document est le playbook d'execution pour transformer Theoria en SaaS commercialisable.

Il sert a:

- prioriser clairement quoi construire,
- definir l'ordre d'execution,
- fixer les criteres de validation,
- suivre l'avancement sans ambiguite.

## 2) Objectif 90 jours

En 90 jours, lancer une **private beta payante** avec:

- application desktop stable,
- API SaaS securisee,
- auth utilisateur,
- quotas et billing Stripe,
- onboarding et support minimal,
- pilotage metriques.

Definition de succes a J+90:

- 50 beta users actifs,
- 10 clients payants,
- taux de succes transcription > 96%,
- latence P95 < 8s sur clips courts,
- MRR initial valide.

## 3) Scope execute vs non-execute

## Execute (v1)

- Client desktop macOS (hotkey, HUD, dictation, paste).
- API de transcription/structuration.
- Auth email magic link + Google OAuth.
- Billing Stripe (free/pro/power) + webhooks.
- Quotas usage (minutes/mois) et limitation par plan.
- Dashboard web minimal (compte, plan, usage, facturation).
- Observabilite de base (logs structures, erreurs, latency).

## Non-execute (post-v1)

- Equipes/multi-workspaces.
- API publique externe.
- Mobile natif.
- Collaboration et partage de snippets.

## 4) Architecture cible (implementation)

## 4.1 Components

- `desktop-client`:
  - capture micro,
  - hotkey globale,
  - HUD et paste,
  - auth token local,
  - appels API SaaS.
- `api-core`:
  - authN/authZ,
  - endpoint `/v1/transcribe`,
  - orchestration provider IA,
  - quotas et policy.
- `billing-service`:
  - sync Stripe customer/subscription,
  - gestion entitlements.
- `web-app`:
  - onboarding/login,
  - settings utilisateur,
  - plans/pricing,
  - historique et usage.
- `data-store`:
  - users, sessions, plans, subscriptions, usage_events.
- `observability`:
  - logs centralises,
  - dashboards latency/error/cost.

## 4.2 Decisions techniques conseillees

- Backend: FastAPI (continuite avec l'existant).
- DB: Postgres.
- Cache/queues: Redis (si besoin workers).
- Front web: Next.js.
- Auth: Clerk ou Supabase Auth (aller vite) ou auth maison minimale.
- Billing: Stripe Billing + Stripe Customer Portal.
- Packaging desktop: rester script + launchd en beta, packager plus tard.

## 5) Modele de donnees minimal (v1)

## 5.1 Tables

- `users`
  - `id`, `email`, `name`, `created_at`, `locale`, `status`
- `user_settings`
  - `user_id`, `hotkey`, `trigger_mode`, `language`, `style_mode`, `context_bias`, `hud_enabled`
- `plans`
  - `id`, `code` (`free`, `pro`, `power`), `monthly_minutes`, `price_cents`, `active`
- `subscriptions`
  - `id`, `user_id`, `plan_id`, `stripe_customer_id`, `stripe_subscription_id`, `status`, `period_start`, `period_end`
- `usage_events`
  - `id`, `user_id`, `request_id`, `audio_seconds`, `provider`, `model`, `success`, `latency_ms`, `cost_estimate`, `created_at`
- `transcription_events` (optionnel en v1 si retention faible)
  - `id`, `user_id`, `request_id`, `status`, `error_code`, `created_at`

## 5.2 Index critiques

- `usage_events(user_id, created_at desc)`
- `subscriptions(user_id, status)`
- `users(email unique)`
- `usage_events(request_id unique)`

## 6) API contract (v1)

## 6.1 Auth

- `POST /v1/auth/login` (magic link / OAuth callback)
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`

## 6.2 Core

- `POST /v1/transcribe`
  - input: multipart audio + options
  - output: `{ transcript, text, request_id, latency_ms }`
  - erreurs:
    - `401` auth invalide,
    - `402/403` plan limite,
    - `429` rate limit,
    - `502` provider indisponible.

## 6.3 Billing and usage

- `GET /v1/me`
- `GET /v1/usage/current-period`
- `GET /v1/plans`
- `POST /v1/billing/checkout-session`
- `POST /v1/billing/portal-session`
- `POST /v1/stripe/webhook`

## 7) Backlog priorise (par epic)

## Epic A - Auth et compte

- A1: login email + session JWT
- A2: OAuth Google
- A3: endpoint `me` + settings utilisateur
- A4: middleware auth sur endpoints prives

Done criteria:

- login/logout fonctionne end-to-end,
- token refresh stable,
- client desktop peut appeler `/v1/transcribe` avec user auth.

## Epic B - Billing et plans

- B1: products/prices Stripe
- B2: checkout session
- B3: webhook sync subscription state
- B4: customer portal
- B5: entitlement resolver (plan actif utilisateur)

Done criteria:

- upgrade/downgrade plan reflechi en DB en < 1 min,
- blocage usage quand limite atteinte.

## Epic C - Usage metering et quotas

- C1: calcul audio_seconds par requete
- C2: ecriture `usage_events`
- C3: agrégation mensualisee par user
- C4: policy quota avant appel provider

Done criteria:

- usage fiable (ecart < 2%),
- dashboard user affiche usage restant.

## Epic D - Fiabilite API

- D1: retries provider (deja entame)
- D2: timeouts stricts et erreurs propres
- D3: idempotency key sur requetes
- D4: circuit breaker simple si provider KO

Done criteria:

- aucune 500 non geree sur `/v1/transcribe`,
- erreurs clients explicites et actionnables.

## Epic E - Desktop hardening

- E1: auth desktop (token local securise)
- E2: settings sync depuis backend
- E3: diagnostics in-app (permissions mic/accessibility)
- E4: auto-update strategy (post-beta possible)

Done criteria:

- onboarding desktop < 3 minutes,
- taux echec setup < 10%.

## Epic F - Web app

- F1: landing + pricing
- F2: app dashboard (usage, plan, settings)
- F3: page billing
- F4: page support/help

Done criteria:

- user peut creer compte, s'abonner, consulter usage sans support.

## 8) Sprints (12 semaines)

## Sprint 1 (S1): Foundation data + auth

- setup Postgres + migrations
- table users/subscriptions/plans
- auth email
- endpoint `me`

Gate:

- login complet + lecture profil.

## Sprint 2 (S2): Stripe base

- create plans Stripe
- checkout + webhook
- subscription sync

Gate:

- passage free -> pro stable en staging.

## Sprint 3 (S3): Usage metering

- usage_events + aggregate monthly
- quotas appliques en preflight

Gate:

- blocage quota fonctionnel avec message clair.

## Sprint 4 (S4): Transcribe reliability

- retries/timeouts/codes erreur propres
- idempotency key
- observabilite de base

Gate:

- P95 stable et baisse erreurs 5xx.

## Sprint 5 (S5): Desktop auth + settings

- token storage
- sync settings utilisateur
- onboarding permissions guide

Gate:

- nouveau user installe et dicte sans intervention manuelle externe.

## Sprint 6 (S6): Web app alpha

- dashboard usage
- plans/pricing
- billing portal

Gate:

- boucle self-serve complete.

## Sprint 7 (S7): QA hardening

- tests e2e critiques
- securite headers, rate limits
- runbooks incidents

Gate:

- release candidate beta.

## Sprint 8-9 (S8-S9): Private beta

- 20-50 users invites
- feedback loops
- quick fixes hebdo

Gate:

- retention W1 satisfaisante et churn early compris.

## Sprint 10-12 (S10-S12): Paid beta

- ouverture paiements limitee
- optimisation funnel conversion
- optimisation cout IA / marge

Gate:

- premiers clients payants recurrents.

## 9) Critères d'acceptation (transverses)

- Aucune regression sur boucle core hotkey -> texte.
- Erreurs toujours explicites cote client.
- Temps de setup initial < 3 min.
- Temps moyen transcription < 6 s sur clips courts.
- Aucune fuite de donnees logs sensibles.

## 10) KPI de pilotage (hebdomadaire)

## Produit

- Transcription success rate.
- Latence P50 / P95.
- Crash-free desktop sessions.
- % transcriptions avec correction manuelle.

## Growth

- signups / semaine
- activation D1
- retention W1 / W4
- invitation -> install conversion

## Business

- conversion free -> pro
- MRR
- churn mensuel
- marge brute estimee (revenu - cout IA - infra)

## 11) Securite et privacy checklist

- JWT rotation + expiration courte.
- Chiffrement TLS uniquement.
- Secret management (pas de secrets dans repo).
- Logs sans contenu texte brut par defaut.
- Retention configurable des evenements.
- Export/suppression compte utilisateur.

## 12) Plan Stripe concret

1. Creer 3 produits (`free`, `pro`, `power`).
2. Configurer price monthly (+ annual plus tard).
3. Implémenter checkout session par plan.
4. Implémenter webhook:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Mettre a jour `subscriptions` + entitlements.
6. Exposer customer portal.

## 13) Plan QA et tests

## Tests automatiques

- unitaires service transcription/quotas/errors.
- integration API auth+billing+transcribe.
- smoke desktop (mock API).

## Tests manuels critiques

- onboarding complet nouveau user.
- quota atteint.
- subscription upgrade/downgrade.
- provider indisponible.
- permissions micro/accessibility cassees.

## 14) Runbooks incidents

## Incident type A: provider IA indisponible

- Detection: hausse 502.
- Action: activer retry policy stricte + message utilisateur.
- Communication: status page + notif in-app.

## Incident type B: Stripe webhook KO

- Detection: desync subscription state.
- Action: reprocess events via Stripe CLI/dashboard.

## Incident type C: latence forte

- Detection: P95 > seuil.
- Action: limiter concurrency, fallback model, analyser requetes longues.

## 15) Definition of Done (DoD) par ticket

Un ticket est "done" quand:

- code merge + review,
- tests passes,
- logs/metriques ajoutes si necessaire,
- doc utilisateur/dev mise a jour,
- feature testee sur environnement cible.

## 16) Cadence de gouvernance

- Daily async: blocages + priorites.
- Weekly product review: KPI + feedback users.
- Weekly tech review: dette, incidents, perf, cout IA.
- Biweekly roadmap review: scope et priorites.

## 17) Plan de lancement private beta (checklist)

- [ ] onboarding page operationnelle
- [ ] auth stable
- [ ] billing dry-run teste
- [ ] quota policy active
- [ ] observability dashboard pret
- [ ] support canal (email/discord) en place
- [ ] legal minimum (CGU, privacy policy)
- [ ] backup et rollback plan

## 18) Sequencing immediat (7 prochains jours)

Jour 1-2:

- figer architecture et stack finale,
- creer schema DB + migrations,
- implementer auth de base.

Jour 3-4:

- integrer Stripe checkout + webhook,
- stocker subscriptions/entitlements.

Jour 5:

- ajouter usage metering basique,
- endpoint usage current-period.

Jour 6:

- connecter desktop auth token + appel API protege.

Jour 7:

- test end-to-end complet + bugfix pass + release beta interne.

## 19) Annexes (templates)

## Template ticket execution

- Contexte:
- Objectif:
- Scope in:
- Scope out:
- Done criteria:
- Risks:
- Metrics impactees:

## Template postmortem incident

- Incident:
- Impact:
- Root cause:
- Detection gap:
- Corrective action:
- Preventive action:

