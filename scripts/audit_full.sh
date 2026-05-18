#!/usr/bin/env bash
# ============================================================
#  AGENTE_APUESTAS — AUDITORÍA COMPLETA
#  Uso: bash scripts/audit_full.sh [--json]
# ============================================================
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

JSON_MODE=0
[[ "${1:-}" == "--json" ]] && JSON_MODE=1

# ── Colores ──────────────────────────────────────────────────
G="\033[0;32m"; Y="\033[0;33m"; R="\033[0;31m"
B="\033[0;34m"; C="\033[0;36m"; W="\033[1;37m"; NC="\033[0m"
ok()   { echo -e "  ${G}✅ $*${NC}"; }
warn() { echo -e "  ${Y}🟡 $*${NC}"; }
fail() { echo -e "  ${R}❌ $*${NC}"; }
info() { echo -e "  ${C}ℹ  $*${NC}"; }
hdr()  { echo -e "\n${W}══════════════════════════════════════════════${NC}"; \
          echo -e "${W}  $*${NC}"; \
          echo -e "${W}══════════════════════════════════════════════${NC}"; }
sub()  { echo -e "\n${B}── $* ──${NC}"; }

# ── Contadores globales ───────────────────────────────────────
TOTAL_OK=0; TOTAL_WARN=0; TOTAL_FAIL=0
PENDING_ITEMS=()
DONE_ITEMS=()

check_file() {
    local label="$1" path="$2" required="${3:-1}"
    if [[ -f "$path" ]]; then
        local lines
        lines=$(wc -l < "$path" 2>/dev/null || echo 0)
        if (( lines < 5 )); then
            warn "$label  ($path — solo $lines líneas, puede estar vacío)"
            ((TOTAL_WARN++))
            PENDING_ITEMS+=("STUB: $label")
        else
            ok "$label  ($lines líneas)"
            ((TOTAL_OK++))
            DONE_ITEMS+=("$label")
        fi
    else
        if (( required )); then
            fail "$label  → FALTA: $path"
            ((TOTAL_FAIL++))
            PENDING_ITEMS+=("FALTA: $label ($path)")
        else
            warn "$label  → opcional, no existe aún"
            ((TOTAL_WARN++))
            PENDING_ITEMS+=("OPCIONAL FALTANTE: $label")
        fi
    fi
}

check_symbol() {
    local label="$1" path="$2" symbol="$3"
    if [[ -f "$path" ]] && grep -q "$symbol" "$path" 2>/dev/null; then
        ok "$label  (símbolo: $symbol)"
        ((TOTAL_OK++))
        DONE_ITEMS+=("$label")
    else
        fail "$label  → símbolo '$symbol' no encontrado en $path"
        ((TOTAL_FAIL++))
        PENDING_ITEMS+=("SÍMBOLO FALTANTE: $symbol en $path")
    fi
}

# ════════════════════════════════════════════════════════════
hdr "1. ENTORNO"
# ════════════════════════════════════════════════════════════

sub "Python & venv"
if [[ -d "venv" ]]; then
    ok "venv existe"
    ((TOTAL_OK++))
else
    fail "venv no encontrado"
    ((TOTAL_FAIL++))
fi

PY=$(python3 --version 2>&1 || true)
info "Python: $PY"

sub "Dependencias clave"
for pkg in pytest requests sqlite3; do
    if python3 -c "import $pkg" 2>/dev/null; then
        ok "$pkg importable"
        ((TOTAL_OK++))
    else
        fail "$pkg NO disponible"
        ((TOTAL_FAIL++))
        PENDING_ITEMS+=("pip install $pkg")
    fi
done

sub ".env / config"
if [[ -f ".env" ]]; then
    KEYS=$(grep -c "=" .env 2>/dev/null || echo 0)
    ok ".env presente ($KEYS variables)"
    ((TOTAL_OK++))
else
    fail ".env no existe"
    ((TOTAL_FAIL++))
    PENDING_ITEMS+=("Crear .env con API keys")
fi

# ════════════════════════════════════════════════════════════
hdr "2. CORE"
# ════════════════════════════════════════════════════════════

check_file "core/config.py"           "core/config.py"
check_file "core/health.py"           "core/health.py"
check_file "core/logging.py"          "core/logging.py"        0
check_file "main.py"                  "main.py"
check_file "telegrambot.py"           "telegrambot.py"

