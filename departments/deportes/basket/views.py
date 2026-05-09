from __future__ import annotations

from departments.deportes.basket.service import get_fixtures, get_live, get_one


def basket_index():
    return get_fixtures()


def basket_live():
    return get_live()


def basket_detail(fixture_id: str):
    return get_one(fixture_id)
