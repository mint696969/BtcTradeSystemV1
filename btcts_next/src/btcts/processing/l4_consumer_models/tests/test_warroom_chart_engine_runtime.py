# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_warroom_chart_engine_runtime.py
# desc: Verify WarRoom Chart Engine runtime is an L4 UI-managed read-only process boundary.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui import warroom_chart_engine_runtime as runtime  # noqa: E402


def test_runtime_declares_l4_ui_managed_layer() -> None:
    assert runtime.WARROOM_CHART_ENGINE_LAYER == "L4_CONSUMER_MODEL_OPERATOR_UI_RUNTIME"
    assert runtime.WARROOM_CHART_ENGINE_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_engine_runtime"
    assert runtime.DEFAULT_TIMEFRAMES_SEC == "60,300,900,1800,3600,86400"
    assert runtime.DEFAULT_RETENTION_DAYS == 92


def test_runtime_paths_are_under_state_warroom_chart_engine(tmp_path: Path) -> None:
    paths = runtime.chart_engine_paths(tmp_path)
    assert paths["state_dir"] == tmp_path / "state" / "warroom_chart_engine"
    assert paths["status"].name == "status.json"
    assert paths["health"].name == "health.json"
    assert paths["request"].name == "request.json"
    assert paths["lock"].name == "runtime.lock.json"
    assert paths["stdout"].name == "runtime.stdout.log"
    assert paths["stderr"].name == "runtime.stderr.log"


def test_runtime_snapshot_is_safe_when_state_missing(tmp_path: Path) -> None:
    snapshot = runtime.chart_engine_runtime_snapshot(tmp_path)
    assert snapshot["ok"] is True
    assert snapshot["active"] is False
    assert snapshot["gap_policy"] == "absent_candles_no_synthetic_null"
    assert snapshot["broker_send_enabled"] is False
    assert snapshot["order_intent_submitted"] is False
    assert snapshot["prediction_invoked"] is False
    assert snapshot["classifier_invoked"] is False


def test_runtime_request_writes_read_only_control_file(tmp_path: Path) -> None:
    ok, msg = runtime.request_chart_engine_safe_stop(tmp_path)
    assert ok is True
    assert "request_id=" in msg
    payload = runtime.chart_engine_paths(tmp_path)["request"].read_text(encoding="utf-8-sig")
    assert "safe_stop" in payload
    assert "operator_ui" in payload
    assert "broker_send_enabled" in payload
    assert "prediction_invoked" in payload


def test_run_tool_uses_safe_endpoint_query_interpolation_and_append_boundary() -> None:
    repo_root = Path(__file__).resolve().parents[6]
    text = (repo_root / "tools" / "run_warroom_chart_engine.ps1").read_text(encoding="utf-8-sig")
    assert '"${Endpoint}?max_candles=$MaxCandles&timeframe_sec=$TimeframeSec"' in text
    assert '"$Endpoint?max_candles=$MaxCandles&timeframe_sec=$TimeframeSec"' not in text
    assert "append_boundary=update_state.source_part_file+byte_offset" in text
    assert "resume_from_update_state_no_reaggregate_processed_trades" in text


def test_run_tool_preserves_last_endpoint_payload_on_exit_status() -> None:
    repo_root = Path(__file__).resolve().parents[6]
    text = (repo_root / "tools" / "run_warroom_chart_engine.ps1").read_text(encoding="utf-8-sig")
    assert "$LastEndpointPayload = $null" in text
    assert "$script:LastEndpointPayload = $payload" in text
    assert 'Write-ChartEngineStatus -Mode "STOPPED" -LastAction "runtime_exit" -Extra $script:LastEndpointPayload' in text
    assert 'Write-ChartEngineHealth -Ok $true -Reason "runtime_exit" -Extra $script:LastEndpointPayload' in text


def test_run_tool_keeps_status_payload_lightweight_without_candle_arrays() -> None:
    repo_root = Path(__file__).resolve().parents[6]
    text = (repo_root / "tools" / "run_warroom_chart_engine.ps1").read_text(encoding="utf-8-sig")
    assert "function ConvertTo-EndpointSummary" in text
    assert "extra = (ConvertTo-EndpointSummary -Payload $Extra)" in text
    assert "candles = $Payload.candles" not in text


def test_start_helper_logs_child_process_and_explicitly_runs_forever() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8-sig")
    assert "runtime.stdout.log" in source
    assert "runtime.stderr.log" in source
    assert '"-MaxCycles"' in source
    assert '"0"' in source
    assert "command_args" in source
    assert "stdout_path" in source
    assert "stderr_path" in source
    assert "data_root_normalized" in source


def test_run_tool_promotes_endpoint_summary_to_top_level_status_fields() -> None:
    repo_root = Path(__file__).resolve().parents[6]
    text = (repo_root / "tools" / "run_warroom_chart_engine.ps1").read_text(encoding="utf-8-sig")
    assert '$endpointSummary.Contains("meta")' in text
    assert '$payload.latest_candle_end_ts_utc = $endpointSummary["meta"].end_ts_utc' in text
    assert '$payload.candle_count = $endpointSummary["candle_count"]' in text


def test_runtime_normalizes_nested_data_dir_to_hot_root(tmp_path: Path) -> None:
    hot = tmp_path / "hot"
    nested = hot / "data"
    (nested / "market_data").mkdir(parents=True)
    assert runtime._normalize_runtime_root(nested) == hot
    assert runtime._normalize_runtime_root(hot) == hot


def test_candle_store_cli_exposes_history_rebuild_mode() -> None:
    source = Path(runtime.__file__).with_name("warroom_candle_store.py").read_text(encoding="utf-8-sig")
    assert "--rebuild-history" in source
    assert "--history-raw-root" in source
    assert "rebuild_candle_store_from_trade_history" in source
    assert "_trade_parts_asc_from_roots" in source
    assert "later_roots_replace_earlier_roots_by_date_partition" in source
    assert "history_rebuild" in source
    assert "append_boundary" in source


def test_chart_engine_start_clears_stale_request_marker() -> None:
    source = Path("btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/warroom_chart_engine_runtime.py").read_text(encoding="utf-8-sig")
    tool = Path("tools/run_warroom_chart_engine.ps1").read_text(encoding="utf-8-sig")
    assert "def _clear_stale_request_on_start" in source
    assert "cleared_stale_request_on_start" in source
    assert "clearing stale startup request" in tool
    assert "Clear-RequestFile" in tool

