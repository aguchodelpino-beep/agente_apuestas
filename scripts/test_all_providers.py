#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import requests
from core.config import Config

OUT = Path("cachediario/providers_audit_report.json")
TIMEOUT = 20


def try_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"raw_text": resp.text[:300]}


def hit(name, method, url, headers=None, params=None):
    try:
        r = requests.request(
            method,
            url,
            headers=headers or {},
            params=params or {},
            timeout=TIMEOUT,
        )
        data = try_json(r)
        return {
            "name": name,
            "status_code": r.status_code,
            "url": r.url,
            "ok": r.status_code == 200,
            "top_keys": list(data.keys())[:10] if isinstance(data, dict) else [],
        }
    except Exception as e:
        return {
            "name": name,
            "status_code": None,
            "url": url,
            "ok": False,
            "error": str(e),
        }


def main():
    detected = {
        "APISPORTSKEY": bool(getattr(Config, "APISPORTSKEY", "")),
        "FOOTBALLDATAKEY": bool(getattr(Config, "FOOTBALLDATAKEY", "")),
        "SPORTSGAMEODDSKEY": bool(getattr(Config, "SPORTSGAMEODDSKEY", "")),
        "PINNACLEENCODEDAUTH": bool(getattr(Config, "PINNACLEENCODEDAUTH", "")),
        "RAPIDAPIKEY": bool(getattr(Config, "RAPIDAPIKEY", "")),
        "ODDSAPIKEYS_count": len(getattr(Config, "ODDSAPIKEYS", []) or []),
    }

    print("=== CONFIG DETECTION ===")
    for k, v in detected.items():
        print(k, v)

    results = []

    if detected["APISPORTSKEY"]:
        h = {"x-apisports-key": Config.APISPORTSKEY}
        results.append(hit("apisports_status", "GET", "https://v3.football.api-sports.io/status", headers=h))
        results.append(hit("apisports_leagues_england", "GET", "https://v3.football.api-sports.io/leagues", headers=h, params={"country": "England"}))

    if detected["FOOTBALLDATAKEY"]:
        h = {"X-Auth-Token": Config.FOOTBALLDATAKEY}
        results.append(hit("footballdata_competitions", "GET", "https://api.football-data.org/v4/competitions", headers=h))
        results.append(hit("footballdata_pl_matches", "GET", "https://api.football-data.org/v4/competitions/PL/matches", headers=h))

    if detected["SPORTSGAMEODDSKEY"]:
        h = {"x-api-key": Config.SPORTSGAMEODDSKEY, "Accept": "application/json"}
        results.append(hit("sgo_sports", "GET", "https://api.sportsgameodds.com/v1/sports", headers=h))
        results.append(hit("sgo_leagues", "GET", "https://api.sportsgameodds.com/v1/leagues", headers=h))
        results.append(hit("sgo_bookmakers", "GET", "https://api.sportsgameodds.com/v1/bookmakers", headers=h))

    if detected["PINNACLEENCODEDAUTH"]:
        h = {"Authorization": f"Basic {Config.PINNACLEENCODEDAUTH}", "Accept": "application/json"}
        results.append(hit("pinnacle_test", "GET", "https://guest.api.arcadia.pinnacle.com/0.1/sports", headers=h))

    if detected["RAPIDAPIKEY"]:
        targets = [
            ("rapid_nba_api_free_data", "https://nba-api-free-data.p.rapidapi.com", "nba-api-free-data.p.rapidapi.com"),
            ("rapid_ultimate_tennis1", "https://ultimate-tennis1.p.rapidapi.com/api/v1/players", "ultimate-tennis1.p.rapidapi.com"),
            ("rapid_tennis_api_atp_wta_itf", "https://tennis-api-atp-wta-itf.p.rapidapi.com/atp", "tennis-api-atp-wta-itf.p.rapidapi.com"),
        ]
        for name, url, host in targets:
            h = {"X-RapidAPI-Key": Config.RAPIDAPIKEY, "X-RapidAPI-Host": host}
            results.append(hit(name, "GET", url, headers=h))

    summary = []
    for r in results:
        code = r.get("status_code")
        if code == 200:
            verdict = "OK"
        elif code in (401, 403):
            verdict = "AUTH_FAIL"
        elif code == 404:
            verdict = "PATH_FAIL"
        else:
            verdict = "PENDING"
        summary.append({
            "name": r["name"],
            "status_code": code,
            "verdict": verdict,
            "url": r["url"],
        })

    report = {
        "timestamp": datetime.now().isoformat(),
        "detected": detected,
        "summary": summary,
        "results": results,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== PROVIDERS AUDIT SUMMARY ===")
    for row in summary:
        print(f"{row['name']:30} {str(row['status_code']):>5}  {row['verdict']}")
    print(f"REPORT_FILE: {OUT}")


if __name__ == "__main__":
    main()
