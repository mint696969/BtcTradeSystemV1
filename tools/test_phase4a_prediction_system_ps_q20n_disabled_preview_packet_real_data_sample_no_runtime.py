# path: ./tools/test_phase4a_prediction_system_ps_q20n_disabled_preview_packet_real_data_sample_no_runtime.py
# desc: Focused guard for PS-Q20N disabled preview packet real-data sample with no runtime.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from tools.sample_phase4a_prediction_system_ps_q20n_disabled_preview_packet_real_data_sample_no_runtime import (  # noqa: E402
    SAMPLE_VERSION,
    build_disabled_preview_packet_real_data_sample_no_runtime,
    run_disabled_preview_packet_real_data_sample_no_runtime,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20N_DISABLED_PREVIEW_PACKET_REAL_DATA_SAMPLE_NO_RUNTIME_2026-06-26.md"
MODULE = REPO_ROOT / "tools/sample_phase4a_prediction_system_ps_q20n_disabled_preview_packet_real_data_sample_no_runtime.py"

REQUIRED_MARKERS = (
    "ps_q20n_disabled_preview_packet_real_data_sample_no_runtime=true",
    "sample_only=true",
    "hot_data_read_only=true",
    "stdout_only=true",
    "preview_packet_only=true",
    "default_disabled_preview=true",
    "runtime_enablement_allowed=false",
    "loader_binding_runtime_allowed=false",
)

FALSE_BOUNDARIES = (
    "target_loader_invoked=false",
    "latest_prediction_warroom_read_model_loader_changed=false",
    "component_runtime_binding_allowed=false",
    "ui_code_changed=false",
    "warroom_ui_trigger_enabled=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "runtime_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "would_write_warroom_view_artifact=false",
    "ps_q19r_scoring_policy_changed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _payload() -> dict:
    return {
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-25T11:59:14Z",
            "read_only": True,
            "non_executing": True,
            "records": [
                {
                    "family": "market_regime",
                    "horizon_sec": 15,
                    "horizon_key": "15s",
                    "primary_label": "range_candidate",
                    "confidence": "medium",
                    "score": 0.52,
                    "usable": True,
                    "warnings": [],
                    "drivers": ["range_boundary_visible"],
                    "values_snapshot": {"estimated_signal_strength_percent": 51},
                    "read_only": True,
                    "non_executing": True,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "would_append_ledger": False,
                }
            ],
        },
    }


def _row(*, ok: bool = True) -> dict:
    if ok:
        return {
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "collector_ts": "2026-06-26T01:15:08Z",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 9628144.0,
            "best_ask": 9628772.0,
            "spread": 628.0,
            "mid_price": 9628458.0,
            "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:2",
            "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
        }
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-26T01:15:07Z",
        "trust_state": "quarantined",
        "continuity_state": "transition",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 9628773.0,
        "best_ask": 9628772.0,
        "spread": -1.0,
        "mid_price": 9628772.5,
        "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:1",
        "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
    }


def test_spec_declares_sample_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_sample_builds_preview_packet_from_real_like_inputs_without_attaching_section() -> None:
    result = build_disabled_preview_packet_real_data_sample_no_runtime(
        prediction_payload=_payload(),
        market_overview_rows=[_row(ok=False), _row(ok=True)],
        prediction_path="D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
        market_overview_path="D:/btc_ts_hot/data/market_state/.../part-00001.jsonl",
        now_utc="2026-06-26T01:16:00Z",
    )
    assert result["sample_version"] == SAMPLE_VERSION
    assert result["sample_state"] == "disabled_preview_packet_real_data_sample_ready"
    assert result["sample_only"] is True
    assert result["hot_data_read_only"] is True
    assert result["stdout_only"] is True
    assert result["preview_state"] == "disabled_binding_plan_preview_packet_ready"
    assert result["preview_packet_only"] is True
    assert result["default_disabled_preview"] is True
    assert result["plan_ready"] is True
    assert result["helper_state"] == "explicit_read_only_loader_binding_helper_disabled"
    assert result["helper_dry_run_ready"] is True
    assert result["optional_section_attached"] is False
    assert result["output_model_has_optional_section"] is False
    assert result["selected_row_summary"]["spread"] == 628.0
    assert result["target_loader_invoked"] is False
    assert result["would_send_to_broker"] is False


def test_runner_reads_temp_real_data_files_and_writes_no_artifact(tmp_path: Path) -> None:
    prediction = tmp_path / "prediction" / "latest_prediction_system_result.json"
    overview = tmp_path / "data" / "market_state" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.overview" / "date=2026-06-26" / "part-00001.jsonl"
    prediction.parent.mkdir(parents=True)
    overview.parent.mkdir(parents=True)
    prediction.write_text(json.dumps(_payload()), encoding="utf-8")
    overview.write_text(json.dumps(_row(ok=False)) + "\n" + json.dumps(_row(ok=True)) + "\n", encoding="utf-8")

    result = run_disabled_preview_packet_real_data_sample_no_runtime(
        data_root=tmp_path,
        prediction_path="prediction/latest_prediction_system_result.json",
        market_overview_path="data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date=2026-06-26/part-00001.jsonl",
        tail_rows=10,
        now_utc="2026-06-26T01:16:00Z",
    )
    assert result["ok"] is True
    assert result["market_overview_tail_row_count"] == 2
    assert result["optional_section_attached"] is False
    assert result["output_model_has_optional_section"] is False
    assert not (tmp_path / "prediction" / "status" / "latest_prediction_warroom_view.json").exists()


def test_module_has_no_writes_runtime_binding_or_execution_behavior() -> None:
    text = MODULE.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "write_bytes(",
        "append_jsonl(",
        "send_order(",
        "place_order(",
        "requests.",
        "urllib.",
        "load_latest_market_state(",
        "load_latest_prediction_warroom_read_model(",
        "runtime_enablement_allowed\": True",
        "loader_binding_runtime_allowed\": True",
        "target_loader_invoked\": True",
        "latest_prediction_warroom_read_model_loader_changed\": True",
        "component_runtime_binding_allowed\": True",
        "ui_code_changed\": True",
        "producer_enabled\": True",
        "scheduler_enabled\": True",
        "warroom_ui_trigger_enabled\": True",
        "view_artifact_write_allowed\": True",
        "would_write_warroom_view_artifact\": True",
        "ps_q19r_scoring_policy_changed\": True",
        "autotrade_trigger_allowed\": True",
        "broker_private_api_allowed\": True",
        "would_send_to_broker\": True",
    )
    for token in forbidden:
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_sample_and_safety_boundaries()
    test_sample_builds_preview_packet_from_real_like_inputs_without_attaching_section()
    test_runner_reads_temp_real_data_files_and_writes_no_artifact(Path("tmp/ps_q20n_selftest"))
    test_module_has_no_writes_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
