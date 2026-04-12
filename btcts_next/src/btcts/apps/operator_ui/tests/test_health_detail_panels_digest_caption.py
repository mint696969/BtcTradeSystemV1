# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_detail_panels_digest_caption.py
# desc: Verify health current-state digest caption stays additive and wording-light.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.health_detail_panels import (  # noqa: E402
    build_health_digest_current_state_caption,
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
        semantic_contract_rows_count=1,
        orderbook_summary_slots_count=2,
        active_event_count=1,
        age_sec=5.0,
        event_ts="2026-04-11T15:00:00Z",
        source_kind="health_data_service",
    )

    caption = build_health_digest_current_state_caption(
        widget=widget,
        payload={
            "semantic_usage_contract_rows_count": 1,
            "orderbook_summary_slots_count": 2,
            "orderbook_active_event_contracts_count": 1,
        },
    )
    assert "freshness=LIVE" in caption
    assert "semantic_rows=1" in caption
    assert "summary_slots=2" in caption
    assert "active_event_rows=1" in caption

    empty_caption = build_health_digest_current_state_caption(
        widget=None,
        payload=None,
    )
    assert empty_caption == "health_digest unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())