# ════════════════════════════════════════════════════════════
hdr "3. SHARED"
# ════════════════════════════════════════════════════════════

check_file "shared/cache.py"                  "shared/cache.py"
check_file "shared/validators.py"             "shared/validators.py"
check_file "shared/datetime_utils.py"         "shared/datetime_utils.py"
check_file "shared/odds.py"                   "shared/odds.py"
check_file "shared/bets_history_repo.py"      "shared/bets_history_repo.py"
check_file "shared/bets_history_schema.sql"   "shared/bets_history_schema.sql"
check_symbol "bets_history: record_bet"       "shared/bets_history_repo.py"  "def record_bet"
check_symbol "bets_history: settle_bet"       "shared/bets_history_repo.py"  "def settle_bet"
check_symbol "bets_history: summarize_overall" "shared/bets_history_repo.py" "def summarize_overall"
check_symbol "bets_history: summarize_by"     "shared/bets_history_repo.py"  "def summarize_by"
check_symbol "bets_history: list_bets"        "shared/bets_history_repo.py"  "def list_bets"

# ════════════════════════════════════════════════════════════
hdr "4. ANALITICA — MODELOS Y MOTOR KELLY"
# ════════════════════════════════════════════════════════════

check_file  "analitica/models.py"             "departments/analitica/models.py"
check_symbol "KellyDecision dataclass"        "departments/analitica/models.py"     "class KellyDecision"
check_symbol "BetOpportunity dataclass"       "departments/analitica/models.py"     "class BetOpportunity"
check_symbol "KellyConfig dataclass"          "departments/analitica/models.py"     "class KellyConfig"
check_symbol "KellyDecision.edge_pct"         "departments/analitica/models.py"     "edge_pct"
check_symbol "KellyDecision.implied_prob"     "departments/analitica/models.py"     "implied_prob"
check_file  "analitica/service.py"            "departments/analitica/service.py"
check_symbol "evaluate_kelly config=None"     "departments/analitica/service.py"    "config: KellyConfig | None = None"
check_symbol "kelly_to_bet_record"            "departments/analitica/service.py"    "def kelly_to_bet_record"

sub "Modelos avanzados (Fase 3)"
check_file "Poisson fútbol"        "departments/analitica/modelos/poisson_futbol.py"    0
check_file "Elo + surface tenis"   "departments/analitica/modelos/elo_surface_tenis.py" 0
check_file "Ratings basket"        "departments/analitica/modelos/ratings_basket.py"    0
check_file "Monte Carlo"           "departments/analitica/modelos/monte_carlo.py"       0
check_file "Ensemble engine"       "departments/analitica/modelos/ensemble.py"          0

sub "Riesgo (Fase 4)"
check_symbol "fractional Kelly configurable"  "departments/analitica/service.py"    "fractional_kelly"
check_file "Exposure engine"       "departments/analitica/risk/exposure.py"           0
check_file "Portfolio risk"        "departments/analitica/risk/portfolio.py"          0
check_symbol "Calibration/Brier"   "departments/analitica/service.py"                "brier"    0 2>/dev/null || \
    { fail "Calibration/Brier → NO implementado"; ((TOTAL_FAIL++)); PENDING_ITEMS+=("Fase 4: confidence calibration Brier/log_loss"); }

# ════════════════════════════════════════════════════════════
hdr "5. DEPORTES — TENIS"
# ════════════════════════════════════════════════════════════

check_file "tenis/repo.py"         "departments/deportes/tenis/repo.py"
check_file "tenis/models.py"       "departments/deportes/tenis/models.py"
check_file "tenis/handlers.py"     "departments/deportes/tenis/handlers.py"
check_file "tenis/service.py"      "departments/deportes/tenis/service.py"
check_file "tenis/utils.py"        "departments/deportes/tenis/utils.py"        0
check_file "analitica/tenis/service.py" "departments/analitica/deportes/tenis/service.py"
check_symbol "tenis service: NO BET"    "departments/analitica/deportes/tenis/service.py" "NO BET"
check_symbol "tenis service: best_edge" "departments/analitica/deportes/tenis/service.py" "best_edge"

# ════════════════════════════════════════════════════════════
hdr "6. DEPORTES — FÚTBOL"
# ════════════════════════════════════════════════════════════

