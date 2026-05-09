from __future__ import annotations

from departments.deportes.basket.views import basket_index, basket_live, basket_detail

urlpatterns = [
    ("basket/", basket_index),
    ("basket/live/", basket_live),
    ("basket/<fixture_id>/", basket_detail),
]
