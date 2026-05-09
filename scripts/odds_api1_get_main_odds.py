from datetime import datetime
import json
import requests
import sys

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
HOST = "odds-api1.p.rapidapi.com"
BASE = f"https://{HOST}"

fixture_id = sys.argv[1] if len(sys.argv) > 1 else "id1205138871217578"
bookmakers = sys.argv[2] if len(sys.argv) > 2 else "pinnacle,stake,draftkings"

url = f"{BASE}/fixtures/odds/main"
params = {
    "fixtureIds": fixture_id,
    "bookmakers": bookmakers,
}

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": HOST,
    "Content-Type": "application/json",
}

log_file = f"logs/odds_api1_main_odds_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

def log(line):
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def sample(resp, n=2500):
    t = (resp.text or "").strip()
    return t[:n] if t else "<empty body>"

log(f"TIME_UTC: {datetime.utcnow().isoformat()}Z")
log(f"URL: {url}")
log(f"PARAMS: {json.dumps(params, ensure_ascii=False)}")

r = requests.get(url, headers=headers, params=params, timeout=25)
log(f"STATUS: {r.status_code}")
log(f"CONTENT_TYPE: {r.headers.get('content-type', 'unknown')}")
log("BODY_SAMPLE_START")
log(sample(r))
log("BODY_SAMPLE_END")

try:
    data = r.json()
    if isinstance(data, list):
        log(f"JSON_TYPE: list")
        log(f"JSON_LEN: {len(data)}")
        if data:
            log("JSON_FIRST_ITEM:")
            log(json.dumps(data[0], ensure_ascii=False)[:2000])
    elif isinstance(data, dict):
        log(f"JSON_TYPE: dict")
        log(f"JSON_KEYS: {list(data.keys())[:50]}")
        log("JSON_DICT_SAMPLE:")
        log(json.dumps(data, ensure_ascii=False)[:2000])
except Exception as e:
    log(f"JSON_PARSE_ERROR: {type(e).__name__}: {e}")

log(f"LOG_FILE: {log_file}")
