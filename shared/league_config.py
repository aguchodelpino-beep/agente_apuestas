"""
LigaConfig — Filtro de ligas prioritarias por región
Usa keys reales de Odds API / Sportsgameodds
"""
from typing import Dict, List, Tuple
from enum import Enum

class Region(Enum):
    EUROPA_TOP = "europa_top"
    COPAS_EUROPA = "copas_europa"
    LATINOAMERICA = "latinoamerica"
    ASIA_ARABIA = "asia_arabia"
    BASKET = "basket"

LEAGUES: Dict[Region, List[str]] = {
    Region.EUROPA_TOP: [
        "soccer_epl",
        "soccer_spain_la_liga", 
        "soccer_germany_bundesliga",
        "soccer_italy_serie_a",
        "soccer_france_ligue_one",
        "soccer_netherlands_eredivisie",
        "soccer_portugal_primeira_liga",
        "soccer_russia_premier_league",
    ],
    Region.COPAS_EUROPA: [
        "soccer_uefa_champs_league",
        "soccer_uefa_europa_league", 
        "soccer_uefa_europa_conference_league",
        "soccer_fa_cup",
        "soccer_germany_dfb_pokal",
        "soccer_italy_coppa_italia",
        "soccer_france_coupe_de_france",
    ],
    Region.LATINOAMERICA: [
        "soccer_brazil_campeonato",
        "soccer_argentina_primera_division",
        "soccer_mexico_ligamx",
        "soccer_colombia_primera_a",
        "soccer_chile_campeonato",
        "soccer_ecuador_liga_pro",
        "soccer_conmebol_copa_libertadores",
        "soccer_conmebol_copa_sudamericana",
        "soccer_usa_mls",
    ],
    Region.ASIA_ARABIA: [
        "soccer_saudi_arabia_pro_league",
        "soccer_japan_j_league",
        "soccer_china_superleague",
        "soccer_korea_kleague1",
        "soccer_australia_aleague",
    ],
    Region.BASKET: [
        "basketball_nba",
        "basketball_euroleague",
        "basketball_wnba",
    ],
}

ALL_LEAGUES = [liga for region in LEAGUES.values() for liga in region]

def get_leagues_by_region(region: Region) -> List[str]:
    """Ligas filtradas por región"""
    return LEAGUES.get(region, [])

def filter_events(events: list, region: Region = None) -> list:
    """Filtra eventos solo de ligas prioritarias"""
    if region is None:
        target_leagues = ALL_LEAGUES
    else:
        target_leagues = LEAGUES[region]
    
    filtered = []
    for event in events:
        league_key = event.get("league_key", event.get("key", ""))
        if league_key in target_leagues:
            filtered.append(event)
    return filtered

def get_region_name(region: Region) -> str:
    return {
        Region.EUROPA_TOP: "🌍 EUROPA TOP",
        Region.COPAS_EUROPA: "🏆 COPAS EUROPA", 
        Region.LATINOAMERICA: "🌎 LATINOAMÉRICA",
        Region.ASIA_ARABIA: "🕌 ASIA/ARABIA",
        Region.BASKET: "🏀 BASKET",
    }[region]
