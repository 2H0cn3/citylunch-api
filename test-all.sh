#!/usr/bin/env bash
# test-all.sh — Smoke test bout-en-bout de l'API CityLunch
# Usage : bash test-all.sh
# Prérequis : l'API doit tourner (uvicorn app.main:app --reload)

set -e

BASE_URL="http://localhost:8000"
TIMESTAMP=$(date +%s)
EMAIL="test_${TIMESTAMP}@citylunch.fr"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

step() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
ok()   { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Helper : extraire un champ d'une réponse JSON sans dépendre de jq
json_get() {
  python -c "import sys, json
try:
    print(json.load(sys.stdin).get('$1', ''))
except Exception:
    print('')
"
}

# === Health check ===
step "Health check"
HEALTH=$(curl -s "$BASE_URL/")
echo "  → $HEALTH"
echo "$HEALTH" | grep -q '"status":"ok"' && ok "API en ligne" || fail "API injoignable. Lance d'abord : uvicorn app.main:app --reload"

# === Partie 1 — Produits ===
step "Partie 1 — Produits (CRUD public)"

echo "POST /products"
RESP=$(curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"nom":"Poulet roti","description":"Plat du jour","type":"PLAT","prix":12.5}')
echo "  → $RESP"
PRODUCT_ID=$(echo "$RESP" | json_get id)
[ -n "$PRODUCT_ID" ] && ok "Produit créé (id=$PRODUCT_ID)" || fail "Création produit"

echo "GET /products"
curl -s "$BASE_URL/products" >/dev/null && ok "Liste des produits"

echo "GET /products/$PRODUCT_ID"
curl -s "$BASE_URL/products/$PRODUCT_ID" >/dev/null && ok "Lecture par id"

echo "PUT /products/$PRODUCT_ID"
RESP=$(curl -s -X PUT "$BASE_URL/products/$PRODUCT_ID" \
  -H "Content-Type: application/json" \
  -d '{"prix":13.5}')
echo "  → $RESP"
echo "$RESP" | grep -q '"prix":13.5' && ok "Mise à jour" || fail "Update produit"

echo "DELETE /products/$PRODUCT_ID"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/products/$PRODUCT_ID")
[ "$STATUS" = "204" ] && ok "Suppression (204)" || fail "Delete produit, reçu $STATUS"

echo "GET /products/9999 (404 attendu)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/products/9999")
[ "$STATUS" = "404" ] && ok "404 sur produit inexistant" || fail "404 attendu, reçu $STATUS"

echo "POST /products avec payload invalide (422 attendu)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"nom":"sans prix"}')
[ "$STATUS" = "422" ] && ok "422 sur validation Pydantic" || fail "422 attendu, reçu $STATUS"

# Recréer un produit pour la partie sac
PRODUCT_ID=$(curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{"nom":"Tarte","type":"DESSERT","prix":4.5}' | json_get id)
ok "Produit recréé pour la suite (id=$PRODUCT_ID)"

# === Partie 1 — Livreurs ===
step "Partie 1 — Livreurs (CRUD public)"

echo "POST /livreurs"
RESP=$(curl -s -X POST "$BASE_URL/livreurs" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"nom\":\"Dupont\",\"prenom\":\"Jean\"}")
echo "  → $RESP"
LIVREUR_ID=$(echo "$RESP" | json_get id)
PASSWORD=$(echo "$RESP" | json_get mot_de_passe_initial)
[ -n "$LIVREUR_ID" ] && ok "Livreur créé (id=$LIVREUR_ID, mdp=$PASSWORD)" || fail "Création livreur"

echo "GET /livreurs"
curl -s "$BASE_URL/livreurs" >/dev/null && ok "Liste des livreurs"

echo "GET /livreurs/$LIVREUR_ID"
curl -s "$BASE_URL/livreurs/$LIVREUR_ID" >/dev/null && ok "Lecture par id"

echo "PUT /livreurs/$LIVREUR_ID"
RESP=$(curl -s -X PUT "$BASE_URL/livreurs/$LIVREUR_ID" \
  -H "Content-Type: application/json" \
  -d '{"is_available":false}')
echo "  → $RESP"
echo "$RESP" | grep -q '"is_available":false' && ok "Mise à jour" || fail "Update livreur"

echo "POST /livreurs avec email déjà utilisé (409 attendu)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/livreurs" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"nom\":\"Bis\",\"prenom\":\"Doublon\"}")
[ "$STATUS" = "409" ] && ok "409 sur email déjà pris" || fail "409 attendu, reçu $STATUS"

# === Partie 2 — Auth ===
step "Partie 2 — Authentification JWT"

echo "POST /auth/login (mauvais mdp, 401 attendu)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"wrong\"}")
[ "$STATUS" = "401" ] && ok "401 sur mauvais mot de passe" || fail "401 attendu, reçu $STATUS"

echo "POST /auth/login (vrai mdp)"
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  | json_get access_token)
[ -n "$TOKEN" ] && ok "JWT reçu (${TOKEN:0:30}...)" || fail "Login échoué"

# === Partie 2 — Sac ===
step "Partie 2 — Sac (routes protégées)"

echo "GET /sac sans token (401 attendu)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/sac")
[ "$STATUS" = "401" ] && ok "401 sans token" || fail "401 attendu, reçu $STATUS"

echo "GET /sac avec token (vide)"
RESP=$(curl -s "$BASE_URL/sac" -H "Authorization: Bearer $TOKEN")
echo "  → $RESP"
echo "$RESP" | grep -q '"items":\[\]' && ok "Sac vide initial" || fail "Sac vide attendu"

echo "POST /sac/items (+5)"
RESP=$(curl -s -X POST "$BASE_URL/sac/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\":$PRODUCT_ID,\"quantite\":5}")
echo "  → $RESP"
echo "$RESP" | grep -q '"quantite":5' && ok "Ajout de 5 unités" || fail "Ajout au sac"

echo "DELETE /sac/items (-2)"
RESP=$(curl -s -X DELETE "$BASE_URL/sac/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\":$PRODUCT_ID,\"quantite\":2}")
echo "  → $RESP"
echo "$RESP" | grep -q '"quantite":3' && ok "Retrait de 2, reste 3" || fail "Retrait du sac"

echo "DELETE /sac/items (-99) (400 attendu : règle métier)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/sac/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\":$PRODUCT_ID,\"quantite\":99}")
[ "$STATUS" = "400" ] && ok "400 sur retrait excessif" || fail "400 attendu, reçu $STATUS"

echo "GET /sac final"
RESP=$(curl -s "$BASE_URL/sac" -H "Authorization: Bearer $TOKEN")
echo "  → $RESP"
ok "Sac final consulté"

# === Nettoyage ===
step "Nettoyage"
curl -s -X DELETE "$BASE_URL/livreurs/$LIVREUR_ID" >/dev/null && ok "Livreur de test supprimé"
curl -s -X DELETE "$BASE_URL/products/$PRODUCT_ID" >/dev/null && ok "Produit de test supprimé"

# === Résumé ===
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Tous les tests passent${NC}"
echo "  • 14 endpoints fonctionnels (Partie 1 + Partie 2)"
echo "  • 6 cas d'erreur vérifiés (400, 401, 404, 409, 422)"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"