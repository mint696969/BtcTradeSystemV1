# path: ./tools/test_phase4a_prediction_system_ps_q19m_tier0_source_quality_status_input_repair.py
# desc: Focused guard for PS-Q19M Tier0 source-quality status input repair.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    _build_from_kwargs_contract,
    _source_quality_status_map_from_kwargs_contract,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19M_TIER0_SOURCE_QUALITY_STATUS_INPUT_REPAIR_2026-06-25.md"
BUILDER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py"

REQUIRED_MARKERS = (
    "ps_q19m_tier0_source_quality_status_input_repair=true",
    "source_quality_by_id_built_from_q10a_builder_kwargs=true",
    "bitflyer_trades_quality_status_mapped=true",
    "bitflyer_board_summary_quality_status_mapped=true",
    "bitflyer_fx_ticker_quality_status_mapped=true",
    "provider_source_reliability_state_status_mapped=true",
    "source_quality_by_id_passed_to_prediction_system=true",
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
            {"source_id": "bitflyer_fx_ticker", "venue": "bitflyer", "symbol": "FX_BTC_JPY", "market_role": "bitflyer_fx", "price": 100.5, "best_bid": 100.0, "best_ask": 101.0, "collector_ts": "2026-06-25T00:00:02Z"},
        ],
        "feature_depth_context_summary": {
            "source_id": "bitflyer_board_summary",
            "bid_level_count": 20,
            "ask_level_count": 20,
            "event_ts": "2026-06-25T00:00:02Z",
        },
        "requested_horizon_groups": ["nowcast"],
        "requested_horizons_sec": [15],
        "previous_prediction_run_id": None,
        "now": "2026-06-25T00:00:03Z",
    }


def test_spec_declares_tier0_source_quality_repair_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_source_quality_status_map_is_built_from_builder_kwargs() -> None:
    statuses = _source_quality_status_map_from_kwargs_contract(_builder_kwargs())
    assert set(statuses) >= {"bitflyer_trades", "bitflyer_board_summary", "bitflyer_fx_ticker", "provider_source_reliability_state"}
    assert statuses["bitflyer_trades"].usable is True
    assert statuses["bitflyer_board_summary"].usable is True
    assert statuses["bitflyer_fx_ticker"].usable is True
    for status in statuses.values():
        data = status.to_dict()
        assert data["read_only"] is True
        assert data["non_executing"] is True
        assert data["would_send_to_broker"] is False


def test_build_prediction_system_result_receives_source_quality_statuses() -> None:
    payload = _build_from_kwargs_contract(_builder_kwargs())
    assert payload["source_quality_by_id_supplied"] is True
    supplied = set(payload["source_quality_status_ids_supplied"])
    assert {"bitflyer_trades", "bitflyer_board_summary", "bitflyer_fx_ticker", "provider_source_reliability_state"}.issubset(supplied)
    coverage = payload.get("source_artifact_coverage_summary") or {}
    observed = set(coverage.get("observed_required_source_ids") or [])
    missing_quality = set((coverage.get("tier0_source_quality_gate") or {}).get("missing_quality_status_source_ids") or [])
    assert "bitflyer_trades" in observed
    assert "bitflyer_board_summary" in observed
    assert "bitflyer_fx_ticker" in observed
    assert "provider_source_reliability_state" in observed
    assert "bitflyer_trades" not in missing_quality
    assert "bitflyer_board_summary" not in missing_quality
    assert "bitflyer_fx_ticker" not in missing_quality
    assert payload.get("would_send_to_broker") is False


def test_builder_imports_source_quality_and_no_forced_none_remains() -> None:
    text = BUILDER.read_text(encoding="utf-8")
    assert "assess_source_quality" in text
    assert "SourceQualityStatus" in text
    assert "_source_quality_status_map_from_kwargs_contract" in text
    assert "source_quality_by_id=source_quality_by_id" in text
    assert "source_quality_by_id=None," not in text


if __name__ == "__main__":
    test_spec_declares_tier0_source_quality_repair_and_safety_boundaries()
    test_source_quality_status_map_is_built_from_builder_kwargs()
    test_build_prediction_system_result_receives_source_quality_statuses()
    test_builder_imports_source_quality_and_no_forced_none_remains()
    print('{"ok": true}')
