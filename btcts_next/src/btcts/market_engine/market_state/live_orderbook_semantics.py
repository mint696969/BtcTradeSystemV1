# path: ./btcts_next/src/btcts/market_engine/market_state/live_orderbook_semantics.py
# desc: Thin live adapter from current BookState to partial outward orderbook semantics summary.

from __future__ import annotations

from typing import Any

from btcts.ingestion.l2_canonical import OrderBookState
from btcts.processing.l3_market_semantics.continuity.models import BookState
from btcts.processing.l3_market_semantics.event_usage_policy import (
    enrich_event_contracts_for_bucket,
)
from btcts.processing.l3_market_semantics.orderbook.event_enrichment import candidate_events
from btcts.processing.l3_market_semantics.orderbook.liquidity_signals import (
    liquidity_pressure_signal,
    wall_signal,
)
from btcts.processing.l3_market_semantics.orderbook.signal_events import (
    build_signal_events,
)
from btcts.processing.l3_market_semantics.orderbook.semantic_profile import (
    OrderbookSemanticProfile,
)


def _merged_bids(book_state: BookState) -> list[dict[str, Any]]:
    return list(book_state.bids_near) + list(book_state.bids_far)


def _merged_asks(book_state: BookState) -> list[dict[str, Any]]:
    return list(book_state.asks_near) + list(book_state.asks_far)


def to_orderbook_state(book_state: BookState) -> OrderBookState:
    out = OrderBookState()
    out.set_snapshot(
        _merged_bids(book_state),
        _merged_asks(book_state),
        update_ts=book_state.exchange_ts or book_state.collector_ts,
    )
    return out


