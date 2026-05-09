#!/usr/bin/env python3
from __future__ import annotations

from shared.api_usage import track_usage


def main() -> None:
    track_usage("sportsgameodds", used=5, remaining=995, total_limit=1000, endpoint="/sports", status_code=200)
    track_usage("oddsapi", used=2, remaining=498, total_limit=500, endpoint="/v4/sports", status_code=200)
    track_usage("rapidapi", used=1, remaining=999, total_limit=1000, endpoint="/nba-api-free-data", status_code=200)
    print("SIMULATION_OK")


if __name__ == "__main__":
    main()
