# path: ./tools/test_phase4a_prediction_system_ps_q20d_preferred_row_consumer_integration_design.py
# desc: Focused guard for PS-Q20D preferred-row consumer integration design contract.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from btcts.market_engine.market_state.consumer_integration_design import (  # noqa: E402
    LANE_AUTOTRADE_TRIGGER,
    LANE_EXECUTION_CANDIDATE,
    LANE_PREDICTION_PRODUCER_INPUT,
    LANE_REPLAY_ANALYSIS,
    LANE_STRATEGY_CANDIDATE,
    LANE_WARROOM_READ,
    build_market_overview_consumer_integration_design,
)
from btcts.market_engine.market_state.consumer_row_selection import select_market_overview_consumer_preferred_row  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20D_PREFERRED_ROW_CONSUMER_INTEGRATION_DESIGN_2026-06-26.md"
MODULE = REPO_ROOT / "btcts_next/src/btcts/market_engine/market_state/consumer_integration_design.py"
INIT = REPO_ROOT / "btcts_next/src/btcts/market_engine/market_state/__init__.py"

REQUIRED_MARKERS = (
    "ps_q20d_preferred_row_consumer_integration_design=true",
    "integration_design_only=true",
    "warroom_runtime_behavior_changed=false",
    "prediction_producer_behavior_changed=false",
    "ps_q19r_scoring_policy_changed=false",
    "autotrade_trigger_allowed=false",
)

FALSE_BOUNDARIES = (
    "collector_runtime_behavior_changed=false",
    "market_state_writer_changed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "collector_ts": "2026-06-25T12:04:14Z",
            "trust_state": "trusted",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 100.0,
            "best_ask": 102.0,
            "spread": 2.0,
            "mid_price": 101.0,
            "source_series_id": "series:1",
            "source_stream_session_id": "stream:1",
        }
    return {
        "collector_ts": "2026-06-25T12:04:14Z",
        "trust_state": "quarantined",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 105.0,
        "best_ask": 104.0,
        "spread": -1.0,
        "mid_price": 104.5,
        "source_series_id": "series:1",
        "source_stream_session_id": "stream:1",
    }


def _lane(design, lane: str):
    return {item.lane: item for item in design.lane_policies}[lane]


def test_spec_declares_design_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_design_allows_read_only_lanes_when_preferred_row_exists() -> None:
    selection = select_market_overview_consumer_preferred_row([_row(ok=False), _row(ok=True)])
    design = build_market_overview_consumer_integration_design(selection)
    assert design.preferred_row_available is True
    assert design.diagnostic_rows_present is True
    assert design.fail_closed is False
    for lane in (LANE_WARROOM_READ, LANE_PREDICTION_PRODUCER_INPUT, LANE_REPLAY_ANALYSIS, LANE_STRATEGY_CANDIDATE):
        policy = _lane(design, lane)
        assert policy.status == "allowed_read_only"
        assert policy.may_use_consumer_preferred_row is True
        assert policy.may_display_diagnostic_rows is True
        assert policy.may_score_diagnostic_rows is False
        assert policy.may_trigger_execution is False
        assert policy.would_send_to_broker is False
    assert design.recommended_next_slice == "PS-Q20E_WARROOM_AND_PRODUCER_READ_ONLY_PREFERRED_ROW_ADAPTER"


def test_design_blocks_execution_and_autotrade_lanes_even_when_preferred_exists() -> None:
    selection = select_market_overview_consumer_preferred_row([_row(ok=True)])
    design = build_market_overview_consumer_integration_design(selection)
    for lane in (LANE_EXECUTION_CANDIDATE, LANE_AUTOTRADE_TRIGGER):
        policy = _lane(design, lane)
        assert policy.status == "blocked_by_policy"
        assert policy.may_use_consumer_preferred_row is False
        assert policy.may_trigger_execution is False
        assert policy.requires_human_policy_gate is True
        assert "ps_q20d_does_not_enable_execution_candidate_lane" in policy.blockers
    assert design.autotrade_trigger_allowed is False
    assert design.broker_private_api_allowed is False
    assert design.would_send_to_broker is False


def test_design_fail_closes_safe_read_lanes_without_preferred_row() -> None:
    selection = select_market_overview_consumer_preferred_row([_row(ok=False), _row(ok=False)])
    design = build_market_overview_consumer_integration_design(selection)
    assert design.preferred_row_available is False
    assert design.fail_closed is True
    assert design.recommended_next_slice == "continue_collector_reanchor_observation"
    policy = _lane(design, LANE_WARROOM_READ)
    assert policy.status == "blocked"
    assert policy.may_use_consumer_preferred_row is False
    assert "consumer_preferred_market_overview_row_missing" in policy.blockers


def test_market_state_init_exports_design_contract() -> None:
    text = INIT.read_text(encoding="utf-8")
    assert "build_market_overview_consumer_integration_design" in text
    assert "MarketOverviewConsumerIntegrationDesign" in text


def test_module_has_no_runtime_write_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_text(",
        "open(",
        "send_order(",
        "place_order(",
        "broker_private_api_allowed: bool = True",
        "call_private_api(",
        "private_api_client",
        "requests.",
        "urllib.",
        "would_send_to_broker: bool = True",
        "collector_runtime_behavior_changed: bool = True",
        "warroom_runtime_behavior_changed: bool = True",
        "prediction_producer_behavior_changed: bool = True",
        "ps_q19r_scoring_policy_changed: bool = True",
        "autotrade_trigger_allowed: bool = True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_design_and_safety_boundaries()
    test_design_allows_read_only_lanes_when_preferred_row_exists()
    test_design_blocks_execution_and_autotrade_lanes_even_when_preferred_exists()
    test_design_fail_closes_safe_read_lanes_without_preferred_row()
    test_market_state_init_exports_design_contract()
    test_module_has_no_runtime_write_or_execution_behavior()
    print('{"ok": true}')
