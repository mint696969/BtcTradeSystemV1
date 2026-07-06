# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candle_refresh_tool.py
# desc: Verify the non-UI WarRoom plain candle refresh PowerShell launcher stays bounded and read-only.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
TOOL = REPO_ROOT / "tools" / "refresh_warroom_plain_candles.ps1"
RUN_TOOL = REPO_ROOT / "tools" / "run_warroom_chart_engine.ps1"
SERVE_TOOL = REPO_ROOT / "tools" / "serve_warroom_plain_candles.ps1"


def test_refresh_tool_exists_and_calls_plain_candle_refresh_module() -> None:
    text = TOOL.read_text(encoding="utf-8-sig")
    assert "btcts.prediction.warroom_plain_candle_refresh" in text
    assert "--raw-root" in text
    assert "--cache-root" in text
    assert "--range-minutes" in text
    assert "--max-files" in text
    assert "--max-trades" in text
    assert "--latest-scan-days" in text
    assert "--latest-scan-files-per-day" in text


def test_refresh_tool_defaults_are_dhot_bounded_and_non_ui() -> None:
    text = TOOL.read_text(encoding="utf-8-sig")
    assert '$RawRoot = "D:\\btc_ts_hot"' in text
    assert '$CacheRoot = "D:\\btc_ts_hot"' in text
    assert '$RangeMinutes = 180' in text
    assert '$MaxFiles = 8' in text
    assert '$MaxTrades = 500000' in text
    assert '$LatestScanDays = 7' in text
    assert '$LatestScanFilesPerDay = 24' in text
    assert "read_only=true" in text
    assert "broker_send_enabled=false" in text
    assert "prediction_invoked=false" in text
    assert "classifier_invoked=false" in text
    assert "ui_trigger_enabled=false" in text
    assert "streamlit_invoked=false" in text


def test_refresh_tool_has_dry_run_and_does_not_launch_ui_or_broker() -> None:
    text = TOOL.read_text(encoding="utf-8-sig")
    assert "[switch]$DryRun" in text
    assert "dry_run=true command" in text
    lowered = text.lower()
    assert "streamlit run" not in lowered
    assert "send_to_broker" not in lowered
    assert "broker_private" not in lowered


def test_serve_tool_exposes_read_only_chart_endpoint_without_ui_or_broker() -> None:
    text = SERVE_TOOL.read_text(encoding="utf-8-sig")
    assert "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server" in text
    assert "WARROOM_PLAIN_CANDLE_CHART_ENDPOINT" in text
    assert "127.0.0.1" in text
    assert "8765" in text
    assert "read_only=true" in text
    assert "broker_send_enabled=false" in text
    assert "order_intent_submitted=false" in text
    assert "prediction_invoked=false" in text
    assert "classifier_invoked=false" in text
    assert "ui_trigger_enabled=false" in text
    assert "streamlit_invoked=false" in text
    lowered = text.lower()
    assert "streamlit run" not in lowered
    assert "send_to_broker" not in lowered
    assert "broker_private" not in lowered


def test_run_tool_combines_read_only_server_and_candle_store_update_loop() -> None:
    text = RUN_TOOL.read_text(encoding="utf-8-sig")
    assert "warroom_chart_data_server" in text
    assert "warroom_candle_store" in text
    assert "--timeframes-sec" in text
    assert "--retention-days" in text
    assert "--max-bootstrap-bytes" in text
    assert "candle_store_retention_days" in text
    assert "absent_candles_no_synthetic_null" in text
    assert "status.json" in text
    assert "health.json" in text
    assert "request.json" in text
    assert "runtime.lock.json" in text
    assert "Get-RequestedAction" in text
    assert "${Endpoint}?max_candles=$MaxCandles&timeframe_sec=$TimeframeSec" in text
    assert "append_boundary=update_state.source_part_file+byte_offset" in text
    assert "resume_from_update_state_no_reaggregate_processed_trades" in text
    assert "$LastEndpointPayload = $null" in text
    assert "$script:LastEndpointPayload = $payload" in text
    assert "function ConvertTo-EndpointSummary" in text
    assert "extra = (ConvertTo-EndpointSummary -Payload $Extra)" in text
    assert '$endpointSummary.Contains("meta")' in text
    assert '$payload.latest_candle_end_ts_utc = $endpointSummary["meta"].end_ts_utc' in text
    assert '$payload.candle_count = $endpointSummary["candle_count"]' in text
    assert "Write-ChartEngineStatus -Mode \"STOPPED\" -LastAction \"runtime_exit\" -Extra $script:LastEndpointPayload" in text
    assert "Start-Job" in text
    assert "Invoke-RestMethod" in text
    assert "WARROOM_PLAIN_CANDLE_CHART_ENDPOINT" in text
    assert "127.0.0.1" in text
    assert "8765" in text
    assert "[int]$IntervalSec = 5" in text
    assert "[int]$RetentionDays = 92" in text
    assert "[string]$TimeframesSec = \"60,300,900,1800,3600,86400\"" in text
    assert "[switch]$Once" in text
    assert "[switch]$DryRun" in text
    assert "read_only=true" in text
    assert "broker_send_enabled=false" in text
    assert "order_intent_submitted=false" in text
    assert "prediction_invoked=false" in text
    assert "classifier_invoked=false" in text
    assert "ui_trigger_enabled=false" in text
    assert "streamlit_invoked=false" in text
    lowered = text.lower()
    assert "streamlit run" not in lowered
    assert "send_to_broker" not in lowered
    assert "broker_private" not in lowered

