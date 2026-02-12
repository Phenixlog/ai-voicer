#!/bin/bash
# =============================================================================
# Théoria - Script de Setup Local
# =============================================================================
# Usage: ./setup-local.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

echo "🚀 Théoria - Setup Environnement Local"
echo "========================================"

# Vérifier les prérequis
echo ""
echo "📋 Vérification des prérequis..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker est requis mais n'est pas installé."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose est requis mais n'est pas installé."; exit 1; }

echo "✅ Docker et Docker Compose sont installés"

# Vérifier le fichier .env
echo ""
echo "🔧 Configuration de l'environnement..."

if [ ! -f "$INFRA_DIR/.env" ]; then
    if [ -f "$INFRA_DIR/.env.production.example" ]; then
        cp "$INFRA_DIR/.env.production.example" "$INFRA_DIR/.env"
        echo "✅ Fichier .env créé depuis .env.production.example"
        echo "⚠️  IMPORTANT: Éditez $INFRA_DIR/.env et configurez MISTRAL_API_KEY"
    else
        echo "❌ Fichier .env.production.example non trouvé"
        exit 1
    fi
else
    echo "✅ Fichier .env existe déjà"
fi

# Vérifier que MISTRAL_API_KEY est configuré
if ! grep -q "MISTRAL_API_KEY=your_" "$INFRA_DIR/.env" && ! grep -q "MISTRAL_API_KEY=$" "$INFRA_DIR/.env"; then
    echo "✅ MISTRAL_API_KEY semble configuré"
else
    echo "⚠️  ATTENTION: MISTRAL_API_KEY n'est pas configuré dans .env"
    echo "   Obtenez une clé sur: https://console.mistral.ai/"
fi

# Créer les répertoires nécessaires
echo ""
echo "📁 Création des répertoires..."
mkdir -p "$INFRA_DIR/init-db"
mkdir -p "$INFRA_DIR/logs"

# Lancer les services
echo ""
echo "🐳 Démarrage des services Docker..."
cd "$INFRA_DIR"
docker-compose up -d

# Attendre que les services soient prêts
echo ""
echo "⏳ Attente du démarrage des services..."
sleep 5

# Vérifier la santé des services
echo ""
echo "🏥 Vérification de la santé..."

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ API est en ligne!"
        break
    fi
    
    echo "   ⏳ API pas encore prête... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ L'API n'a pas démarré correctement"
    echo "   Consultez les logs: docker-compose logs api"
    exit 1
fi

# Afficher le résumé
echo ""
echo "========================================"
echo "🎉 Setup terminé avec succès!"
echo "========================================"
echo ""
echo "📊 Services disponibles:"
echo "   • API:        http://localhost:8000"
echo "   • Health:     http://localhost:8000/health"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis:      localhost:6379"
echo ""
echo "📝 Commandes utiles:"
echo "   • Logs API:       docker-compose logs -f api"
echo "   • Logs DB:        docker-compose logs -f postgres"
echo "   • Arrêter:        docker-compose down"
echo "   • Reset complet:  docker-compose down -v"
echo ""
echo "🔑 Pour tester l'API:"
echo "   curl http://localhost:8000/health"
echo ""