check_file "futbol/repo.py"        "departments/deportes/futbol/repo.py"
check_file "futbol/models.py"      "departments/deportes/futbol/models.py"       0
check_file "futbol/handlers.py"    "departments/deportes/futbol/handlers.py"     0
check_file "futbol/service.py"     "departments/deportes/futbol/service.py"      0
check_file "analitica/futbol/service.py" "departments/analitica/deportes/futbol/service.py"
check_symbol "futbol service: NO BET"   "departments/analitica/deportes/futbol/service.py" "NO BET"

# ════════════════════════════════════════════════════════════
hdr "7. DEPORTES — BASKET"
# ════════════════════════════════════════════════════════════

check_file "basket/repo.py"        "departments/deportes/basket/repo.py"
check_file "basket/models.py"      "departments/deportes/basket/models.py"       0
check_file "basket/handlers.py"    "departments/deportes/basket/handlers.py"     0
check_file "basket/service.py"     "departments/deportes/basket/service.py"      0
check_file "analitica/basket/service.py" "departments/analitica/deportes/basket/service.py" 0

# ════════════════════════════════════════════════════════════
hdr "8. VISUALES"
# ════════════════════════════════════════════════════════════

check_file "visuales/cards.py"         "departments/visuales/cards.py"
check_file "visuales/formatter.py"     "departments/visuales/formatter.py"
check_file "visuales/markdown.py"      "departments/visuales/markdown.py"
check_file "visuales/telegram_ui.py"   "departments/visuales/telegram_ui.py"
check_file "visuales/inline_keyboards.py" "departments/visuales/inline_keyboards.py" 0

# ════════════════════════════════════════════════════════════
hdr "9. SCHEDULER"
# ════════════════════════════════════════════════════════════

check_file "scheduler/scheduler.py"    "departments/scheduler/scheduler.py"      0
check_file "scripts/refresh_once.py"   "scripts/refresh_once.py"                 0
check_file "scripts/check_stale_data.py" "scripts/check_stale_data.py"           0

# ════════════════════════════════════════════════════════════
hdr "10. ANALYTICS (Fase 5)"
# ════════════════════════════════════════════════════════════

check_file "analytics/roi_report.py"       "departments/analitica/analytics/roi_report.py"    0
check_file "analytics/clv_dashboard.py"    "departments/analitica/analytics/clv_dashboard.py" 0
check_file "analytics/drawdown.py"         "departments/analitica/analytics/drawdown.py"       0
check_file "analytics/ab_testing.py"       "departments/analitica/analytics/ab_testing.py"     0
check_file "analytics/calibration.py"      "departments/analitica/analytics/calibration.py"    0

# ════════════════════════════════════════════════════════════
hdr "11. PRODUCCIÓN (Fase 7)"
# ════════════════════════════════════════════════════════════

check_file "Dockerfile"            "Dockerfile"                0
check_file "docker-compose.yml"    "docker-compose.yml"        0
check_file "logging JSON"          "core/logging.py"           0
# Backoff/circuit breaker en cualquier módulo
if grep -rq "backoff\|circuit.breaker\|CircuitBreaker" departments/ 2>/dev/null; then
    ok "Retries/backoff encontrado en departments/"
    ((TOTAL_OK++))
    DONE_ITEMS+=("Retries con backoff")
else
    fail "Retries con backoff → NO implementado"
    ((TOTAL_FAIL++))
    PENDING_ITEMS+=("Fase 7: retries con backoff/circuit breaker")
fi
# Secrets manager
if grep -rq "secrets\|SecretManager\|vault" core/ shared/ 2>/dev/null; then
    ok "Secrets manager detectado"
    ((TOTAL_OK++))
else
    warn "Secrets manager → usando .env plano"
    ((TOTAL_WARN++))
    PENDING_ITEMS+=("Fase 7: secrets manager")
fi

# ════════════════════════════════════════════════════════════
hdr "12. TESTS"
# ════════════════════════════════════════════════════════════

sub "Cobertura de archivos de test"
TEST_FILES=$(find tests/ -name "test_*.py" 2>/dev/null | wc -l)
info "Archivos de test encontrados: $TEST_FILES"

sub "Ejecutando pytest..."
if python -m pytest tests/ -q --tb=no 2>/dev/null; then
    PYTEST_OUT=$(python -m pytest tests/ -q --tb=no 2>&1 | tail -3)
    ok "pytest: $PYTEST_OUT"
    ((TOTAL_OK++))
    DONE_ITEMS+=("Suite de tests pasando")
