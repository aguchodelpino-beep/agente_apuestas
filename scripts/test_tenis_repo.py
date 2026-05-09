#!/usr/bin/env python3
from departments.deportes.tenis.handlers import handle_tenis_scoreboard, handle_tenis_news

scoreboard = handle_tenis_scoreboard()
print("SCOREBOARD_STATUS=", scoreboard["status_code"])
print("SCOREBOARD_URL=", scoreboard["url"])
data = scoreboard["data"]
if isinstance(data, dict):
    events = data.get("events", [])
    print("EVENTS_COUNT=", len(events))

news = handle_tenis_news()
print("NEWS_STATUS=", news["status_code"])
print("NEWS_URL=", news["url"])
data = news["data"]
if isinstance(data, dict):
    articles = data.get("articles", [])
    print("ARTICLES_COUNT=", len(articles))
