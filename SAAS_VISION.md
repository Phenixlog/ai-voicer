# Theoria - Vision SaaS B2C

## 1) Contexte et ambition

Nous avons validé un MVP puissant: une expérience de dictée push-to-talk ultra fluide, avec transcription et structuration automatique.

L'ambition de Theoria est de devenir le **copilote vocal personnel** de tous les profils qui écrivent beaucoup (fondateurs, freelances, creators, commerciaux, étudiants, managers), en réduisant la friction entre la pensée et le texte.

Objectif long terme: faire de la voix le canal d'entrée principal du texte dans les outils numériques.

## 2) Vision produit

**Promesse produit**

"Parlez naturellement, Theoria écrit proprement pour vous, partout."

**Proposition de valeur**

- Dictée instantanée, contextuelle et fiable.
- Nettoyage intelligent du texte sans trahir le sens.
- Intégration transparente dans n'importe quel champ texte.
- UX minimaliste et rapide (hotkey -> parler -> texte prêt).

**Ce qui rend Theoria différent**

- Focus extrême sur la vitesse et la fiabilité d'injection.
- Structuration orientée usage réel (message, email, note, prompt).
- Contrôle fin du style (ton, format, longueur), sans bavardage IA.
- Coût optimisé via modèles audio récents (Voxtral) + architecture efficiente.

## 3) Cible B2C initiale

## Segment primaire (beachhead)

- Solopreneurs, freelances, consultants, builders.
- Besoin: écrire vite dans Slack, Notion, CRM, email, chats IA.
- Sensibles au gain de temps quotidien et à la simplicité.

## Segment secondaire

- Étudiants et créateurs de contenu.
- Profils multilingues.
- Managers qui produisent beaucoup de messages et notes.

## ICP utilisateur

- Produit > 20 messages/notes/jour.
- Tolérance faible à la friction.
- Prêt à payer pour gagner 30-90 min/semaine.

## 4) Jobs-to-be-done

- "Quand je dois écrire vite, je veux parler et obtenir un texte propre immédiatement."
- "Quand j'ai une idée à chaud, je veux la capturer sans casser mon flow."
- "Quand je passe d'un outil à un autre, je veux garder la même expérience de dictée."
- "Quand j'utilise la voix, je veux un résultat publiable sans retouche lourde."

## 5) Positionnement et messaging

## Positionnement

Theoria est un **assistant vocal de production écrite** (pas un simple transcripteur).

## Message central

"Votre pensée, directement en texte clair."

## Pillars marketing

- Fast: quelques secondes du son au texte prêt.
- Clean: ponctuation, structure, clarté.
- Everywhere: fonctionne dans tous les champs texte.
- Private by design: contrôle utilisateur sur ses données.

## 6) Expérience utilisateur cible

## Boucle principale

1. L'utilisateur maintient (ou toggle) une hotkey.
2. HUD discret confirme l'état "Ecoute...".
3. Relâchement -> "Transcription...".
4. Texte nettoyé injecté dans le champ actif.
5. Son système restauré automatiquement.

## Règles UX non négociables

- 1 geste, 1 résultat.
- Aucun pop-up intrusif.
- Aucun texte méta ("voici la correction...").
- Latence perçue faible.
- Zéro configuration complexe au démarrage.

## 7) Portée produit (MVP SaaS commercial)

## Ce qui est inclus

- Auth utilisateur (email + OAuth).
- Desktop app client (hotkey + capture audio + HUD).
- Backend API de transcription/structuration.
- Dashboard web minimal:
  - profil et settings,
  - historique court des transcriptions,
  - gestion abonnement.
- Paiement Stripe.
- Limites d'usage par plan.

## Ce qui n'est pas inclus v1

- Collaboration équipe avancée.
- API publique complète.
- Marketplace d'automations.
- Mobile natif.

## 8) Architecture cible

## Couches

- **Client desktop**: capture audio, hotkey globale, HUD, paste.
- **API SaaS**: auth, quotas, billing checks, orchestration IA.
- **Workers**: tâches asynchrones (si besoin, selon volume).
- **Data layer**: users, plans, events, usages, sessions.
- **Observability**: logs, métriques, alerting.

