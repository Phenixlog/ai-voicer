# 🚀 Théoria - Guide de Déploiement

Ce guide explique comment déployer l'API Théoria en production sur Render.com (recommandé) ou Railway.

---

## 📋 Prérequis

- Compte [Render.com](https://render.com) (ou [Railway](https://railway.app))
- Compte [GitHub](https://github.com)
- Clé API Mistral ([Obtenir une clé](https://console.mistral.ai/))
- Git installé localement

---

## 🎯 Option 1: Déploiement sur Render.com (Recommandé)

### Étape 1: Fork/Push du Repository

```bash
# Si vous partez de zéro
git clone <your-repo-url>
cd ai-voicer

# Créer un nouveau repo sur GitHub et pousser
git remote add origin <your-github-url>
git push -u origin main
```

### Étape 2: Créer une Blueprint sur Render

1. Connectez-vous à [Render Dashboard](https://dashboard.render.com)
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Connectez votre compte GitHub et sélectionnez le repo `ai-voicer`
4. Render détectera automatiquement le fichier `infrastructure/render.yaml`

### Étape 3: Configuration des Variables d'Environnement

Dans le dashboard Render, configurez les variables secrètes suivantes :

```bash
# OBLIGATOIRE - Clé API Mistral
MISTRAL_API_KEY=sk-xxxxxxxxxxxxxxxx

# OBLIGATOIRE - Authentification API (générez un token sécurisé)
AI_VOICER_API_AUTH_TOKEN=votre_token_ultra_securise_ici
```

**Générer un token sécurisé :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Étape 4: Déploiement

1. Cliquez sur **"Apply"** dans la Blueprint
2. Render va automatiquement :
   - Créer la base de données PostgreSQL
   - Créer le cache Redis
   - Build et déployer l'API
3. Attendez que le statut passe à **"Live"** (2-3 minutes)

### Étape 5: Vérification

```bash
# Test de santé
curl https://votre-api.onrender.com/health

# Résultat attendu
{"status":"ok"}
```

---

## 🚂 Option 2: Déploiement sur Railway

### Étape 1: Installer Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Étape 2: Initialiser le Projet

```bash
cd ai-voicer
railway init --name theoria-api
```

### Étape 3: Ajouter les Services

```bash
# Ajouter PostgreSQL
railway add --database postgres

# Ajouter Redis
railway add --database redis
```

### Étape 4: Configurer les Variables

```bash
railway variables set MISTRAL_API_KEY="sk-xxxxx"
railway variables set AI_VOICER_API_AUTH_TOKEN="votre_token"
railway variables set AI_VOICER_LOG_LEVEL="INFO"
```

### Étape 5: Déployer

```bash
railway up
```

---

## 🐳 Développement Local avec Docker

### Démarrage Rapide

```bash
cd infrastructure

# Copier les variables d'environnement
cp .env.production.example .env
# Éditer .env avec vos vraies valeurs

# Lancer la stack complète
docker-compose up -d

# Vérifier les services
docker-compose ps

# Logs
docker-compose logs -f api
```

### Commandes Utiles

```bash
# Rebuild après modification du code
docker-compose up -d --build api

# Accès à la base de données
docker-compose exec postgres psql -U theoria -d theoria

# Accès à Redis
docker-compose exec redis redis-cli

# Arrêter tout
docker-compose down

# Reset complet (⚠️ perd les données)
docker-compose down -v
```

---

## 🔄 CI/CD - GitHub Actions

### Configuration des Secrets GitHub

Dans **Settings** → **Secrets and variables** → **Actions**, ajoutez :

| Secret | Description | Où trouver |
|--------|-------------|------------|
| `RENDER_API_KEY` | Clé API Render | Render Dashboard → Account Settings → API Keys |
| `RENDER_SERVICE_ID` | ID du service web | Render Dashboard → Service → Settings → ID |

### Workflow Automatique

Le workflow CI/CD est déclenché automatiquement :

```
Push sur main → Tests → Lint → Build → Déploiement Render → Vérification
```

### Déploiement Manuel

```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Ou depuis l'interface GitHub
# Actions → Deploy to Production → Run workflow
```

---

## 📊 Monitoring

### Logs Render.com

```bash
# Via CLI (install render-cli)
render logs --service theoria-api

# Via dashboard
https://dashboard.render.com/web/{service-id}/logs
```

### Endpoints de Santé

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Statut général du service |
| `GET /` | Page d'accueil/info API |

### Métriques Importantes

- **CPU/Memory**: Dashboard Render
- **Response Time**: Render metrics
- **Error Rate**: Logs + Sentry (si configuré)

---

## 🛡️ Sécurité

### Checklist Production

- [ ] `AI_VOICER_API_AUTH_TOKEN` configuré et complexe
- [ ] `MISTRAL_API_KEY` stocké dans les secrets Render
- [ ] HTTPS forcé (Render le fait automatiquement)
- [ ] CORS configuré pour les domaines autorisés
- [ ] Rate limiting activé
- [ ] Logs centralisés (Logtail/BetterStack)

### Rotation des Secrets

```bash
# Générer nouveau token
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Mettre à jour sur Render
# Dashboard → Service → Environment → Modifier AI_VOICER_API_AUTH_TOKEN
```

---

## 🆘 Troubleshooting

### Problème: "Build failed"

```bash
# Vérifier les logs de build
render deploy-logs --service theoria-api

# Common fixes:
# 1. Vérifier que requirements.txt est à jour
# 2. Vérifier les imports dans le code
# 3. S'assurer que le Dockerfile est valide
docker build -f infrastructure/Dockerfile -t test-build .
```

### Problème: "Service won't start"

```bash
# Vérifier les variables d'environnement
render env --service theoria-api

# Vérifier que MISTRAL_API_KEY est défini
# Vérifier que DATABASE_URL est bien formé
```

### Problème: "Database connection error"

1. Vérifier que PostgreSQL est en statut "Available"
2. Vérifier que `DATABASE_URL` pointe vers la bonne DB
3. Vérifier les firewall rules (IP allowlist)

### Problème: "Out of memory"

1. Upgrade le plan Render : Starter → Standard
2. Optimiser le Dockerfile (multi-stage build déjà fait)
3. Vérifier les memory leaks dans l'application

---

## 💰 Optimisation des Coûts

### Gratuit vs Payant (Render)

| Service | Gratuit | Starter ($7/mois) | Standard ($25/mois) |
|---------|---------|-------------------|---------------------|
| Web Service | ✅ 512MB RAM | ✅ 512MB + always-on | ✅ 2GB RAM |
| PostgreSQL | ✅ 256MB | ❌ | ✅ 4GB + backups |
| Redis | ✅ 256MB | ❌ | ✅ 5GB |

### Recommandations par Phase

| Phase | Setup | Coût mensuel estimé |
|-------|-------|---------------------|
| MVP/Dev | Gratuit + PostgreSQL Starter | $7-15 |
| Beta | Starter Web + Standard DB | $50-75 |
| Production | Standard Web + Standard DB + Redis | $100-150 |

---

## 🌍 Custom Domain (Optionnel)

### Ajouter un Domaine Personnalisé sur Render

1. Dashboard → Service → Settings → Custom Domain
2. Ajouter `api.theoria.app`
3. Configurer les DNS chez votre registrar :
   ```
   CNAME api.theoria.app → theoria-api.onrender.com
   ```
4. Attendre la propagation DNS (5-60 min)
5. Render provisionnera automatiquement le certificat SSL

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Logs**: Dashboard → Service → Logs
- **Status Page**: https://status.render.com

---

## 📝 Changements

Voir [CHANGELOG.md](../CHANGELOG.md) pour l'historique des déploiements.
