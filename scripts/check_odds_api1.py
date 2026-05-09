from datetime import datetime
import json
import requests

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
HOST = "odds-api1.p.rapidapi.com"
BASE = f"https://{HOST}"

tests = [
    {"name": "sports", "url": f"{BASE}/sports", "params": None},
    {"name": "fixtures_today_tennis", "url": f"{BASE}/fixtures/today", "params": {"sportId": 12}},
    {"name": "fixtures_today_soccer", "url": f"{BASE}/fixtures/today", "params": {"sportId": 10}},
    {"name": "fixtures_today_basketball", "url": f"{BASE}/fixtures/today", "params": {"sportId": 11}},
]

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": HOST,
    "Content-Type": "application/json",
}

out = f"logs/odds_api1_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

def log(line):
    print(line)
    with open(out, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def sample_text(resp):
    txt = (resp.text or "").strip()
    return txt[:1500] if txt else "<empty body>"

log(f"TIME_UTC: {datetime.utcnow().isoformat()}Z")
log(f"OUT_FILE: {out}")

for t in tests:
    log("=" * 60)
    log(f"TEST: {t['name']}")
    log(f"URL: {t['url']}")
    if t["params"]:
        log(f"PARAMS: {json.dumps(t['params'], ensure_ascii=False)}")
    try:
        resp = requests.get(t["url"], headers=headers, params=t["params"], timeout=25)
        log(f"STATUS: {resp.status_code}")
        log(f"CONTENT_TYPE: {resp.headers.get('content-type', 'unknown')}")
        log("BODY_SAMPLE_START")
        log(sample_text(resp))
        log("BODY_SAMPLE_END")
        try:
            data = resp.json()
            if isinstance(data, list):
                log(f"JSON_TYPE: list")
                log(f"JSON_LEN: {len(data)}")
                if data:
                    log("JSON_FIRST_ITEM:")
                    log(json.dumps(data[0], ensure_ascii=False)[:1000])
            elif isinstance(data, dict):
                log(f"JSON_TYPE: dict")
                log(f"JSON_KEYS: {list(data.keys())[:30]}")
                log("JSON_DICT_SAMPLE:")
                log(json.dumps(data, ensure_ascii=False)[:1000])
            else:
                log(f"JSON_TYPE: {type(data).__name__}")
        except Exception as e:
            log(f"JSON_PARSE_ERROR: {type(e).__name__}: {e}")
    except requests.exceptions.Timeout:
        log("REQUEST_ERROR: Timeout")
    except requests.exceptions.RequestException as e:
        log(f"REQUEST_ERROR: {type(e).__name__}: {e}")

log(f"LOG_FILE: {out}")
