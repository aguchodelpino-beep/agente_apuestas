#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import requests

API_KEY_DEFAULT = os.getenv("RAPIDAPIKEY", "TEST")
TIMEOUT = 20

APIS = [
    "https://odds-api1.p.rapidapi.com",
    "https://sportsbook-api2.p.rapidapi.com",
    "https://today-football-prediction.p.rapidapi.com",
    "https://bet365-api-inplay.p.rapidapi.com",
    "https://bet365data.p.rapidapi.com",
    "https://betfair-sports-casino-live-tv-result-odds.p.rapidapi.com",
    "https://ultimate-tennis1.p.rapidapi.com",
    "https://sports-live-scores.p.rapidapi.com",
    "https://tennis-api-atp-wta-itf.p.rapidapi.com",
    "https://allsportsapi2.p.rapidapi.com",
    "https://nba-api-free-data.p.rapidapi.com",
    "https://1xbet-api.p.rapidapi.com",
    "https://basketball-highlights-api.p.rapidapi.com",
    "https://nba-injury-data.p.rapidapi.com",
    "https://free-football-api-data.p.rapidapi.com",
    "https://premier-league-stats.p.rapidapi.com",
    "https://propsports.p.rapidapi.com",
]

DEFAULT_PATHS = [
    "/",
    "/sports",
    "/fixtures/today",
    "/live",
    "/odds",
    "/matches",
    "/games",
    "/events",
    "/status",
]

LOG_DIR = Path("logs")


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def make_log_file():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / f"check_rapidapis_{utc_stamp()}.log"


def log_fn(log_path):
    def log(msg):
        line = str(msg)
        print(line)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return log


def build_headers(host, api_key):
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }


def try_request(base_url, path, api_key, log):
    url = base_url.rstrip("/") + path
    host = base_url.replace("https://", "").replace("http://", "").strip("/")
    headers = build_headers(host, api_key)
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        ct = r.headers.get("content-type", "unknown")
        sample = (r.text or "").strip()[:700]
        try:
            data = r.json()
            if isinstance(data, list):
                jt = f"list[{len(data)}]"
            elif isinstance(data, dict):
                jt = f"dict[{len(data.keys())}]"
            else:
                jt = type(data).__name__
        except Exception:
            jt = "non-json"
        return {
            "url": url,
            "status": r.status_code,
            "content_type": ct,
            "json_type": jt,
            "sample": sample,
        }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "status": "ERROR",
            "content_type": "",
            "json_type": "",
            "sample": f"{type(e).__name__}: {e}",
        }


def main():
    parser = argparse.ArgumentParser(description="Prueba múltiples RapidAPI con una sola key.")
    parser.add_argument("--api-key", default=API_KEY_DEFAULT)
    parser.add_argument("--paths", default=",".join(DEFAULT_PATHS))
    args = parser.parse_args()

    log_path = make_log_file()
    log = log_fn(log_path)

    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    results = []

    log(f"TIME_UTC: {utc_now()}")
    log(f"API_KEY: {'SET' if args.api_key else 'MISSING'}")
    log(f"PATHS: {paths}")
    log("=" * 100)

    for base in APIS:
        host = base.replace("https://", "").replace("http://", "").strip("/")
        log(f"API: {base}")
        for path in paths:
            res = try_request(base, path, args.api_key, log)
            results.append({"api": base, **res})
            log(f"  PATH: {path}")
            log(f"  STATUS: {res['status']}")
            if res["content_type"]:
                log(f"  CONTENT_TYPE: {res['content_type']}")
            if res["json_type"]:
                log(f"  JSON_TYPE: {res['json_type']}")
            if res["sample"]:
                log(f"  SAMPLE: {res['sample']}")
            log("-" * 60)
        log("=" * 100)

    out_path = Path("logs") / f"check_rapidapis_{utc_stamp()}_results.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if isinstance(r["status"], int) and r["status"] < 400)
    total = len(results)
    log(f"RESULTS_JSON: {out_path}")
    log(f"OK: {ok}/{total}")
    log(f"LOG_FILE: {log_path}")


if __name__ == "__main__":
    main()
