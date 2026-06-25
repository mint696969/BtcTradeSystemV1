# path: ./tools/test_phase4a_prediction_system_ps_q20j_disabled_helper_real_data_dry_run_sample.py
# desc: Focused guard for PS-Q20J disabled helper real-data dry-run sample.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for item in (REPO_ROOT, SRC_ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

from tools.sample_phase4a_prediction_system_ps_q20j_disabled_helper_real_data_dry_run_sample import (  # noqa: E402
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
    SAMPLE_VERSION,
    build_disabled_helper_real_data_dry_run_sample,
    run_disabled_helper_real_data_dry_run_sample,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q20J_DISABLED_HELPER_REAL_DATA_DRY_RUN_SAMPLE_2026-06-26.md"
MODULE = REPO_ROOT / "tools/sample_phase4a_prediction_system_ps_q20j_disabled_helper_real_data_dry_run_sample.py"

REQUIRED_MARKERS = (
    "ps_q20j_disabled_helper_real_data_dry_run_sample=true",
    "sample_only=true",
    "hot_data_read_only=true",
    "stdout_only=true",
    "helper_disabled_by_default=true",
    "target_loader_invoked=false",
    "latest_prediction_warroom_read_model_loader_changed=false",
)

FALSE_BOUNDARIES = (
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
            "collector_ts": "2026-06-25T19:19:40Z",
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "semantic_observer_status": "healthy",
            "best_bid": 9578989.0,
            "best_ask": 9581832.0,
            "spread": 2843.0,
            "mid_price": 9580410.5,
            "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:2",
            "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
        }
    return {
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "symbol_raw": "FX_BTC_JPY",
        "collector_ts": "2026-06-25T19:19:39Z",
        "trust_state": "quarantined",
        "continuity_state": "transition",
        "interpretation_bucket": "reanchor_required",
        "semantic_observer_status": "broken",
        "best_bid": 9581833.0,
        "best_ask": 9581832.0,
        "spread": -1.0,
        "mid_price": 9581832.5,
        "source_series_id": "collector_main-stream-bitflyer-unified_board_ws:series:1",
        "source_stream_session_id": "collector_main-stream-bitflyer-unified_board_ws",
    }


def test_spec_declares_sample_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_sample_default_disabled_uses_real_like_inputs_without_attaching() -> None:
    result = build_disabled_helper_real_data_dry_run_sample(
        prediction_payload=_payload(),
        market_overview_rows=[_row(ok=False), _row(ok=True)],
        prediction_path="D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
        market_overview_path="D:/btc_ts_hot/data/market_state/.../part-00001.jsonl",
        now_utc="2026-06-25T12:00:00Z",
    )
    assert result["sample_version"] == SAMPLE_VERSION
    assert result["sample_state"] == "disabled_helper_real_data_dry_run_sample_ready"
    assert result["sample_only"] is True
    assert result["hot_data_read_only"] is True
    assert result["helper_state"] == "explicit_read_only_loader_binding_helper_disabled"
    assert result["helper_disabled_by_default"] is True
    assert result["enable_explicit_read_only_loader_binding"] is False
    assert result["dry_run_ready"] is True
    assert result["optional_section_attached"] is False
    assert result["output_model_has_optional_section"] is False
    assert result["adapter_allowed_for_requested_lane"] is True
    assert result["selected_row_summary"]["spread"] == 2843.0
    assert result["target_loader_invoked"] is False
    assert result["would_send_to_broker"] is False


def test_sample_explicit_preview_attaches_in_memory_only_when_requested() -> None:
    result = build_disabled_helper_real_data_dry_run_sample(
        prediction_payload=_payload(),
        market_overview_rows=[_row(ok=True)],
        prediction_path="D:/btc_ts_hot/prediction/latest_prediction_system_result.json",
        market_overview_path="D:/btc_ts_hot/data/market_state/.../part-00001.jsonl",
        enable_explicit_read_only_loader_binding=True,
        now_utc="2026-06-25T12:00:00Z",
    )
    assert result["helper_state"] == "explicit_read_only_loader_binding_helper_attached"
    assert result["enable_explicit_read_only_loader_binding"] is True
    assert result["dry_run_ready"] is True
    assert result["optional_section_attached"] is True
    assert result["output_model_has_optional_section"] is True
    assert result["runtime_loader_invoked"] is False
    assert result["would_write_warroom_view_artifact"] is False
    assert result["would_send_to_broker"] is False


def test_runner_reads_temp_real_data_files_and_writes_no_artifact(tmp_path: Path) -> None:
    prediction = tmp_path / "prediction" / "latest_prediction_system_result.json"
    overview = tmp_path / "data" / "market_state" / "exchange=bitflyer" / "symbol=FX_BTC_JPY" / "type=market.overview" / "date=2026-06-25" / "part-00001.jsonl"
    prediction.parent.mkdir(parents=True)
    overview.parent.mkdir(parents=True)
    prediction.write_text(json.dumps(_payload()), encoding="utf-8")
    overview.write_text(json.dumps(_row(ok=False)) + "\n" + json.dumps(_row(ok=True)) + "\n", encoding="utf-8")

    result = run_disabled_helper_real_data_dry_run_sample(
        data_root=tmp_path,
        prediction_path="prediction/latest_prediction_system_result.json",
        market_overview_path="data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date=2026-06-25/part-00001.jsonl",
        tail_rows=10,
        now_utc="2026-06-25T12:00:00Z",
    )
    assert result["ok"] is True
    assert result["market_overview_tail_row_count"] == 2
    assert result["optional_section_attached"] is False
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
    test_sample_default_disabled_uses_real_like_inputs_without_attaching()
    test_sample_explicit_preview_attaches_in_memory_only_when_requested()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        test_runner_reads_temp_real_data_files_and_writes_no_artifact(Path(tmp))
    test_module_has_no_writes_runtime_binding_or_execution_behavior()
    print('{"ok": true}')
