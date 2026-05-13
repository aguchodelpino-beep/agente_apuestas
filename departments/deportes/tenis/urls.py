from __future__ import annotations

from departments.deportes.tenis.views import tenis_index, tenis_live, tenis_detail

urlpatterns = [
    ("tenis/", tenis_index),
    ("tenis/live/", tenis_live),
    ("tenis/<fixture_id>/", tenis_detail),
]

if __name__ == "__main__":
    print("SCRIPT OK")