else
    PYTEST_OUT=$(python -m pytest tests/ -q --tb=no 2>&1 | tail -3)
    fail "pytest: $PYTEST_OUT"
    ((TOTAL_FAIL++))
    PENDING_ITEMS+=("Tests fallando — ver pytest -v")
fi

# xfail markers que ya pasan (deben limpiarse)
XFAIL_FILES=$(grep -rl "pytest.mark.xfail" tests/ 2>/dev/null | tr '\n' ' ')
if [[ -n "$XFAIL_FILES" ]]; then
    warn "xfail markers activos: $XFAIL_FILES"
    ((TOTAL_WARN++))
    PENDING_ITEMS+=("Limpiar xfail markers en: $XFAIL_FILES")
fi

# ════════════════════════════════════════════════════════════
hdr "13. DATOS"
# ════════════════════════════════════════════════════════════

sub "Archivos JSON de fixtures"
for sport in tenis futbol basket; do
    JSON=$(find data/ -name "*.json" -path "*$sport*" 2>/dev/null | head -1)
    if [[ -n "$JSON" ]]; then
        AGE_MIN=$(( ($(date +%s) - $(stat -c %Y "$JSON" 2>/dev/null || echo 0)) / 60 ))
        if (( AGE_MIN < 120 )); then
            ok "$sport: $JSON (${AGE_MIN}min)"
        else
            warn "$sport: $JSON (${AGE_MIN}min — puede estar obsoleto)"
        fi
    else
        fail "$sport: sin JSON de fixtures en data/"
        ((TOTAL_FAIL++))
        PENDING_ITEMS+=("Refrescar datos: python scripts/refresh_once.py $sport")
    fi
done

sub "Base de datos bets_history"
DB_PATH=$(find data/ -name "bets_history.sqlite" 2>/dev/null | head -1)
if [[ -n "$DB_PATH" ]]; then
    ROWS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM bets;" 2>/dev/null || echo "0")
    ok "bets_history.sqlite — $ROWS apuestas registradas"
    ((TOTAL_OK++))
else
    warn "bets_history.sqlite no existe aún (se crea al primer record_bet)"
    ((TOTAL_WARN++))
fi

# ════════════════════════════════════════════════════════════
hdr "RESUMEN FINAL"
# ════════════════════════════════════════════════════════════

TOTAL=$((TOTAL_OK + TOTAL_WARN + TOTAL_FAIL))
PCT_OK=$(( TOTAL > 0 ? TOTAL_OK * 100 / TOTAL : 0 ))

echo ""
echo -e "  ${G}✅ OK:       $TOTAL_OK${NC}"
echo -e "  ${Y}🟡 WARNINGS: $TOTAL_WARN${NC}"
echo -e "  ${R}❌ FALTAN:   $TOTAL_FAIL${NC}"
echo -e "  ${W}   TOTAL:    $TOTAL  ($PCT_OK% listo)${NC}"

if (( ${#PENDING_ITEMS[@]} > 0 )); then
    echo ""
    echo -e "${R}── PENDIENTES ──────────────────────────────────────${NC}"
    for item in "${PENDING_ITEMS[@]}"; do
        echo -e "  ${R}▸ $item${NC}"
    done
fi

echo ""
echo -e "${G}── COMPLETADO ──────────────────────────────────────${NC}"
for item in "${DONE_ITEMS[@]}"; do
    echo -e "  ${G}▸ $item${NC}"
done

# ── JSON output opcional ─────────────────────────────────
if (( JSON_MODE )); then
    python3 - << PYEOF
import json, sys
data = {
    "ok": $TOTAL_OK,
    "warn": $TOTAL_WARN,
    "fail": $TOTAL_FAIL,
    "total": $TOTAL,
    "pct_ready": $PCT_OK,
    "pending": $(python3 -c "import json; print(json.dumps([$(printf '"%s",' "${PENDING_ITEMS[@]}" | sed 's/,$//')]  if True else []))"),
}
print(json.dumps(data, indent=2, ensure_ascii=False))
PYEOF
fi

echo ""
echo -e "${W}PRÓXIMOS PASOS SUGERIDOS:${NC}"
echo -e "  1. bash scripts/run_audit.sh          # auditoría de módulos internos"
echo -e "  2. python scripts/refresh_once.py all  # refrescar datos"
echo -e "  3. python -m pytest tests/ -v          # suite completa"
echo ""
