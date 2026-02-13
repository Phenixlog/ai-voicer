# Theoria - Roadmap Production (SaaS + Desktop)

## 1) Pourquoi ce document

Ce document definit le chemin pour passer de "MVP qui marche pour nous" a "produit vendable pour des clients externes".

Objectif: clarifier ce qui est deja en place, ce qu'il reste a construire, et l'ordre d'execution.

## 2) Point de depart (etat actuel)

### Deja en place

- API SaaS en ligne sur Railway.
- Base Postgres en ligne sur Railway.
- Landing page et web app deployees.
- Flux fonctionnel valide: daemon local -> API Railway -> transcription -> collage texte.
- Login utilisateur, settings, usage de base.

### Limites actuelles

- Le daemon est encore lance en mode "dev" (script Python), pas distribue proprement.
- Auth encore trop faible pour une ouverture publique large.
- Pas encore de parcours onboarding desktop "sans terminal".
- Packaging client final non finalise.

## 3) Vision cible produit

Un utilisateur externe doit pouvoir:

1. Creer un compte sur le web.
2. Telecharger "Theoria Desktop".
3. Ouvrir l'app, se connecter, valider les permissions macOS.
4. Configurer sa hotkey.
5. Fermer l'app et continuer a dicter en background.

Sans intervention manuelle ni commande terminal.

## 4) Roadmap par phases

## Phase A - Productiser le desktop client (Sprint 1)

Objectif: supprimer la friction terminal et rendre l'installation utilisable par un non-tech.

Livrables:

- App desktop installable (Mac).
- Onboarding guide (permissions + connexion + hotkey).
- Daemon lance automatiquement au login.
- Ecran de statut clair (connecte, ecoute, transcription, erreur).

Critere de sortie:

- Un testeur externe installe en moins de 5 minutes et dicte sans aide.

## Phase B - Securite et fiabilite SaaS (Sprint 2)

Objectif: fiabiliser l'exploitation et proteger les comptes.

Livrables:

- Auth securisee (magic link/OTP).
- Gestion des erreurs et retries renforces.
- Observabilite de base (logs, erreurs, alertes).
- Verifications multi-user (isolation data, quotas, sessions).

Critere de sortie:

- Pas de faille evidente d'auth et production stable sur plusieurs jours.

## Phase C - Go-to-market operable (Sprint 3)

Objectif: pouvoir vendre et supporter les premiers clients.

Livrables:

- Parcours acquisition simple (site -> signup -> download -> activation).
- Billing Stripe finalise (checkout, portal, webhook complet).
- Pages legales (Privacy, Terms) et support minimal.
- Process de release desktop et rollback clair.

Critere de sortie:

- 10+ utilisateurs externes actifs sans support synchrone permanent.

## 5) Priorisation stricte

1. D'abord Sprint 1 (desktop produit), sinon aucun client non-tech ne peut activer la valeur.
2. Ensuite Sprint 2 (auth + fiabilite), sinon risque business et support.
3. Enfin Sprint 3 (conversion et operations), pour scaler proprement.

## 6) Definition "Production Ready" (v1)

Le produit est considere "production ready v1" si:

- Installation desktop simple et stable.
- Connexion utilisateur fiable.
- Dictation fonctionne sans terminal.
- Donnees utilisateur isolees et persistantes.
- Monitoring minimal en place.
- Facturation et plan free/pro operationnels.

## 7) Prochaine action immediate

Demarrer Sprint 1 avec un backlog executable et un ordre d'implementation clair.
