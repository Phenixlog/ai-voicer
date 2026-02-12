#!/bin/bash
# =============================================================================
# Théoria - Script de Déploiement Render.com
# =============================================================================
# Usage: ./deploy-render.sh [create|update|logs|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vérifier que Render CLI est installé
check_render_cli() {
    if ! command -v render &> /dev/null; then
        echo -e "${RED}❌ Render CLI n'est pas installé${NC}"
        echo ""
        echo "Installation:"
        echo "  brew install render"  # macOS
        echo "  # ou voir: https://render.com/docs/cli"
        exit 1
    fi
}

# Vérifier l'authentification
check_auth() {
    if ! render whoami &> /dev/null; then
        echo -e "${RED}❌ Vous n'êtes pas connecté à Render${NC}"
        echo ""
        echo "Connectez-vous avec: render login"
        exit 1
    fi
}

# Créer un nouveau service
create_service() {
    echo -e "${BLUE}🚀 Création d'un nouveau service sur Render...${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # Vérifier le blueprint
    if [ ! -f "infrastructure/render.yaml" ]; then
        echo -e "${RED}❌ Fichier render.yaml non trouvé${NC}"
        exit 1
    fi
    
    echo "Cette commande va créer:"
    echo "  • PostgreSQL database"
    echo "  • Redis cache"
    echo "  • Web service (API)"
    echo ""
    read -p "Continuer? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        render blueprint apply infrastructure/render.yaml
        echo -e "${GREEN}✅ Service créé!${NC}"
        echo ""
        echo "⚠️  IMPORTANT: Configurez les secrets dans le dashboard Render:"
        echo "   https://dashboard.render.com"
        echo ""
        echo "Variables à configurer:"
        echo "  • MISTRAL_API_KEY"
        echo "  • AI_VOICER_API_AUTH_TOKEN"
    fi
}

# Mettre à jour le service (redéployer)
update_service() {
    echo -e "${BLUE}🔄 Mise à jour du service...${NC}"
    
    # Lister les services
    echo ""
    echo "Services disponibles:"
    render services list
    echo ""
    
    read -p "Entrez le nom du service à mettre à jour: " service_name
    
    if [ -n "$service_name" ]; then
        render deploy "$service_name"
        echo -e "${GREEN}✅ Déploiement déclenché!${NC}"
    fi
}

# Afficher les logs
show_logs() {
    echo -e "${BLUE}📜 Logs du service...${NC}"
    
    # Lister les services
    echo ""
    echo "Services disponibles:"
    render services list
    echo ""
    
    read -p "Entrez le nom du service (laisser vide pour 'theoria-api'): " service_name
    service_name=${service_name:-theoria-api}
    
    echo ""
    echo "Affichage des logs (Ctrl+C pour quitter)..."
    render logs --service "$service_name" --follow
}

# Afficher le statut
show_status() {
    echo -e "${BLUE}📊 Statut des services...${NC}"
    echo ""
    
    render services list
}

# Menu principal
show_menu() {
    echo ""
    echo "========================================"
    echo "🚀 Théoria - Déploiement Render.com"
    echo "========================================"
    echo ""
    echo "Commandes disponibles:"
    echo "  1. create  - Créer un nouveau service"
    echo "  2. update  - Mettre à jour (redéployer)"
    echo "  3. logs    - Voir les logs"
    echo "  4. status  - Statut des services"
    echo "  5. quit    - Quitter"
    echo ""
}

# Main
main() {
    check_render_cli
    check_auth
    
    COMMAND=${1:-""}
    
    case $COMMAND in
        create)
            create_service
            ;;
        update)
            update_service
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        *)
            show_menu
            read -p "Choisissez une option (1-5): " choice
            
            case $choice in
                1) create_service ;;
                2) update_service ;;
                3) show_logs ;;
                4) show_status ;;
                5) echo "Au revoir!"; exit 0 ;;
                *) echo -e "${RED}Option invalide${NC}"; exit 1 ;;
            esac
            ;;
    esac
}

main "$@"
