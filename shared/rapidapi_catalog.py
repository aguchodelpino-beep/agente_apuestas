from __future__ import annotations
import os

RAPIDAPI_KEY = os.getenv("RAPIDAPIKEY", "").strip()

RAPIDAPI_PRODUCTS = [
    {
        "name": "odds_api1",
        "host": "odds-api1.p.rapidapi.com",
        "sport": "multi",
        "kind": "odds",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "sportsbook_api2",
        "host": "sportsbook-api2.p.rapidapi.com",
        "sport": "multi",
        "kind": "odds",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "today_football_prediction",
        "host": "today-football-prediction.p.rapidapi.com",
        "sport": "futbol",
        "kind": "predictions",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "bet365_api_inplay",
        "host": "bet365-api-inplay.p.rapidapi.com",
        "sport": "multi",
        "kind": "live",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "bet365data",
        "host": "bet365data.p.rapidapi.com",
        "sport": "multi",
        "kind": "odds",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "ultimate_tennis1",
        "host": "ultimate-tennis1.p.rapidapi.com",
        "sport": "tenis",
        "kind": "players",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "sports_live_scores",
        "host": "sports-live-scores.p.rapidapi.com",
        "sport": "multi",
        "kind": "live",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "tennis_api_atp_wta_itf",
        "host": "tennis-api-atp-wta-itf.p.rapidapi.com",
        "sport": "tenis",
        "kind": "events",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "allsportsapi2",
        "host": "allsportsapi2.p.rapidapi.com",
        "sport": "multi",
        "kind": "events",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "nba_api_free_data",
        "host": "nba-api-free-data.p.rapidapi.com",
        "sport": "basket",
        "kind": "stats",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "free_football_api_data",
        "host": "free-football-api-data.p.rapidapi.com",
        "sport": "futbol",
        "kind": "stats",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "premier_league_stats",
        "host": "premier-league-stats.p.rapidapi.com",
        "sport": "futbol",
        "kind": "stats",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "propsports",
        "host": "propsports.p.rapidapi.com",
        "sport": "basket",
        "kind": "props",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
    {
        "name": "nba_injury_data",
        "host": "nba-injury-data.p.rapidapi.com",
        "sport": "basket",
        "kind": "injuries",
        "status": "pending_path_discovery",
        "notes": "Host conocido, endpoint real pendiente",
        "paths": []
    },
]
