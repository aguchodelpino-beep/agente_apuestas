#!/usr/bin/env python3
from shared.odds import list_sports

data, meta = list_sports()
print("OK")
print("api_key_used", meta["api_key_used"][:8])
print("status_code", meta["status_code"])
print("sports_count", len(data) if isinstance(data, list) else -1)
