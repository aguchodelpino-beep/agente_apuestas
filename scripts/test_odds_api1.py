import json
from datetime import datetime
import requests

URL = "https://odds-api1.p.rapidapi.com/sports"
HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPIKEY", "TEST"),
    "x-rapidapi-host": "odds-api1.p.rapidapi.com",
    "Content-Type": "application/json",
}

out_file = f"logs/odds_api1_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"

def write(line: str):
    print(line)
    with open(out_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

write(f"TIME_UTC: {datetime.utcnow().isoformat()}Z")
write(f"URL: {URL}")

try:
    resp = requests.get(URL, headers=HEADERS, timeout=25)
    write(f"STATUS: {resp.status_code}")
    write(f"CONTENT_TYPE: {resp.headers.get('content-type', 'unknown')}")

    body = resp.text.strip()
    write("BODY_SAMPLE_START")
    write(body[:1500] if body else "<empty body>")
    write("BODY_SAMPLE_END")

    try:
        parsed = resp.json()
        if isinstance(parsed, dict):
            write(f"JSON_TYPE: dict")
            write(f"JSON_KEYS: {list(parsed.keys())[:30]}")
        elif isinstance(parsed, list):
            write(f"JSON_TYPE: list")
            write(f"JSON_LEN: {len(parsed)}")
            write("JSON_FIRST_ITEM:")
            write(json.dumps(parsed[0], ensure_ascii=False)[:1000] if parsed else "[]")
        else:
            write(f"JSON_TYPE: {type(parsed).__name__}")
    except Exception as e:
        write(f"JSON_PARSE_ERROR: {type(e).__name__}: {e}")

except requests.exceptions.Timeout as e:
    write(f"REQUEST_ERROR: Timeout: {e}")
except requests.exceptions.RequestException as e:
    write(f"REQUEST_ERROR: {type(e).__name__}: {e}")

write(f"LOG_FILE: {out_file}")
