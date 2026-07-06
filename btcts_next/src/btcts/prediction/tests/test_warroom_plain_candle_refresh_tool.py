# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candle_refresh_tool.py
# desc: Verify the non-UI WarRoom plain candle refresh PowerShell launcher stays bounded and read-only.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
TOOL = REPO_ROOT / "tools" / "refresh_warroom_plain_candles.ps1"


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
