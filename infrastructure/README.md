# 🏗️ Théoria Infrastructure

Ce dossier contient toute l'infrastructure as code pour le déploiement de Théoria en production.

---

## 📁 Structure

```
infrastructure/
├── README.md                     # Ce fichier
├── ARCHITECTURE.md               # Documentation architecture complète
├── DEPLOYMENT.md                 # Guide de déploiement step-by-step
├── docker-compose.yml            # Stack de développement local
├── Dockerfile                    # Image de production
├── .dockerignore                 # Fichiers exclus du build Docker
├── render.yaml                   # Blueprint Render.com (IaC)
├── railway.toml                  # Configuration Railway (alternative)
├── .env.production.example       # Template variables d'environnement
├── scripts/                      # Scripts utilitaires
│   ├── setup-local.sh           # Setup environnement local
│   ├── deploy-render.sh         # Déploiement Render.com
│   └── health-check.sh          # Vérification santé
└── init-db/                      # Scripts d'initialisation DB (optionnel)
```

---

## 🚀 Démarrage Rapide

### 1. Développement Local (Docker)

```bash
cd infrastructure

# Setup initial (crée .env et lance les services)
./scripts/setup-local.sh

# Ou manuellement:
cp .env.production.example .env
# Éditer .env avec vos clés API
docker-compose up -d
```

### 2. Déploiement Production (Render.com)

```bash
# Via le script interactif
./scripts/deploy-render.sh

# Ou via GitHub Actions (recommandé)
git push origin main  # Déclenche le workflow deploy.yml
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture technique, schémas, décisions |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guide de déploiement complet |

---

## 🔧 Configuration Requise

### Variables d'Environnement Critiques

| Variable | Description | Où la configurer |
|----------|-------------|------------------|
| `MISTRAL_API_KEY` | Clé API Mistral AI | Render Dashboard → Environment |
| `AI_VOICER_API_AUTH_TOKEN` | Token d'authentification API | Render Dashboard → Environment |
| `DATABASE_URL` | Connexion PostgreSQL | Auto-généré par Render |
| `REDIS_URL` | Connexion Redis | Auto-généré par Render |

---

## 🧪 Tests et Vérification

```bash
# Vérification santé locale
./scripts/health-check.sh local

# Vérification santé production
./scripts/health-check.sh production

# Test manuel
curl http://localhost:8000/health
```

---

## 💰 Providers Supportés

| Provider | Fichier de config | Coût estimé MVP |
|----------|-------------------|-----------------|
| **Render.com** | `render.yaml` | $7-15/mois |
| **Railway** | `railway.toml` | $5-20/mois |

---

## 🆘 Support

En cas de problème:
1. Consulter [DEPLOYMENT.md](DEPLOYMENT.md) section Troubleshooting
2. Vérifier les logs: `docker-compose logs` ou Dashboard Render
3. Vérifier la santé: `./scripts/health-check.sh`
