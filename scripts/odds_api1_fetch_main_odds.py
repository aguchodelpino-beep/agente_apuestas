#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import sys
import requests

API_KEY = os.getenv("RAPIDAPIKEY", "TEST")
HOST = "odds-api1.p.rapidapi.com"
BASE_URL = f"https://{HOST}"
DEFAULT_BOOKMAKERS = "pinnacle,stake,draftkings"

LOGS_DIR = Path("logs")
RAW_DIR = Path("data/raw")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def ensure_dirs() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def make_logger(log_path: Path):
    def log(msg: str) -> None:
        line = str(msg)
        print(line)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trae main odds desde odds-api1.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture-id", help="Ejemplo: id1205138871217578")
    group.add_argument("--tournament-id", help="Ejemplo: 51388")
    parser.add_argument(
        "--bookmakers",
        default=DEFAULT_BOOKMAKERS,
        help=f"CSV de bookmakers. Default: {DEFAULT_BOOKMAKERS}",
    )
    parser.add_argument("--out", default=None, help="Ruta opcional de salida JSON.")
    parser.add_argument("--timeout", type=int, default=25, help="Timeout HTTP en segundos.")
    return parser.parse_args()


def build_params(args: argparse.Namespace) -> dict:
    params = {"bookmakers": args.bookmakers}
    if args.fixture_id:
        params["fixtureIds"] = args.fixture_id
    else:
        params["tournamentId"] = args.tournament_id
    return params


def build_headers() -> dict:
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": HOST,
        "Content-Type": "application/json",
    }


def summarize_payload(data) -> dict:
    summary = {"json_type": type(data).__name__, "items": 0, "fixtures": []}
    if not isinstance(data, list):
        return summary

    summary["items"] = len(data)
    for item in data[:10]:
        summary["fixtures"].append(
            {
                "fixtureId": item.get("fixtureId"),
                "sport": (item.get("sport") or {}).get("sportName"),
                "tournament": (item.get("tournament") or {}).get("tournamentName"),
                "status": (item.get("status") or {}).get("statusName"),
                "bookmakers_present": sorted(list((item.get("odds") or {}).keys())),
            }
        )
    return summary


def main() -> int:
    ensure_dirs()
    args = parse_args()

    stamp = utc_stamp()
    log_path = LOGS_DIR / f"odds_api1_fetch_main_odds_{stamp}.log"
    log = make_logger(log_path)

    url = f"{BASE_URL}/fixtures/odds/main"
    params = build_params(args)
    headers = build_headers()

    if args.out:
        out_path = Path(args.out)
    else:
        suffix = args.fixture_id if args.fixture_id else f"tournament_{args.tournament_id}"
        out_path = RAW_DIR / f"odds_api1_main_odds_{suffix}_{stamp}.json"

    log(f"TIME_UTC: {utc_now_iso()}")
    log(f"URL: {url}")
    log(f"PARAMS: {json.dumps(params, ensure_ascii=False)}")
    log(f"OUT_FILE: {out_path}")
    log(f"LOG_FILE: {log_path}")

    response = None
    try:
        response = requests.get(url, headers=headers, params=params, timeout=args.timeout)
        log(f"STATUS: {response.status_code}")
        log(f"CONTENT_TYPE: {response.headers.get('content-type', 'unknown')}")
        log("BODY_SAMPLE_START")
        log((response.text or "").strip()[:2500] or "<empty body>")
        log("BODY_SAMPLE_END")

        response.raise_for_status()
        data = response.json()

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        log("SUMMARY_START")
        log(json.dumps(summarize_payload(data), ensure_ascii=False, indent=2))
        log("SUMMARY_END")
        log("RESULT: OK")
        return 0

    except requests.exceptions.HTTPError as e:
        log(f"HTTP_ERROR: {e}")
        if response is not None:
            try:
                log(f"ERROR_JSON: {json.dumps(response.json(), ensure_ascii=False)}")
            except Exception:
                pass
        return 2
    except requests.exceptions.Timeout as e:
        log(f"TIMEOUT_ERROR: {e}")
        return 3
    except requests.exceptions.RequestException as e:
        log(f"REQUEST_ERROR: {e}")
        return 4
    except Exception as e:
        log(f"UNEXPECTED_ERROR: {type(e).__name__}: {e}")
        return 5


if __name__ == "__main__":
    sys.exit(main())
