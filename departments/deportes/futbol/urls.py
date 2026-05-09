from __future__ import annotations

from departments.deportes.futbol.views import futbol_index, futbol_live, futbol_detail

urlpatterns = [
    ("futbol/", futbol_index),
    ("futbol/live/", futbol_live),
    ("futbol/<fixture_id>/", futbol_detail),
]
