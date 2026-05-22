# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_top_panels_digest_caption.py
# desc: Verify health top panels digest caption stays additive and contract-boundary aware.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.health_top_panels import (  # noqa: E402
    build_health_digest_api_summary_caption,
    build_health_digest_collector_summary_caption,
    build_health_digest_layer3_summary_caption,
    build_health_digest_operational_reading_caption,
    build_health_digest_ws_summary_caption,
)
from btcts.processing.l4_consumer_models.operator_ui import (  # noqa: E402
    HealthDigestWidgetModel,
)


def main() -> int:
    widget = HealthDigestWidgetModel(
        widget_kind="health_digest",
        freshness_key="LIVE",
        collector_ok=True,
        collector_mode_key="unified",
        api_mode_key="normal",
        ws_board_state_key="healthy",
        ws_executions_state_key="healthy",
        trust_key="trusted",
        continuity_key="continuous",
        interpretation_key="allow_structural_use",
        semantic_wiring_key="wired",
        orderbook_wiring_key="partial",
        semantic_summary_source_key="market_state_semantic_usage_summary",
        semantic_observer_status_key="healthy",
        orderbook_contract_status_source_key="market_state_orderbook_contract_status",
        semantic_observer_present_key="true",
        semantic_usage_summary_present_key="true",
        semantic_contract_rows_present_key="true",
        semantic_source_series_present_key="true",
        orderbook_near_wall_present_key="true",
        orderbook_support_present_key="true",
        orderbook_resistance_present_key="false",
        orderbook_persistence_present_key="false",
        orderbook_persistence_observable_key="true",
        orderbook_summary_slots_present=["near_wall", "support", "persistence"],
        orderbook_active_event_names=["near_wall_continued"],
        semantic_contract_rows_count=2,
        orderbook_summary_slots_count=3,
        active_event_count=1,
        age_sec=5.0,
        event_ts="2026-04-11T15:00:00Z",
        source_kind="health_data_service",
    )

    collector_caption = build_health_digest_collector_summary_caption(
        widget=widget,
        payload={
            "collector_runtime": {
                "runtime_kind": "watchdog_managed",
            },
        },
    )
    assert "mode=unified" in collector_caption
    assert "ok=True" in collector_caption
    assert "runtime_kind=watchdog_managed" in collector_caption

    api_caption = build_health_digest_api_summary_caption(
        widget=widget,
        payload={
            "api_runtime": {
                "utilization": 0.22,
                "requests_60s": 14,
            },
        },
    )
    assert "mode=normal" in api_caption
    assert "utilization=22.0%" in api_caption
    assert "requests_60s=14" in api_caption

    ws_caption = build_health_digest_ws_summary_caption(
        widget=widget,
        payload={
            "ws_runtime": {
                "board_freshness": "LIVE",
                "executions_freshness": "LIVE",
            },
        },
    )
    assert "board=healthy (LIVE)" in ws_caption
    assert "exec=healthy (LIVE)" in ws_caption

    caption = build_health_digest_layer3_summary_caption(
        widget=widget,
        payload={
            "semantic_observability": {
                "observer_present": True,
                "usage_summary_present": True,
                "contract_rows_present": True,
                "contract_rows_count": 2,
                "source_series_present": True,
            },
            "orderbook_active_event_observability": {
                "persistence_present": False,
                "persistence_observable": True,
                "summary_slots_count": 3,
                "summary_slots_present": ["near_wall", "support", "persistence"],
                "active_event_count": 1,
                "active_event_names": ["near_wall_continued"],
                "active_event_compact_rows_count": 1,
                "active_event_compact_rows": [
                    {
                        "event_name": "near_wall_continued",
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "actionability": "review",
                        "forecast_horizon_hint": "short",
                        "half_life_sec": 30,
                        "side": "bid",
                    }
                ],
                "active_event_contracts_count": 1,
                "active_event_contracts": [
                    {
                        "event_name": "raw_contract_should_not_be_used",
                        "event_family": "raw_contract",
                    }
                ],
            },
            "semantic_usage_observer_present": True,
            "semantic_usage_summary_present": True,
            "semantic_usage_contract_rows_present": True,
            "semantic_usage_source_series_present": True,
            "semantic_usage_contract_rows_count": 2,
            "orderbook_persistence_present": False,
            "orderbook_persistence_observable": True,
            "orderbook_summary_slots_count": 3,
            "orderbook_active_event_count": 1,
            "orderbook_active_event_compact_rows_count": 1,
            "orderbook_active_event_contracts_count": 1,
        },
    )
    assert "semantic_wiring=wired" in caption
    assert "semantic_source=market_state_semantic_usage_summary" in caption
    assert "observer_status=healthy" in caption
    assert "orderbook_wiring=partial" in caption
    assert "orderbook_source=market_state_orderbook_contract_status" in caption
    assert "source=health_data_service" in caption
    assert "observer_present=True" in caption
    assert "usage_summary_present=True" in caption
    assert "contract_rows_present=True" in caption
    assert "source_series_present=True" in caption
    assert "persistence_present=False" in caption
    assert "persistence_observable=True" in caption
    assert "semantic_rows=2" in caption
    assert "summary_slots=3" in caption
    assert "slots_present=near_wall,support,persistence" in caption
    assert "active_events=1" in caption
    assert "active_event_names=near_wall_continued" in caption
    assert "active_event_compact_rows=1" in caption
    assert "active_event_rows=1" in caption
    assert "age=5.0s" in caption
    assert "event_ts=2026-04-11T15:00:00Z" in caption

    operational_caption = build_health_digest_operational_reading_caption(
        widget=widget,
        payload={
            "orderbook_active_event_observability": {
                "active_event_names": ["near_wall_continued"],
                "active_event_compact_rows": [
                    {
                        "event_name": "near_wall_continued",
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "actionability": "review",
                        "forecast_horizon_hint": "short",
                        "half_life_sec": 30,
                        "side": "bid",
                    }
                ],
                "active_event_contracts": [
                    {
                        "event_name": "raw_contract_should_not_be_used",
                        "event_family": "raw_contract",
                    }
                ],
            }
        },
    )
    assert "health_operational_reading=allow_structural_use" in operational_caption
    assert "trust=trusted" in operational_caption
    assert "continuity=continuous" in operational_caption
    assert "observer_status=healthy" in operational_caption
    assert "active_event=near_wall_continued" in operational_caption
    assert "source=health_data_service" in operational_caption
    assert "review_mode=operator_review_only" in operational_caption
    assert "execution=not_instruction" in operational_caption

    empty_caption = build_health_digest_layer3_summary_caption(
        widget=None,
        payload=None,
    )
    assert empty_caption == "health_digest unavailable"

    empty_operational_caption = build_health_digest_operational_reading_caption(
        widget=None,
        payload=None,
    )
    assert empty_operational_caption == "health_operational_reading unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())