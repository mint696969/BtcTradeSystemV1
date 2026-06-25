# path: ./tools/test_phase4a_prediction_system_ps_q20b_market_overview_consumer_row_selection_contract.py
# desc: Focused guard for PS-Q20B market.overview consumer preferred-row / diagnostic-row separation contract.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.market_engine.market_state.consumer_row_selection import (  # noqa: E402
    CONSUMER_PREFERRED,
    DIAGNOSTIC_TRANSITION,
    FAIL_CLOSED,
    classify_market_overview_consumer_row,
    select_market_overview_consumer_preferred_row,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20B_MARKET_OVERVIEW_CONSUMER_ROW_SELECTION_CONTRACT_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/market_engine/market_state/consumer_row_selection.py"
INIT = REPO_ROOT / "btcts_next/src/btcts/market_engine/market_state/__init__.py"

REQUIRED_MARKERS = (
    "ps_q20b_market_overview_consumer_row_selection_contract=true",
    "consumer_preferred_row_contract=true",
    "diagnostic_transition_row_contract=true",
    "responsibility_market_engine_market_state=true",
    "collector_runtime_behavior_changed=false",
    "ps_q19r_scoring_policy_changed=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_contract=false",
    "collector_state_write_performed_by_contract=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(
    *,
    trust_state: str = "trusted",
    bucket: str = "allow_structural_use",
    semantic: str = "healthy",
    best_bid: float | None = 100.0,
    best_ask: float | None = 102.0,
    spread: float | None = 2.0,
    source_series_id: str = "series:1",
) -> dict:
    return {
        "collector_ts": "2026-06-25T12:04:14Z",
        "exchange_ts": None,
        "trust_state": trust_state,
        "boundary_reason": "none" if trust_state == "trusted" else "profile_rule",
        "continuity_state": "continuous",
        "interpretation_bucket": bucket,
        "interpretation_reason": "unit",
        "semantic_observer_status": semantic,
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "mid_price": None if best_bid is None or best_ask is None else (best_bid + best_ask) / 2,
        "source_series_id": source_series_id,
        "source_stream_session_id": "stream:1",
    }


def test_spec_declares_contract_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_classifies_trusted_positive_spread_as_consumer_preferred() -> None:
    role = classify_market_overview_consumer_row(_row(), row_index=0)
    assert role.row_role == CONSUMER_PREFERRED
    assert role.quality_ok is True
    assert role.quality_reasons == ()
    assert role.usable_for_prediction is True
    assert role.usable_for_strategy_candidate is True
    assert role.usable_for_execution_candidate is False
    assert role.would_send_to_broker is False


def test_classifies_quarantined_crossed_book_as_diagnostic_transition() -> None:
    role = classify_market_overview_consumer_row(
        _row(trust_state="quarantined", bucket="reanchor_required", semantic="broken", best_bid=105.0, best_ask=104.0, spread=-1.0),
        row_index=3,
    )
    assert role.row_role == DIAGNOSTIC_TRANSITION
    assert role.quality_ok is False
    assert "market_overview_not_trusted" in role.quality_reasons
    assert "market_overview_not_allow_structural_use" in role.quality_reasons
    assert "market_overview_semantic_observer_broken" in role.quality_reasons
    assert "market_overview_negative_spread" in role.quality_reasons
    assert "market_overview_crossed_book" in role.quality_reasons
    assert role.usable_for_prediction is False
    assert role.diagnostic_visible is True


def test_selects_consumer_preferred_row_and_retains_diagnostic_rows() -> None:
    packet = select_market_overview_consumer_preferred_row(
        [
            _row(trust_state="quarantined", bucket="reanchor_required", semantic="broken", best_bid=105.0, best_ask=104.0, spread=-1.0, source_series_id="series:1"),
            _row(best_bid=100.0, best_ask=102.0, spread=2.0, source_series_id="series:1"),
            _row(best_bid=101.0, best_ask=103.0, spread=2.0, source_series_id="series:1"),
        ]
    )
    data = packet.to_dict()
    assert packet.selection_state == CONSUMER_PREFERRED
    assert packet.selected_row_index == 1
    assert packet.consumer_preferred_count == 2
    assert packet.diagnostic_transition_count == 1
    assert "diagnostic_transition_rows_retained" in packet.warning_reasons
    assert "multiple_consumer_preferred_rows_available" in packet.warning_reasons
    assert data["selected_row"]["best_bid"] == 100.0
    assert data["diagnostic_rows_retained"] is True
    assert data["collector_runtime_behavior_changed"] is False
    assert data["ps_q19r_scoring_policy_changed"] is False


def test_fail_closed_when_no_consumer_preferred_row_exists() -> None:
    packet = select_market_overview_consumer_preferred_row(
        [
            _row(trust_state="quarantined", bucket="reanchor_required", semantic="broken", best_bid=105.0, best_ask=104.0, spread=-1.0),
            _row(trust_state="quarantined", bucket="reanchor_required", semantic="broken", best_bid=106.0, best_ask=105.0, spread=-1.0),
        ]
    )
    assert packet.selection_state == FAIL_CLOSED
    assert packet.selected_row_index is None
    assert "consumer_preferred_market_overview_row_missing" in packet.blocked_reasons
    assert packet.preferred_row_available_for_future_consumers is False


def test_market_state_init_exports_contract() -> None:
    text = INIT.read_text(encoding="utf-8")
    assert "select_market_overview_consumer_preferred_row" in text
    assert "MarketOverviewConsumerRowSelection" in text


def test_module_has_no_execution_or_write_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_text(",
        "open(",
        "send_order(",
        "place_order(",
        "private_api",
        "requests.",
        "urllib.",
        "would_send_to_broker: bool = True",
        "collector_runtime_behavior_changed: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_contract_and_safety_boundaries()
    test_classifies_trusted_positive_spread_as_consumer_preferred()
    test_classifies_quarantined_crossed_book_as_diagnostic_transition()
    test_selects_consumer_preferred_row_and_retains_diagnostic_rows()
    test_fail_closed_when_no_consumer_preferred_row_exists()
    test_market_state_init_exports_contract()
    test_module_has_no_execution_or_write_behavior()
    print('{"ok": true}')
