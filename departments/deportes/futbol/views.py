from __future__ import annotations

from departments.deportes.futbol.service import get_fixtures, get_live, get_one


def futbol_index():
    return get_fixtures()


def futbol_live():
    return get_live()


def futbol_detail(fixture_id: str):
    return get_one(fixture_id)
