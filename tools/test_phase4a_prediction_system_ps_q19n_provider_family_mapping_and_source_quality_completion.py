# path: ./tools/test_phase4a_prediction_system_ps_q19n_provider_family_mapping_and_source_quality_completion.py
# desc: Focused guard for PS-Q19N provider-family mapping and OHLCV source-quality completion.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_prediction_system_result_builder_runner import (  # noqa: E402
    OHLCV_SOURCE_QUALITY_IDS,
    _build_from_kwargs_contract,
    _source_quality_status_map_from_kwargs_contract,
)
from btcts.prediction.source_quality import _provider_family_for_source_id  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19N_PROVIDER_FAMILY_MAPPING_AND_SOURCE_QUALITY_COMPLETION_2026-06-25.md"
BUILDER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_system_result_builder_runner.py"
SOURCE_QUALITY = REPO_ROOT / "btcts_next/src/btcts/prediction/source_quality.py"

REQUIRED_MARKERS = (
    "ps_q19n_provider_family_mapping_and_source_quality_completion=true",
    "bitflyer_trades_provider_family_mapped=true",
    "bitflyer_board_summary_provider_family_mapped=true",
    "prediction_ohlcv_provider_family_mapped=true",
    "ohlcv_source_quality_statuses_built_from_q10a_rows=true",
    "ohlcv_1m_quality_status_mapped=true",
    "ohlcv_1d_quality_status_mapped=true",
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


def test_spec_declares_provider_mapping_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_provider_family_mapping_no_longer_unknown_for_local_and_ohlcv_sources() -> None:
    assert _provider_family_for_source_id("bitflyer_trades", "bitflyer_local_fx_tradeflow") == "bitflyer_local_fx"
    assert _provider_family_for_source_id("bitflyer_board_summary", "bitflyer_local_fx_orderbook") == "bitflyer_local_fx"
    assert _provider_family_for_source_id("ohlcv_1m", "prediction_ohlcv_from_q10a_rows") == "prediction_ohlcv"
    assert _provider_family_for_source_id("provider_source_reliability_state", "prediction_source_quality_summary") == "prediction_source_quality"


def test_source_quality_status_map_includes_ohlcv_statuses() -> None:
    statuses = _source_quality_status_map_from_kwargs_contract(_builder_kwargs())
    assert set(OHLCV_SOURCE_QUALITY_IDS).issubset(set(statuses))
    assert {"bitflyer_trades", "bitflyer_board_summary", "bitflyer_fx_ticker", "provider_source_reliability_state"}.issubset(set(statuses))
    for source_id in OHLCV_SOURCE_QUALITY_IDS:
        status = statuses[source_id]
        assert status.usable is True
        assert status.source_family == "prediction_ohlcv_from_q10a_rows"
        assert status.to_dict()["would_send_to_broker"] is False


def test_build_prediction_system_result_observes_ohlcv_quality_statuses() -> None:
    payload = _build_from_kwargs_contract(_builder_kwargs())
    supplied = set(payload["source_quality_status_ids_supplied"])
    assert set(OHLCV_SOURCE_QUALITY_IDS).issubset(supplied)
    coverage = payload.get("source_artifact_coverage_summary") or {}
    observed = set(coverage.get("observed_required_source_ids") or [])
    missing_quality = set((coverage.get("tier0_source_quality_gate") or {}).get("missing_quality_status_source_ids") or [])
    assert set(OHLCV_SOURCE_QUALITY_IDS).issubset(observed)
    assert not (set(OHLCV_SOURCE_QUALITY_IDS) & missing_quality)
    assert payload.get("would_send_to_broker") is False


def test_source_quality_and_builder_markers_present() -> None:
    builder = BUILDER.read_text(encoding="utf-8")
    source_quality = SOURCE_QUALITY.read_text(encoding="utf-8")
    assert "OHLCV_SOURCE_QUALITY_IDS" in builder
    assert "_add_ohlcv_source_quality_statuses" in builder
    assert "prediction_ohlcv_from_q10a_rows" in builder
    assert '"bitflyer_board_summary": "bitflyer_local_fx"' in source_quality
    assert '"prediction_ohlcv": "prediction_ohlcv"' in source_quality


if __name__ == "__main__":
    test_spec_declares_provider_mapping_and_safety_boundaries()
    test_provider_family_mapping_no_longer_unknown_for_local_and_ohlcv_sources()
    test_source_quality_status_map_includes_ohlcv_statuses()
    test_build_prediction_system_result_observes_ohlcv_quality_statuses()
    test_source_quality_and_builder_markers_present()
    print('{"ok": true}')
