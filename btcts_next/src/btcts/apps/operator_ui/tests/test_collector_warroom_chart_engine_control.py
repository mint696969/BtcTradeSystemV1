# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_collector_warroom_chart_engine_control.py
# desc: Source-level guard for Collector page WarRoom Chart Engine management section.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next" / "src" / "btcts" / "apps" / "operator_ui" / "views" / "collector_page.py"


def test_collector_page_has_chart_engine_management_section() -> None:
    text = COLLECTOR_PAGE.read_text(encoding="utf-8-sig")
    assert "warroom_chart_engine_runtime" in text
    assert "chart_engine_runtime_snapshot" in text
    assert "start_chart_engine_detached" in text
    assert "request_chart_engine_safe_stop" in text
    assert "request_chart_engine_restart" in text
    assert "WarRoom Chart Engine Runtime" in text
    assert "Chart 起動" in text
    assert "Chart 安全停止" in text
    assert "Chart 再起動" in text
    assert "read_only_source=true" in text
    assert "broker_send_enabled=false" in text
    assert "prediction_invoked=false" in text
    assert "classifier_invoked=false" in text