def build_live_orderbook_signal(
    *,
    book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    orderbook = to_orderbook_state(book_state)
    profile = OrderbookSemanticProfile.from_policy(
        semantic_policy,
        levels=20,
    )

    pressure = liquidity_pressure_signal(
        orderbook,
        levels=10,
        pressure_threshold=profile.pressure_threshold,
    )
    wall = wall_signal(
        orderbook,
        levels=20,
        wall_ratio_threshold=profile.wall_ratio_threshold,
        near_rank_threshold=profile.wall_near_rank_threshold,
    )

    return {
        "summary": {
            "spread": pressure.get("spread"),
            "mid": pressure.get("mid"),
            "imbalance": pressure.get("imbalance"),
            "bid_depth": pressure.get("bid_depth"),
            "ask_depth": pressure.get("ask_depth"),
        },
        "pressure": pressure,
        "wall": wall,
        "bid_pull": None,
        "ask_pull": None,
    }


def build_live_orderbook_transition_summary(
    *,
    prev_book_state: BookState | None,
    curr_book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    prev_signal = None
    if prev_book_state is not None:
        prev_signal = build_live_orderbook_signal(
            book_state=prev_book_state,
            semantic_policy=semantic_policy,
        )

    curr_signal = build_live_orderbook_signal(
        book_state=curr_book_state,
        semantic_policy=semantic_policy,
    )
    events = build_signal_events(prev_signal, curr_signal)

    persistence = next(
        (
            {
                "event_name": str(event.get("event_name")),
                "side": event.get("side"),
            }
            for event in events
            if str(event.get("event_name"))
            in {
                "near_wall_continued",
                "support_continued",
                "resistance_continued",
            }
        ),
        None,
    )

    return {
        "prev_signal_present": prev_signal is not None,
        "persistence": persistence,
    }


def build_live_orderbook_semantics_summary(
    *,
    prev_book_state: BookState | None = None,
    book_state: BookState,
    semantic_policy: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    signal = build_live_orderbook_signal(
        book_state=book_state,
        semantic_policy=semantic_policy,
    )
    transition = build_live_orderbook_transition_summary(
        prev_book_state=prev_book_state,
        curr_book_state=book_state,
        semantic_policy=semantic_policy,
    )
    events = candidate_events(signal)

    near_wall = None
    if bool((signal.get("wall") or {}).get("near_wall_detected")):
        wall = signal.get("wall") or {}
        near_wall = {
            "side": wall.get("near_strongest_side"),
            "rank": wall.get("near_strongest_rank"),
            "ratio": wall.get("near_strongest_ratio"),
        }

    support = next(
        (
            dict(event)
            for event in events
            if str(event.get("event_name")) == "support_candidate"
        ),
        None,
    )
    resistance = next(
        (
            dict(event)
            for event in events
            if str(event.get("event_name")) == "resistance_candidate"
        ),
        None,
    )
    persistence = transition.get("persistence")

    active_events: list[dict[str, Any]] = [dict(event) for event in events]

    persistence_event_name = str((persistence or {}).get("event_name") or "").strip()
    persistence_side = (persistence or {}).get("side")
    if persistence_event_name:
        active_events.append(
            {
                "event_name": persistence_event_name,
                "side": persistence_side,
            }
        )

    enriched_active_event_contracts = enrich_event_contracts_for_bucket(
        active_events,
        book_state.interpretation_bucket,
        trust_state=str(getattr(book_state.trust_state, "value", book_state.trust_state) or ""),
    )

    active_event_contracts: list[dict[str, Any]] = []
    seen_event_keys: set[tuple[str, str]] = set()

    for event in enriched_active_event_contracts:
        event_name = str(event.get("event_name") or "").strip()
        side = str(event.get("side") or "").strip()
        if not event_name:
            continue

        dedupe_key = (event_name, side)
        if dedupe_key in seen_event_keys:
            continue
        seen_event_keys.add(dedupe_key)

        raw_consumer_allowed = event.get("consumer_allowed")
        consumer_allowed = list(raw_consumer_allowed) if isinstance(raw_consumer_allowed, list) else []

        raw_invalidates_on = event.get("invalidates_on")
        invalidates_on = list(raw_invalidates_on) if isinstance(raw_invalidates_on, list) else []

        raw_evidence_refs = event.get("evidence_refs")
        evidence_refs = list(raw_evidence_refs) if isinstance(raw_evidence_refs, list) else []

        active_event_contracts.append(
            {
                "contract_source": str(event.get("contract_source") or "l3_event_usage_policy"),
                "event_name": event_name,
                "event_family": str(event.get("event_family") or "unknown"),
                "usage_grade": str(event.get("usage_grade") or "unknown"),
                "interpretation_bucket": event.get("interpretation_bucket"),
                "meaning_version": str(event.get("meaning_version") or "unknown"),
                "confidence": event.get("confidence"),
                "trust_bucket": str(event.get("trust_bucket") or "unknown"),
                "consumer_allowed": consumer_allowed,
                "actionability": str(event.get("actionability") or "unknown"),
                "forecast_horizon_hint": str(event.get("forecast_horizon_hint") or "unknown"),
                "half_life_sec": event.get("half_life_sec"),
                "invalidates_on": invalidates_on,
                "evidence_refs": evidence_refs,
                "side": event.get("side"),
            }
        )

    active_event_names = [
        str(event.get("event_name") or "")
        for event in active_event_contracts
        if str(event.get("event_name") or "").strip()
    ]

    summary_slots_present = [
        slot_name
        for slot_name, slot_value in (
            ("near_wall", near_wall),
            ("support", support),
            ("resistance", resistance),
            ("persistence", persistence),
        )
        if slot_value is not None
    ]

    summary = {
        "near_wall": near_wall,
        "support": support,
        "resistance": resistance,
        "persistence": persistence,
        "summary_slots_present": summary_slots_present,
        "summary_slots_count": len(summary_slots_present),
        "active_event_count": len(active_event_contracts),
        "active_event_names": active_event_names,
        "active_event_contracts": active_event_contracts,
    }

    present_count = len(summary_slots_present)

    # live adapter がここまで到達している時点で wiring 自体は存在する。
    # したがって current row に active semantics が 0 件でも "missing" ではなく
    # "partial" として扱い、現在の有効要素数は summary 側で読む。
    contract_status = "partial"
    if present_count >= 4:
        contract_status = "wired"

    return contract_status, summary