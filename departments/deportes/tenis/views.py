from __future__ import annotations

from departments.deportes.tenis.service import get_fixtures, get_live, get_one


def tenis_index():
    return get_fixtures()


def tenis_live():
    return get_live()


def tenis_detail(fixture_id: str):
    return get_one(fixture_id)
