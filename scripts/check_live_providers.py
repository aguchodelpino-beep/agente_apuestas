#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import requests

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
TIMEOUT = 20

TARGETS = [
    {
        "name": "odds-api1",
        "base": "https://odds-api1.p.rapidapi.com",
        "checks": [
            "/sports",
            "/fixtures/today?sportId=12",
            "/fixtures/today?sportId=10",
            "/fixtures/today?sportId=11",
        ],
    },
    {
        "name": "1xbet-api",
        "base": "https://1xbet-api.p.rapidapi.com",
        "checks": [
            "/sports",
            "/matches",
        ],
    },
    {
        "name": "premier-league-stats",
        "base": "https://premier-league-stats.p.rapidapi.com",
        "checks": [
            "/fixtures",
        ],
    },
]

LOG_DIR = Path("logs")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_fn(path: Path):
    def log(msg: str) -> None:
        line = str(msg)
        print(line)
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return log


def headers(host: str) -> dict:
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }


def json_type_of(value) -> str:
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    return type(value).__name__


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    run_stamp = stamp()
    log_path = LOG_DIR / f"check_live_providers_{run_stamp}.log"
    log = log_fn(log_path)

    results = []
    log(f"TIME_UTC: {now()}")

    for target in TARGETS:
        base = target["base"]
        name = target["name"]
        host = base.replace("https://", "").replace("http://", "").strip("/")

        log("=" * 80)
        log(f"PROVIDER: {name} -> {base}")

        for check in target["checks"]:
            url = base.rstrip("/") + check
            try:
                response = requests.get(url, headers=headers(host), timeout=TIMEOUT)
                content_type = response.headers.get("content-type", "unknown")
                sample = (response.text or "").strip().replace("\n", " ")[:500]

                try:
                    payload = response.json()
                    json_type = json_type_of(payload)
                except Exception:
                    payload = None
                    json_type = "non-json"

                row = {
                    "provider": name,
                    "url": url,
                    "status": response.status_code,
                    "content_type": content_type,
                    "json_type": json_type,
                    "sample": sample,
                }

            except requests.exceptions.RequestException as e:
                row = {
                    "provider": name,
                    "url": url,
                    "status": None,
                    "content_type": "",
                    "json_type": "error",
                    "sample": f"{type(e).__name__}: {e}",
                }

            results.append(row)
            log(f"STATUS: {row['status']} | JSON_TYPE: {row['json_type']} | URL: {row['url']}")
            log(f"SAMPLE: {row['sample']}")
            log("-" * 80)

    out_path = LOG_DIR / f"check_live_providers_{run_stamp}_results.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    log(f"RESULTS_JSON: {out_path}")
    log(f"LOG_FILE: {log_path}")


if __name__ == "__main__":
    main()
