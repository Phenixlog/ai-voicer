# Sprint 1 Backlog - Productiser le Desktop Client

## 1) Objectif sprint

Transformer le daemon actuel (mode script) en experience installable et utilisable par un client non-tech.

Resultat attendu fin sprint:

- installation simple,
- connexion compte,
- permissions macOS guidees,
- hotkey operationnelle,
- daemon auto-demarre au login.

## 2) Scope Sprint 1

## In

- Packaging desktop macOS.
- Onboarding desktop (connexion + permissions + hotkey).
- Auto-start daemon.
- Etat de service visible.
- Logging local minimal pour support.

## Out

- Auth magic link/OTP.
- Refonte business pricing.
- Release Windows.

## 3) Backlog priorise

## Epic A - Packaging Desktop

### S1-A1 (P0) - Definir structure app desktop

- Description: choisir la structure du client desktop (app shell + daemon runner + config locale).
- Output: architecture validee + arborescence claire.
- DoD: dossier desktop structure, scripts de run standardises.

### S1-A2 (P0) - Build app macOS installable

- Description: produire un binaire/app installable pour macOS.
- Output: package installable testable sur une autre machine.
- DoD: installation possible sans Python preinstalle.

### S1-A3 (P1) - Script de build/release interne

- Description: automatiser build + versioning + artefact.
- Output: commande unique pour generer release candidate.
- DoD: artefact reproductible sur 2 runs consecutifs.

## Epic B - Onboarding Desktop

### S1-B1 (P0) - Ecran connexion utilisateur

- Description: interface desktop pour login/logout et statut session.
- Output: utilisateur connecte sans terminal.
- DoD: login/logout fonctionne, erreur explicite en cas d'echec.

### S1-B2 (P0) - Assistant permissions macOS

- Description: guider Microphone, Accessibility, Input Monitoring.
- Output: checklist visuelle des permissions.
- DoD: utilisateur sait exactement quelle permission manque.

### S1-B3 (P1) - Settings hotkey + trigger mode

- Description: UI pour changer hotkey/mode et tester en direct.
- Output: settings persistantes.
- DoD: relance app conserve les settings.

## Epic C - Daemon Productise

### S1-C1 (P0) - Auto-start au login macOS

- Description: installer/maintenir LaunchAgent automatiquement.
- Output: daemon relance apres reboot sans terminal.
- DoD: reboot machine => daemon actif.

### S1-C2 (P0) - Statut runtime visible

- Description: afficher etat courant (idle/listening/transcribing/error).
- Output: panneau statut lisible pour utilisateur.
- DoD: changement d'etat coherent avec logs runtime.

### S1-C3 (P1) - Robustesse hotkey hold/toggle

- Description: finaliser gestion cas rate (missed release, key repeat).
- Output: aucun blocage frequent en usage normal.
- DoD: 30 essais consecutifs sans blocage critique.

## Epic D - Support et observabilite locale

### S1-D1 (P1) - Logs locaux exploitables

- Description: logs clairs, horodates, erreurs actionnables.
- Output: fichier log local par session.
- DoD: support peut diagnostiquer un incident avec logs seuls.

### S1-D2 (P2) - Ecran diagnostic rapide

- Description: infos utiles (backend url, auth status, permissions status).
- Output: vue "debug utilisateur".
- DoD: 80% des tickets "ca marche pas" resolubles via cet ecran.

## 4) Ordre d'implementation (strict)

1. S1-A1
2. S1-B1
3. S1-B2
4. S1-C1
5. S1-C2
6. S1-A2
7. S1-B3
8. S1-C3
9. S1-D1
10. S1-A3
11. S1-D2

## 5) Plan de validation sprint

## Test interne (jour 1-2 de validation)

- Installation from scratch sur machine test.
- Login, permissions, test hotkey, transcription, paste.
- Reboot machine, validation auto-start daemon.

## Test externe (jour 3-4 de validation)

- 2 testeurs non-tech.
- Suivre script d'installation sans aide synchrone.
- Collecter friction points et erreurs.

## 6) Definition of Done sprint

Sprint 1 est termine si:

- Un utilisateur externe installe et active seul en <= 5 minutes.
- Plus besoin d'ouvrir un terminal.
- Le daemon tourne au login automatiquement.
- La dictation fonctionne de bout en bout avec l'API Railway.
- Les erreurs critiques sont visibles et comprehensibles.

## 7) Risques sprint + mitigation

- Risque: permissions macOS incomprises.
  - Mitigation: assistant pas-a-pas + statuts explicites.
- Risque: packaging fragile.
  - Mitigation: script build/release reproductible.
- Risque: daemon bloque en production client.
  - Mitigation: durcissement hold/toggle + logs utiles + restart auto.

## 8) Action immediate (demarrage)

Commencer par S1-A1 et S1-B1 dans la meme branche de travail, puis valider un premier parcours "login desktop sans terminal".
