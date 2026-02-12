#!/bin/bash
# =============================================================================
# Théoria - Script de Vérification de Santé
# =============================================================================
# Usage: ./health-check.sh [local|production]

set -e

ENV=${1:-local}

# Configuration selon l'environnement
if [ "$ENV" = "production" ]; then
    BASE_URL="${PROD_URL:-https://theoria-api.onrender.com}"
    API_TOKEN="${AI_VOICER_API_AUTH_TOKEN:-}"
else
    BASE_URL="http://localhost:8000"
    API_TOKEN="${AI_VOICER_API_AUTH_TOKEN:-}"
fi

echo "🏥 Théoria - Health Check ($ENV)"
echo "================================="
echo ""
echo "URL: $BASE_URL"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction pour faire une requête et vérifier
check_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK ($HTTP_STATUS)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (expected $expected_status, got $HTTP_STATUS)${NC}"
        return 1
    fi
}

# Tests
ERRORS=0

check_endpoint "Health endpoint" "/health" 200 || ((ERRORS++))

# Test avec authentification si token disponible
if [ -n "$API_TOKEN" ]; then
    echo ""
    echo "Testing authenticated endpoints..."
    
    # Créer un fichier audio de test (silence)
    if command -v ffmpeg >/dev/null 2>&1; then
        TMP_FILE=$(mktemp /tmp/test_audio.XXXXXX.wav)
        ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 1 -acodec pcm_s16le "$TMP_FILE" -y 2>/dev/null || true
        
        if [ -f "$TMP_FILE" ]; then
            echo -n "Testing transcription endpoint... "
            HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                -X POST \
                -H "X-API-Key: $API_TOKEN" \
                -F "audio=@$TMP_FILE" \
                -F "structured=false" \
                "$BASE_URL/v1/transcribe" 2>/dev/null || echo "000")
            
            # 200 ou 502 (Mistral peut rejeter le silence)
            if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "502" ]; then
                echo -e "${GREEN}✅ OK ($HTTP_STATUS)${NC}"
            else
                echo -e "${YELLOW}⚠️  UNEXPECTED ($HTTP_STATUS)${NC}"
            fi
            
            rm -f "$TMP_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️  ffmpeg not installed, skipping transcription test${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  AI_VOICER_API_AUTH_TOKEN not set, skipping auth tests${NC}"
fi

# Résumé
echo ""
echo "================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 Tous les tests ont réussi!${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS test(s) ont échoué${NC}"
    exit 1
fi
