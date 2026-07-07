# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_collector_warroom_chart_engine_control.py
# desc: Source-level guard for Collector page Chart Engine lifecycle integration.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
COLLECTOR_PAGE = REPO_ROOT / "btcts_next" / "src" / "btcts" / "apps" / "operator_ui" / "views" / "collector_page.py"


def test_collector_buttons_integrate_chart_engine_lifecycle_without_extra_chart_buttons() -> None:
    text = COLLECTOR_PAGE.read_text(encoding="utf-8-sig")
    assert "warroom_chart_engine_runtime" in text
    assert "chart_engine_runtime_snapshot" in text
    assert "start_chart_engine_detached" in text
    assert "request_chart_engine_safe_stop" in text
    assert "request_chart_engine_restart" in text
    assert "_request_unified_start" in text
    assert "_request_unified_safe_stop" in text
    assert "_request_unified_restart" in text
    assert "linked_chart_engine_action" in text
    assert "Chart Engine は Collector 起動・停止・再起動ボタンに連動します。" in text
    assert "Chart 起動" not in text
    assert "Chart 安全停止" not in text
    assert "Chart 再起動" not in text
    assert "read_only_source=true" in text
    assert "broker_send_enabled=false" in text
    assert "prediction_invoked=false" in text
    assert "classifier_invoked=false" in text


def test_unified_stop_remains_available_when_only_chart_engine_is_active() -> None:
    panel_text = (REPO_ROOT / "btcts_next" / "src" / "btcts" / "apps" / "operator_ui" / "components" / "collector_top_panels.py").read_text(encoding="utf-8-sig")
    page_text = COLLECTOR_PAGE.read_text(encoding="utf-8-sig")
    assert "linked_runtime_active" in panel_text
    assert "stop_restart_target_active = bool(stack_active or linked_runtime_active)" in panel_text
    assert "disabled=(not stop_restart_target_active) or safe_stop_pending" in panel_text
    assert "disabled=(not stop_restart_target_active) or restart_pending or safe_stop_pending" in panel_text
    assert "chart_engine_snapshot = chart_engine_runtime_snapshot()" in page_text
    assert 'linked_runtime_active=bool(chart_engine_snapshot.get("active"))' in page_text
    assert 'linked_runtime_label="Chart Engine"' in page_text
