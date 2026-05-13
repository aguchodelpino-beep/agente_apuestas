from __future__ import annotations

from typing import Any

from shared.event_matcher import match_provider_events
from shared.event_schema import ProviderRef, build_enriched_event
from shared.normalizer_engine import normalize_event_payload


def _provider_ref_from_event(event: dict[str, Any], confidence: float = 1.0) -> ProviderRef:
    return ProviderRef(
        provider=str(event.get("provider") or ""),
        provider_event_id=str(event.get("provider_event_id") or event.get("id") or ""),
        raw_home_team=str(event.get("home_team") or event.get("home") or event.get("team1") or ""),
        raw_away_team=str(event.get("away_team") or event.get("away") or event.get("team2") or ""),
        raw_league=str(event.get("league") or event.get("competition") or ""),
        raw_start_time=str(event.get("start_time") or event.get("commence_time") or event.get("date") or ""),
        confidence=confidence,
    )


def build_enriched_events(
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    *,
    threshold: float = 0.82,
) -> list[dict[str, Any]]:
    matches = match_provider_events(base_events, candidate_events, threshold=threshold)

    candidate_index: dict[tuple[str, str], dict[str, Any]] = {}
    for event in candidate_events:
        provider = str(event.get("provider") or "")
        provider_event_id = str(event.get("provider_event_id") or event.get("id") or "")
        candidate_index[(provider, provider_event_id)] = event

    confidence_index: dict[tuple[str, str], float] = {
        (m["candidate_provider"], m["candidate_provider_id"]): float(m["confidence"])
        for m in matches
    }

    matched_candidate_keys = {
        (m["candidate_provider"], m["candidate_provider_id"])
        for m in matches
    }

    enriched: list[dict[str, Any]] = []

    for base in base_events:
        normalized = normalize_event_payload(base)
        refs = [_provider_ref_from_event(base, confidence=1.0)]

        base_provider = str(base.get("provider") or "")
        base_provider_id = str(base.get("provider_event_id") or base.get("id") or "")

        related = [
            m for m in matches
            if m["base_provider"] == base_provider and m["base_provider_id"] == base_provider_id
        ]

        for match in related:
            key = (match["candidate_provider"], match["candidate_provider_id"])
            candidate = candidate_index.get(key)
            if candidate is None:
                continue
            refs.append(_provider_ref_from_event(candidate, confidence=float(match["confidence"])))

        enriched_event = build_enriched_event(
            internal_event_id=normalized["internal_event_id"],
            sport=normalized["sport"],
            league=normalized["league"],
            start_time=normalized["start_time"],
            home_team=normalized["home_team"],
            away_team=normalized["away_team"],
            provider_refs=refs,
        )
        enriched.append(enriched_event.to_dict())

    for candidate in candidate_events:
        provider = str(candidate.get("provider") or "")
        provider_event_id = str(candidate.get("provider_event_id") or candidate.get("id") or "")
        key = (provider, provider_event_id)
        if key in matched_candidate_keys:
            continue

        normalized = normalize_event_payload(candidate)
        enriched_event = build_enriched_event(
            internal_event_id=normalized["internal_event_id"],
            sport=normalized["sport"],
            league=normalized["league"],
            start_time=normalized["start_time"],
            home_team=normalized["home_team"],
            away_team=normalized["away_team"],
            provider_refs=[_provider_ref_from_event(candidate, confidence=confidence_index.get(key, 1.0))],
        )
        enriched.append(enriched_event.to_dict())

    return enriched

if __name__ == "__main__":
    print("SCRIPT OK")
