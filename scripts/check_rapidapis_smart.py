#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import requests

API_KEY_DEFAULT = os.getenv("RAPIDAPIKEY", "TEST")
TIMEOUT = 20

APIS = {
    "odds-api1": "https://odds-api1.p.rapidapi.com",
    "sportsbook-api2": "https://sportsbook-api2.p.rapidapi.com",
    "today-football-prediction": "https://today-football-prediction.p.rapidapi.com",
    "bet365-api-inplay": "https://bet365-api-inplay.p.rapidapi.com",
    "bet365data": "https://bet365data.p.rapidapi.com",
    "betfair": "https://betfair-sports-casino-live-tv-result-odds.p.rapidapi.com",
    "ultimate-tennis1": "https://ultimate-tennis1.p.rapidapi.com",
    "sports-live-scores": "https://sports-live-scores.p.rapidapi.com",
    "tennis-api-atp-wta-itf": "https://tennis-api-atp-wta-itf.p.rapidapi.com",
    "allsportsapi2": "https://allsportsapi2.p.rapidapi.com",
    "nba-api-free-data": "https://nba-api-free-data.p.rapidapi.com",
    "1xbet-api": "https://1xbet-api.p.rapidapi.com",
    "basketball-highlights-api": "https://basketball-highlights-api.p.rapidapi.com",
    "nba-injury-data": "https://nba-injury-data.p.rapidapi.com",
    "free-football-api-data": "https://free-football-api-data.p.rapidapi.com",
    "premier-league-stats": "https://premier-league-stats.p.rapidapi.com",
    "propsports": "https://propsports.p.rapidapi.com",
}

CANDIDATE_PATHS = [
    "/",
    "/sports",
    "/matches",
    "/fixtures/today",
    "/fixtures",
    "/live",
    "/odds",
    "/events",
    "/games",
    "/status",
]

LOG_DIR = Path("logs")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def log_fn(path):
    def log(msg):
        line = str(msg)
        print(line)
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return log


def headers(host, api_key):
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }


def classify(status, text):
    if isinstance(status, int) and status < 400:
        return "ok"
    if status == 401:
        return "auth_or_plan"
    if status == 403:
        return "forbidden"
    if status == 429:
        return "rate_limit"
    if status == 400:
        return "bad_request"
    if status == 404:
        return "not_found"
    return "other"


def short_text(resp_text, n=300):
    t = (resp_text or "").strip().replace("\n", " ")
    return t[:n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=API_KEY_DEFAULT)
    parser.add_argument("--paths", default=",".join(CANDIDATE_PATHS))
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"check_rapidapis_smart_{stamp()}.log"
    log = log_fn(log_path)

    paths = [p.strip() for p in args.paths.split(",") if p.strip()]
    results = []

    log(f"TIME_UTC: {utc_now()}")
    log(f"PATHS: {paths}")
    log("=" * 100)

    for name, base in APIS.items():
        host = base.replace("https://", "").replace("http://", "").strip("/")
        log(f"API: {name} -> {base}")
        best = None

        for path in paths:
            url = base.rstrip("/") + path
            try:
                r = requests.get(url, headers=headers(host, args.api_key), timeout=TIMEOUT)
                ct = r.headers.get("content-type", "unknown")
                txt = short_text(r.text)
                try:
                    j = r.json()
                    jt = f"list[{len(j)}]" if isinstance(j, list) else f"dict[{len(j.keys())}]" if isinstance(j, dict) else type(j).__name__
                except Exception:
                    jt = "non-json"
                cls = classify(r.status_code, txt)
                row = {
                    "api": name,
                    "base_url": base,
                    "path": path,
                    "url": url,
                    "status": r.status_code,
                    "content_type": ct,
                    "json_type": jt,
                    "class": cls,
                    "sample": txt,
                }
            except requests.exceptions.RequestException as e:
                row = {
                    "api": name,
                    "base_url": base,
                    "path": path,
                    "url": url,
                    "status": None,
                    "content_type": "",
                    "json_type": "",
                    "class": "error",
                    "sample": f"{type(e).__name__}: {e}",
                }

            results.append(row)
            if best is None and row["class"] == "ok":
                best = row

            log(f"  {path} -> {row['status']} | {row['class']} | {row['json_type']} | {row['sample']}")
        log("-" * 100)

    out_path = LOG_DIR / f"check_rapidapis_smart_{stamp()}_results.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    summary = {}
    for r in results:
        summary.setdefault(r["api"], {"ok": 0, "total": 0, "best": None})
        summary[r["api"]]["total"] += 1
        if r["class"] == "ok":
            summary[r["api"]]["ok"] += 1
            if summary[r["api"]]["best"] is None:
                summary[r["api"]]["best"] = r["path"]

    log("=" * 100)
    log(f"RESULTS_JSON: {out_path}")
    log("SUMMARY:")
    log(json.dumps(summary, ensure_ascii=False, indent=2))
    log(f"LOG_FILE: {log_path}")


if __name__ == "__main__":
    main()
