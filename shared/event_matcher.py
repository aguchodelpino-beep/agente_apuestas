from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.normalizer_engine import (
    is_valid_normalized_event,
    normalize_event_payload,
)


@dataclass(slots=True)
class MatchResult:
    matched: bool
    confidence: float
    reasons: list[str]


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _provider_name(event: dict[str, Any]) -> str:
    return str(event.get("provider") or "")


def _provider_event_id(event: dict[str, Any]) -> str:
    return str(event.get("provider_event_id") or event.get("id") or "")


def _normalize_for_match(event: dict[str, Any]) -> dict[str, Any] | None:
    try:
        normalized = normalize_event_payload(event)
    except Exception:
        return None
    if not is_valid_normalized_event(normalized):
        return None
    return normalized


def _time_difference_minutes(a: str, b: str) -> float:
    da = _parse_utc(a)
    db = _parse_utc(b)
    return abs((da - db).total_seconds()) / 60.0


def match_events(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    max_minutes_diff: int = 180,
    min_confidence: float = 0.80,
) -> MatchResult:
    left_n = _normalize_for_match(left)
    right_n = _normalize_for_match(right)

    if left_n is None or right_n is None:
        return MatchResult(matched=False, confidence=0.0, reasons=["invalid_event"])

    sport_score = 1.0 if left_n["sport"] == right_n["sport"] else 0.0
    league_score = 1.0 if left_n["league"] == right_n["league"] else 0.0
    home_score = 1.0 if left_n["home_team"] == right_n["home_team"] else 0.0
    away_score = 1.0 if left_n["away_team"] == right_n["away_team"] else 0.0

    minutes_diff = _time_difference_minutes(left_n["start_time"], right_n["start_time"])
    time_score = max(0.0, 1.0 - (minutes_diff / max_minutes_diff)) if max_minutes_diff > 0 else 0.0

    confidence = (
        (sport_score * 0.10)
        + (league_score * 0.20)
        + (home_score * 0.30)
        + (away_score * 0.30)
        + (time_score * 0.10)
    )

    reasons: list[str] = []
    if sport_score == 1.0:
        reasons.append("sport_match")
    if league_score == 1.0:
        reasons.append("league_match")
    if home_score == 1.0:
        reasons.append("home_team_match")
    if away_score == 1.0:
        reasons.append("away_team_match")
    if minutes_diff <= 60:
        reasons.append("time_close")

    matched = (
        sport_score == 1.0
        and league_score == 1.0
        and home_score == 1.0
        and away_score == 1.0
        and minutes_diff <= max_minutes_diff
        and confidence >= min_confidence
    )

    return MatchResult(
        matched=matched,
        confidence=round(confidence, 4),
        reasons=reasons,
    )


def match_provider_events(
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    *,
    threshold: float = 0.82,
    max_minutes_diff: int = 180,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    used_candidate_keys: set[tuple[str, str]] = set()

    for base in base_events:
        best_match: dict[str, Any] | None = None
        best_confidence = -1.0

        for candidate in candidate_events:
            candidate_key = (_provider_name(candidate), _provider_event_id(candidate))
            if candidate_key in used_candidate_keys:
                continue

            result = match_events(
                base,
                candidate,
                max_minutes_diff=max_minutes_diff,
                min_confidence=threshold,
            )
            if not result.matched:
                continue

            if result.confidence > best_confidence:
                best_confidence = result.confidence
                best_match = {
                    "base_provider": _provider_name(base),
                    "base_provider_id": _provider_event_id(base),
                    "candidate_provider": _provider_name(candidate),
                    "candidate_provider_id": _provider_event_id(candidate),
                    "confidence": result.confidence,
                    "reasons": result.reasons,
                }

        if best_match is not None:
            used_candidate_keys.add(
                (best_match["candidate_provider"], best_match["candidate_provider_id"])
            )
            matches.append(best_match)

    return matches

if __name__ == "__main__":
    print("SCRIPT OK")
