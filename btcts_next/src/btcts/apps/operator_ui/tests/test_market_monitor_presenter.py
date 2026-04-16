# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_presenter.py
# desc: Verify market monitor presenter contract caption reflects shared mainline contract fields.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_monitor_presenter import (
    summary_contract_caption,
)


def main() -> int:
    caption = summary_contract_caption(
        lang="ja",
        summary={
            "semantic_runtime_wiring_status": "wired",
            "semantic_observer_present": True,
            "semantic_usage_summary_present": True,
            "semantic_contract_rows_present": True,
            "semantic_usage_contract_rows_kind": "event_family_contract_rows",
            "semantic_usage_contract_rows_count": 2,
            "orderbook_wiring_status": "partial",
            "orderbook_summary_slots_count": 1,
            "orderbook_persistence_present": False,
            "orderbook_persistence_observable": True,
            "orderbook_active_event_count": 1,
            "orderbook_active_event_contracts_kind": "active_event_contract_rows",
            "orderbook_active_event_contracts_count": 1,
        },
    )

    assert "semantic_wiring=wired" in caption
    assert "observer_present=True" in caption
    assert "usage_summary_present=True" in caption
    assert "contract_rows_present=True" in caption
    assert "family_rows=2 (event_family_contract_rows)" in caption
    assert "orderbook_wiring=partial" in caption
    assert "summary_slots=1" in caption
    assert "persistence_present=False" in caption
    assert "persistence_observable=True" in caption
    assert "active_events=1" in caption
    assert "active_event_rows=1 (active_event_contract_rows)" in caption

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())