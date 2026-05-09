from datetime import datetime
import json
import requests

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
HOST = "odds-api1.p.rapidapi.com"
BASE_URL = f"https://{HOST}"

checks = [
    ("sports", f"{BASE_URL}/sports", None),
    ("fixtures_tennis", f"{BASE_URL}/fixtures/today", {"sportId": 12}),
    ("fixtures_soccer", f"{BASE_URL}/fixtures/today", {"sportId": 10}),
    ("fixtures_basketball", f"{BASE_URL}/fixtures/today", {"sportId": 11}),
]

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": HOST,
    "content-type": "application/json",
}

log_file = f"logs/odds_api1_validate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

def log(line):
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def preview(resp):
    text = (resp.text or "").strip()
    return text[:1400] if text else "<empty body>"

log(f"TIME_UTC: {datetime.utcnow().isoformat()}Z")
log(f"LOG_FILE: {log_file}")

for name, url, params in checks:
    log("=" * 70)
    log(f"TEST: {name}")
    log(f"URL: {url}")
    if params:
        log(f"PARAMS: {json.dumps(params, ensure_ascii=False)}")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=25)
        log(f"STATUS: {resp.status_code}")
        log(f"CONTENT_TYPE: {resp.headers.get('content-type', 'unknown')}")
        log("BODY_SAMPLE_START")
        log(preview(resp))
        log("BODY_SAMPLE_END")

        try:
            data = resp.json()
            if isinstance(data, list):
                log("JSON_TYPE: list")
                log(f"JSON_LEN: {len(data)}")
                if data:
                    log("JSON_FIRST_ITEM:")
                    log(json.dumps(data[0], ensure_ascii=False)[:1200])
            elif isinstance(data, dict):
                log("JSON_TYPE: dict")
                log(f"JSON_KEYS: {list(data.keys())[:30]}")
                log("JSON_DICT_SAMPLE:")
                log(json.dumps(data, ensure_ascii=False)[:1200])
            else:
                log(f"JSON_TYPE: {type(data).__name__}")
        except Exception as e:
            log(f"JSON_PARSE_ERROR: {type(e).__name__}: {e}")
    except requests.exceptions.Timeout:
        log("REQUEST_ERROR: Timeout")
    except requests.exceptions.RequestException as e:
        log(f"REQUEST_ERROR: {type(e).__name__}: {e}")

log("DONE")
