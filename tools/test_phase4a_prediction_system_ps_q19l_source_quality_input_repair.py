# path: ./tools/test_phase4a_prediction_system_ps_q19l_source_quality_input_repair.py
# desc: Focused guard for PS-Q19L feature-depth source-quality input repair.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    _feature_depth_snapshot_from_kwargs_contract,
    _build_from_kwargs_contract,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19L_SOURCE_QUALITY_INPUT_REPAIR_2026-06-25.md"
BUILDER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py"

REQUIRED_MARKERS = (
    "ps_q19l_source_quality_input_repair=true",
    "feature_depth_snapshot_built_from_q10a_builder_kwargs=true",
    "bitflyer_board_summary_input_mapped=true",
    "bitflyer_trades_input_mapped=true",
    "feature_depth_snapshot_passed_to_prediction_system=true",
)

FALSE_BOUNDARIES = (
    "collector_behavior_changed=false",
    "hot_file_read_scope_changed=false",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _builder_kwargs() -> dict:
    return {
        "rows": [
            {"event_ts": "2026-06-25T00:00:00Z", "price": 100.0, "size": 0.1, "side": "BUY"},
            {"event_ts": "2026-06-25T00:00:01Z", "price": 101.0, "size": 0.2, "side": "SELL"},
            {"event_ts": "2026-06-25T00:00:02Z", "price": 100.5, "size": 0.3, "side": "BUY"},
        ],
        "venue_snapshots": [
            {"source_id": "bitflyer_fx_ticker", "venue": "bitflyer", "symbol": "FX_BTC_JPY", "market_role": "bitflyer_fx", "price": 100.5, "best_bid": 100.0, "best_ask": 101.0},
        ],
        "feature_depth_context_summary": {
            "source_id": "bitflyer_board_summary",
            "bid_level_count": 20,
            "ask_level_count": 20,
            "event_ts": "2026-06-25T00:00:00Z",
        },
        "requested_horizon_groups": ["nowcast"],
        "requested_horizons_sec": [15],
        "previous_prediction_run_id": None,
        "now": "2026-06-25T00:00:03Z",
    }


def test_spec_declares_source_quality_input_repair_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_feature_depth_snapshot_is_built_from_builder_kwargs() -> None:
    snapshot = _feature_depth_snapshot_from_kwargs_contract(_builder_kwargs())
    assert snapshot is not None
    data = snapshot.to_dict()
    assert data["orderbook"]["source_ids"] == ["bitflyer_board_summary"]
    assert data["tradeflow"]["source_ids"] == ["bitflyer_trades"]
    assert data["tradeflow"]["total_trade_count"] == 3
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False


def test_build_prediction_system_result_receives_feature_depth_and_covers_sources() -> None:
    payload = _build_from_kwargs_contract(_builder_kwargs())
    coverage = payload.get("source_artifact_coverage_summary") or {}
    observed = set(coverage.get("observed_required_source_ids") or [])
    assert "bitflyer_board_summary" in observed
    assert "bitflyer_trades" in observed
    assert payload.get("feature_depth_snapshot_supplied") is True or payload.get("debug_summary", {}).get("feature_depth_snapshot_supplied") is True
    assert payload.get("would_send_to_broker") is False


def test_builder_imports_feature_depth_and_no_forced_none_remains() -> None:
    text = BUILDER.read_text(encoding="utf-8")
    assert "build_feature_depth_snapshot" in text
    assert "_feature_depth_snapshot_from_kwargs_contract" in text
    assert "feature_depth_snapshot=feature_depth_snapshot" in text
    assert "feature_depth_snapshot=None," not in text


if __name__ == "__main__":
    test_spec_declares_source_quality_input_repair_and_safety_boundaries()
    test_feature_depth_snapshot_is_built_from_builder_kwargs()
    test_build_prediction_system_result_receives_feature_depth_and_covers_sources()
    test_builder_imports_feature_depth_and_no_forced_none_remains()
    print('{"ok": true}')
