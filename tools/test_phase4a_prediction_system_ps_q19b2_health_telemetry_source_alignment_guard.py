# path: ./tools/test_phase4a_prediction_system_ps_q19b2_health_telemetry_source_alignment_guard.py
# desc: Focused guard for PS-Q19B2 Health telemetry source alignment.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from btcts.apps.operator_ui import health_data_service as svc  # noqa: E402
from btcts.apps.operator_ui.health_audit_read_model import (  # noqa: E402
    build_health_audit_input,
    read_recent_audit_rows,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19B2_HEALTH_TELEMETRY_SOURCE_ALIGNMENT_2026-06-25.md"

REQUIRED_MARKERS = (
    "ps_q19b2_health_telemetry_source_alignment=true",
    "health_activity_source_uses_telemetry=true",
    "health_primary_audit_no_longer_required_for_success_activity_graph=true",
    "bounded_health_event_input=audit_primary + telemetry_collector_vnext",
    "telemetry_collector_vnext_path=logs/telemetry/collector_vnext/date=YYYY-MM-DD/part-00001.jsonl",
    "PS-Q19C_PREDICTION_WARROOM_READ_MODEL",
)

FALSE_BOUNDARIES = (
    "runtime_behavior_changed=false",
    "runtime_trading_behavior_changed=false",
    "collector_data_collection_changed=false",
    "collector_market_data_write_changed=false",
    "raw_market_data_deleted=false",
    "prediction_artifact_deleted=false",
    "state_artifact_deleted=false",
    "ui_render_structure_changed=false",
    "warroom_real_prediction_widget_enabled=false",
    "real_prediction_widget_rendering_allowed=false",
    "real_prediction_widget_render_invoked=false",
    "streamlit_real_widget_render_invoked=false",
    "component_runtime_binding_allowed=false",
    "runtime_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "ledger_append_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_spec_declares_health_telemetry_source_alignment() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_health_event_input_reads_primary_audit_and_collector_telemetry(tmp_path: Path, monkeypatch) -> None:
    logs = tmp_path / "logs"
    monkeypatch.setenv("BTC_TS_LOGS_DIR", str(logs))

    _write_jsonl(
        logs / "audit.jsonl",
        [
            {
                "ts": "2026-06-24T16:13:16Z",
                "event": "watchdog.restart.completed",
                "level": "INFO",
                "payload": {"ok": True},
            },
            {
                "ts": "2026-06-24T16:13:17Z",
                "event": "collector_vnext.unified.ws_executions.connected",
                "level": "INFO",
                "payload": {"topic": "ws_executions"},
            },
        ],
    )
    _write_jsonl(
        logs / "telemetry" / "collector_vnext" / "date=2026-06-24" / "part-00001.jsonl",
        [
            {
                "ts": "2026-06-24T16:13:52Z",
                "event": "collector_vnext.unified.rest_trades.completed",
                "level": "INFO",
                "payload": {"topic": "rest_trades", "audit_routed": False, "telemetry_routed": True},
            },
            {
                "ts": "2026-06-24T16:13:53Z",
                "event": "collector_vnext.unified.ws_executions.trade.written",
                "level": "INFO",
                "payload": {"topic": "ws_executions", "audit_routed": False, "telemetry_routed": True},
            },
        ],
    )

    rows = read_recent_audit_rows(max_lines=20)
    events = [row.get("event") for row in rows]
    assert "watchdog.restart.completed" in events
    assert "collector_vnext.unified.rest_trades.completed" in events
    assert "collector_vnext.unified.ws_executions.trade.written" in events
    assert any(row.get("health_source_kind") == "audit_primary" for row in rows)
    assert any(row.get("health_source_kind") == "telemetry_collector_vnext" for row in rows)

    audit_input = build_health_audit_input(range_key="1h")
    payload = audit_input.as_dict()
    assert payload["ps_q19b_health_event_input"] is True
    assert payload["includes_telemetry"] is True
    assert payload["source_counts"]["audit_primary"] == 2
    assert payload["source_counts"]["telemetry_collector_vnext"] == 2


def test_health_series_source_kind_is_no_longer_audit_only() -> None:
    rows = [
        {
            "ts": "2026-06-24T16:13:52Z",
            "event": "collector_vnext.unified.rest_trades.completed",
            "payload": {"topic": "rest_trades", "elapsed_ms": 10.0},
            "health_source_kind": "telemetry_collector_vnext",
        },
        {
            "ts": "2026-06-24T16:13:53Z",
            "event": "collector_vnext.unified.ws_executions.trade.written",
            "payload": {"topic": "ws_executions"},
            "health_source_kind": "telemetry_collector_vnext",
        },
    ]
    series = svc.build_recent_api_ws_series(range_key="1h", audit_rows=rows)
    assert series
    assert series[-1]["source_kind"] == "health_event_activity_series"


def test_health_caption_and_warning_text_do_not_claim_audit_is_primary() -> None:
    health_text = (REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/texts/health.py").read_text(encoding="utf-8")
    panels_text = (REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/health_chart_panels.py").read_text(encoding="utf-8")
    assert "audit-based activity estimation" not in health_text
    assert "audit tail did not fully cover" not in panels_text
    assert "health event input did not fully cover" in panels_text
    data_service_text = (REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/health_data_service.py").read_text(encoding="utf-8")
    assert "audit_tail_" not in data_service_text
    assert "health_event_input_did_not_cover_full_window" in data_service_text
