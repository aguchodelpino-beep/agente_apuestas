#!/usr/bin/env python3
from departments.deportes.basket.handlers import (
    handle_basket_scoreboard,
    handle_basket_teams,
    handle_basket_news,
)

scoreboard = handle_basket_scoreboard()
print("SCOREBOARD_STATUS=", scoreboard["status_code"])
print("SCOREBOARD_URL=", scoreboard["url"])
data = scoreboard["data"]
if isinstance(data, dict):
    events = data.get("events", [])
    print("EVENTS_COUNT=", len(events))

teams = handle_basket_teams()
print("TEAMS_STATUS=", teams["status_code"])
print("TEAMS_URL=", teams["url"])
data = teams["data"]
if isinstance(data, dict):
    sports = data.get("sports", [])
    print("SPORTS_COUNT=", len(sports))

news = handle_basket_news()
print("NEWS_STATUS=", news["status_code"])
print("NEWS_URL=", news["url"])
data = news["data"]
if isinstance(data, dict):
    articles = data.get("articles", [])
    print("ARTICLES_COUNT=", len(articles))
