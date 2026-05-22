# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py
# desc: Shared presenter helpers for MarketSummary widget model captions.

from __future__ import annotations


def _dist_text(distribution: dict[str, int]) -> str:
    if not distribution:
        return "-"
    return ",".join(f"{key}:{distribution[key]}" for key in sorted(distribution))


def active_event_compact_reading_line(summary_payload: dict | None) -> str:
    if not summary_payload:
        return "active_event_reading unavailable"

    active_event_rows = list(
        summary_payload.get("orderbook_active_event_compact_rows")
        or summary_payload.get("orderbook_active_event_contracts")
        or []
    )
    if not active_event_rows:
        active_event_names = [
            str(name).strip()
            for name in (summary_payload.get("orderbook_active_event_names") or [])
            if str(name).strip()
        ]
        if not active_event_names:
            return "active_event_reading unavailable"
        first_name = active_event_names[0]
        suffix = f" +{len(active_event_names) - 1} more" if len(active_event_names) > 1 else ""
        return f"{first_name}{suffix}"

    first_event = dict(active_event_rows[0] or {})
    event_name = str(first_event.get("event_name") or "-").strip() or "-"
    event_family = str(first_event.get("event_family") or "-").strip() or "-"
    usage_grade = str(first_event.get("usage_grade") or "-").strip() or "-"
    actionability = str(first_event.get("actionability") or "-").strip() or "-"
    horizon = str(first_event.get("forecast_horizon_hint") or "-").strip() or "-"
    half_life_sec = first_event.get("half_life_sec")
    half_life_text = "-" if half_life_sec in (None, "") else str(half_life_sec)
    side = str(first_event.get("side") or "-").strip() or "-"

    suffix = f" +{len(active_event_rows) - 1} more" if len(active_event_rows) > 1 else ""

    return (
        f"{event_name} "
        f"({event_family} / {usage_grade} / {actionability} / {horizon} / "
        f"half_life={half_life_text} / {side})"
        f"{suffix}"
    )


def summary_widget_caption(summary_widget) -> str:
    notable_text = "-" if not summary_widget.notable_tags else ",".join(summary_widget.notable_tags)
    alert_text = "-" if not summary_widget.alert_tags else ",".join(summary_widget.alert_tags)

    slots_present_text = (
        ",".join(summary_widget.orderbook_summary_slots_present)
        if summary_widget.orderbook_summary_slots_present
        else "-"
    )
    active_event_names_text = (
        ",".join(summary_widget.orderbook_active_event_names)
        if summary_widget.orderbook_active_event_names
        else "-"
    )
    family_dist_text = _dist_text(summary_widget.semantic_event_family_distribution)
    trust_dist_text = _dist_text(summary_widget.semantic_trust_bucket_distribution)
    interpretation_dist_text = _dist_text(
        summary_widget.semantic_interpretation_bucket_distribution
    )
    consumer_dist_text = _dist_text(summary_widget.semantic_consumer_distribution)
    age_text = "-" if summary_widget.age_sec is None else f"{float(summary_widget.age_sec):.1f}s"
    event_ts_text = summary_widget.event_ts or "-"

    return (
        "summary_widget "
        f"freshness={summary_widget.freshness_key} / "
        f"trust={summary_widget.trust_key or '-'} / "
        f"continuity={summary_widget.continuity_key or '-'} / "
        f"interpretation={summary_widget.interpretation_key or '-'} / "
        f"semantic_wiring={summary_widget.semantic_wiring_key} / "
        f"observer_status={summary_widget.semantic_observer_status_key} / "
        f"observer_present={summary_widget.semantic_observer_present_key} / "
        f"usage_summary_present={summary_widget.semantic_usage_summary_present_key} / "
        f"contract_rows_present={summary_widget.semantic_contract_rows_present_key} / "
        f"semantic_source={summary_widget.semantic_summary_source_key} / "
        f"semantic_contract={summary_widget.semantic_contract_source_key} / "
        f"semantic_version={summary_widget.semantic_meaning_version_key} / "
        f"orderbook_wiring={summary_widget.orderbook_wiring_key} / "
        f"orderbook_source={summary_widget.orderbook_contract_status_source_key} / "
        f"semantic_rows={summary_widget.semantic_rows_count} / "
        f"semantic_total_rows={summary_widget.semantic_total_rows} / "
        f"semantic_active_events={summary_widget.semantic_active_event_count} / "
        f"mapped_events={summary_widget.semantic_mapped_event_count} / "
        f"unknown_events={summary_widget.semantic_unknown_event_count} / "
        f"family_dist={family_dist_text} / "
        f"trust_dist={trust_dist_text} / "
        f"interpretation_dist={interpretation_dist_text} / "
        f"consumer_dist={consumer_dist_text} / "
        f"summary_slots={summary_widget.summary_slots_count} / "
        f"slots_present={slots_present_text} / "
        f"near_wall_present={summary_widget.orderbook_near_wall_present_key} / "
        f"support_present={summary_widget.orderbook_support_present_key} / "
        f"resistance_present={summary_widget.orderbook_resistance_present_key} / "
        f"active_events={summary_widget.active_event_count} / "
        f"active_event_names={active_event_names_text} / "
        f"persistence_present={summary_widget.persistence_present_key} / "
        f"persistence_observable={summary_widget.persistence_observable_key} / "
        f"source={summary_widget.source_kind} / "
        f"series={summary_widget.source_series_id or '-'} / "
        f"age={age_text} / "
        f"event_ts={event_ts_text} / "
        f"notable={notable_text} / "
        f"alerts={alert_text}"
    )