## Principes techniques

- Stateless API autant que possible.
- Idempotence des requêtes de transcription.
- Dégradation gracieuse en cas d'échec provider.
- Traçabilité forte (request id, erreurs catégorisées).

## 9) IA et qualité de sortie

## Pipeline logique

1. Transcription audio (Voxtral).
2. Post-traitement structuration (modèle texte léger).
3. Filtre anti-meta + garde-fous de style.
4. Injection finale.

## Objectifs qualité

- Fidélité sémantique élevée.
- Aucune hallucination de contenu.
- Style configurable par profil utilisateur.
- Support FR/EN excellent au lancement.

## 10) Business model B2C

## Freemium + abonnement

- **Free**: quota mensuel limité, watermark soft UX.
- **Pro**: usage élevé + options style avancées.
- **Power**: très gros volume + priorités latence.

## Hypothèse pricing (à tester)

- Pro: 12-19 EUR/mois.
- Power: 29-39 EUR/mois.

## Mécanique de marge

- Optimiser coût IA/minute audio.
- Router vers modèle adapté au contexte.
- Réduire retries inutiles et payloads lourds.

## 11) Go-to-market (GTM)

## Acquisition initiale

- Contenu organique (build in public, démos courtes).
- Distribution Twitter/LinkedIn/communautés no-code/solopreneurs.
- Landing page avec vidéo de 30 sec orientée use-case.

## Activation

- Onboarding < 3 min.
- Test guidé instantané.
- "Aha moment" dès première dictée.

## Rétention

- Usage quotidien (streak léger).
- Personnalisation style et context bias.
- Feedback qualité en 1 clic.

## 12) KPI et métriques pilotage

## Produit

- Time-to-first-transcription.
- Taux de succès transcription.
- Latence médiane et P95.
- Taux de correction manuelle post-injection.

## Business

- Activation D1.
- Rétention W1/W4.
- Conversion Free -> Pro.
- MRR, churn logo/revenu.
- Coût IA par utilisateur actif.

## 13) Roadmap proposée (90 jours)

## Phase 1 (S1-S3): Foundation SaaS

- Auth + users + Stripe.
- API robuste (quotas, erreurs propres, retries, logs).
- Client desktop packagé.
- Landing + waitlist.

## Phase 2 (S4-S7): Product polish

- Styles de sortie (message, email, note, prompt).
- Historique et replay court.
- Meilleur HUD + settings.
- Multi-langue et context packs.

## Phase 3 (S8-S12): Monetization + scale

- Plans payants live.
- Expériences d'upsell in-app.
- Monitoring coûts et optimisation marge.
- Programme referral simple.

## 14) Risques principaux et mitigations

- **Qualité variable selon contexte audio** -> fallback, recommandations micro, feedback loop.
- **Latence réseau/provider** -> retries, timeouts, statut UX clair.
- **Coût IA qui grimpe** -> routing modèle, plafonds, optimisation prompts.
- **Friction permissions OS** -> onboarding guidé, diagnostics auto.
- **Concurrence rapide** -> différenciation UX + focus speed/reliability.

## 15) Privacy, conformité et confiance

- Politique de conservation explicite (durée configurable).
- Option "do not store content" pour utilisateurs sensibles.
- Chiffrement transit + repos.
- Transparence sur fournisseurs IA utilisés.
- Contrôle utilisateur sur suppression de données.

## 16) Vision marque

Theoria doit être perçu comme:

- discret,
- fiable,
- rapide,
- élégant.

Ce n'est pas un gadget IA, c'est un outil de production quotidienne.

## 17) Décisions produit immédiates

- Garder le focus B2C solo (pas de dispersion B2B maintenant).
- Prioriser vitesse + fiabilité avant fonctionnalités secondaires.
- Stabiliser un onboarding frictionless.
- Déployer pricing tôt pour valider willingness-to-pay.

## 18) Prochain livrable

Transformer cette vision en exécution avec un `SAAS_EXECUTION_PLAN.md` contenant:

- backlog priorisé,
- architecture technique détaillée,
- modèle de données,
- plan Stripe,
- checklist lancement private beta.
