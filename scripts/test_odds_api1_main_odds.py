from datetime import datetime
import requests
import json

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
HOST = "odds-api1.p.rapidapi.com"
BASE = f"https://{HOST}"

params = {
    "bookmakers": "pinnacle,stake,draftkings",
    "sportId": 12
}

url = f"{BASE}/fixtures/odds/main"
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

log(f"TIME_UTC: {datetime.utcnow().isoformat()}Z")
log(f"URL: {url}")
log(f"PARAMS: {json.dumps(params, ensure_ascii=False)}")

try:
    r = requests.get(url, headers=headers, params=params, timeout=25)
    log(f"STATUS: {r.status_code}")
    log(f"CONTENT_TYPE: {r.headers.get('content-type', 'unknown')}")
    body = (r.text or "").strip()
    log("BODY_SAMPLE_START")
    log(body[:2000] if body else "<empty body>")
    log("BODY_SAMPLE_END")
    try:
        data = r.json()
        if isinstance(data, list):
            log(f"JSON_TYPE: list")
            log(f"JSON_LEN: {len(data)}")
            if data:
                log("JSON_FIRST_ITEM:")
                log(json.dumps(data[0], ensure_ascii=False)[:1200])
        elif isinstance(data, dict):
            log(f"JSON_TYPE: dict")
            log(f"JSON_KEYS: {list(data.keys())[:40]}")
            log("JSON_DICT_SAMPLE:")
            log(json.dumps(data, ensure_ascii=False)[:1200])
    except Exception as e:
        log(f"JSON_PARSE_ERROR: {type(e).__name__}: {e}")
except requests.exceptions.RequestException as e:
    log(f"REQUEST_ERROR: {type(e).__name__}: {e}")

log(f"LOG_FILE: {log_file}")
