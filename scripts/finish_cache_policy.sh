#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas
ts="$(date +%Y%m%d_%H%M%S)"

backup() {
  local f="$1"
  if [ -f "$f" ]; then
    cp "$f" "$f.bak.$ts"
  fi
}

mkdir -p tests/architecture scripts

backup tests/architecture/test_cache_only_repos.py
cat > tests/architecture/test_cache_only_repos.py <<'PY'
from pathlib import Path

REPO_FILES = [
    Path("departments/deportes/futbol/repo.py"),
    Path("departments/deportes/basket/repo.py"),
    Path("departments/deportes/tenis/repo.py"),
]

FORBIDDEN = [
    "requests.",
    "httpx.",
    "urllib.",
    "provider_",
    "espn_get(",
    "get_odds(",
    "sportsgameodds",
    "rapidapi",
    "the-odds-api",
]

REQUIRED = [
    "load_sport_day",
]

def test_repos_read_from_json_cache_only():
    for path in REPO_FILES:
        text = path.read_text(encoding="utf-8")
        assert any(x in text for x in REQUIRED), f"{path} no parece leer cache local"
        for bad in FORBIDDEN:
            assert bad not in text, f"{path} contiene acceso prohibido: {bad}"
PY

backup tests/architecture/test_scheduler_policy.py
cat > tests/architecture/test_scheduler_policy.py <<'PY'
from pathlib import Path

def test_shared_cache_scheduler_has_2am_job():
    text = Path("shared/cache_scheduler.py").read_text(encoding="utf-8")
    assert 'TZ = "America/Guayaquil"' in text
    assert 'CronTrigger(hour=2, minute=0, timezone=TZ)' in text
    assert 'id="daily_cache_2am_ec"' in text

def test_repos_never_call_live_apis():
    for rel in [
        "departments/deportes/futbol/repo.py",
        "departments/deportes/basket/repo.py",
        "departments/deportes/tenis/repo.py",
    ]:
        text = Path(rel).read_text(encoding="utf-8")
        forbidden = [
            "requests.",
            "httpx.",
            "urllib.",
            "provider_",
            "espn_get(",
            "get_odds(",
            "sportsgameodds",
            "rapidapi",
            "the-odds-api",
        ]
        for bad in forbidden:
            assert bad not in text, f"{rel} contiene acceso prohibido: {bad}"
PY

backup scripts/audit_cache_policy.sh
cat > scripts/audit_cache_policy.sh <<'SH2'
#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas

echo "=============================="
echo "CACHE POLICY AUDIT"
echo "=============================="

echo
echo "[1] REPOS cache-only"
grep -RniE 'load_sport_day|requests\.|httpx\.|urllib\.|provider_|espn_get|get_odds\(' \
  departments/deportes/futbol/repo.py \
  departments/deportes/basket/repo.py \
  departments/deportes/tenis/repo.py \
  2>/dev/null || true

echo
echo "[2] Scheduler oficial"
grep -nE 'TZ = |CronTrigger|daily_cache_2am_ec|ensure_today_cache_once|build_all_caches' \
  shared/cache_scheduler.py 2>/dev/null || true

echo
echo "[3] Legacy scheduler"
grep -nE 'refresh_tenis|refresh_futbol|refresh_basket|register_example_jobs|add_job' \
  scheduler.py 2>/dev/null || true

echo
echo "CACHE POLICY AUDIT OK"
SH2
chmod +x scripts/audit_cache_policy.sh

pytest tests/architecture/test_cache_only_repos.py -v
pytest tests/architecture/test_scheduler_policy.py -v
bash scripts/audit_cache_policy.sh
