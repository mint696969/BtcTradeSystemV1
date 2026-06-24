# path: ./tools/test_phase4a_prediction_system_ps_q19b_audit_telemetry_split_minimal_guard.py
# desc: Focused guard for PS-Q19B minimal audit/telemetry split.

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btcts.collector_vnext.archive.audit import append_archive_audit  # noqa: E402
from btcts.collector_vnext.telemetry_policy import (  # noqa: E402
    HIGH_FREQUENCY_SUCCESS_EVENTS,
    emit_collector_event,
    should_route_to_telemetry,
)
from btcts.core import telemetry  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19B_AUDIT_TELEMETRY_SPLIT_MINIMAL_2026-06-25.md"

REQUIRED_MARKERS = (
    "ps_q19b_audit_telemetry_split_minimal=true",
    "primary_audit_high_frequency_success_events_removed=true",
    "collector_telemetry_writer_added=true",
    "telemetry_date_partitioned=true",
    "collector_vnext.unified.board_snapshot.completed",
    "collector_vnext.unified.rest_trades.completed",
    "collector_vnext.unified.ws_board.message.received",
    "collector_vnext.unified.ws_executions.message.received",
    "collector_vnext.unified.ws_executions.trade.written",
    "logs/telemetry/collector_vnext/date=YYYY-MM-DD/part-00001.jsonl",
    "logs/telemetry/collector_vnext_archive/date=YYYY-MM-DD/part-00001.jsonl",
    "PS-Q19C_PREDICTION_WARROOM_READ_MODEL",
)

FALSE_BOUNDARIES = (
    "runtime_behavior_changed=false",
    "collector_data_collection_changed=false",
    "collector_market_data_write_changed=false",
    "raw_market_data_deleted=false",
    "prediction_artifact_deleted=false",
    "state_artifact_deleted=false",
    "ui_code_changed=false",
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


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_ps_q19b_spec_declares_split_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_collector_policy_routes_only_high_frequency_info_to_telemetry(tmp_path: Path, monkeypatch) -> None:
    logs_root = tmp_path / "logs"
    monkeypatch.setenv("BTC_TS_LOGS_DIR", str(logs_root))
    monkeypatch.setenv("BTC_TS_MODE", "NORMAL")
    monkeypatch.setenv("BTCTS_TELEMETRY_ENABLED", "1")

    assert should_route_to_telemetry("collector_vnext.unified.ws_executions.trade.written", level="INFO") is True
    assert should_route_to_telemetry("collector_vnext.unified.ws_executions.reconnected", level="WARN") is False

    emit_collector_event(
        "collector_vnext.unified.ws_executions.trade.written",
        level="INFO",
        actor="test",
        site="test",
        payload={"trade_count": 1},
    )
    emit_collector_event(
        "collector_vnext.unified.ws_executions.reconnected",
        level="WARN",
        actor="test",
        site="test",
        payload={"restart_count": 1},
    )

    audit_path = logs_root / "audit.jsonl"
    telemetry_files = list((logs_root / "telemetry" / "collector_vnext").glob("date=*/part-00001.jsonl"))
    assert len(telemetry_files) == 1

    telemetry_rows = _read_jsonl(telemetry_files[0])
    audit_rows = _read_jsonl(audit_path)
    assert [row["event"] for row in telemetry_rows] == ["collector_vnext.unified.ws_executions.trade.written"]
    assert telemetry_rows[0]["payload"]["audit_routed"] is False
    assert [row["event"] for row in audit_rows] == ["collector_vnext.unified.ws_executions.reconnected"]


def test_core_telemetry_uses_date_partition_and_no_primary_audit(tmp_path: Path, monkeypatch) -> None:
    logs_root = tmp_path / "logs"
    monkeypatch.setenv("BTC_TS_LOGS_DIR", str(logs_root))
    monkeypatch.setenv("BTCTS_TELEMETRY_FSYNC_EACH", "0")
    monkeypatch.setenv("BTCTS_TELEMETRY_FILE_LOCK", "0")

    telemetry.emit(
        "collector_vnext.unified.board_snapshot.completed",
        feature="collector_vnext",
        stream="collector_vnext",
        payload={"ok": True},
    )

    files = list((logs_root / "telemetry" / "collector_vnext").glob("date=*/part-00001.jsonl"))
    assert len(files) == 1
    assert (logs_root / "audit.jsonl").exists() is False
    rows = _read_jsonl(files[0])
    assert rows[0]["event"] == "collector_vnext.unified.board_snapshot.completed"
    assert rows[0]["stream"] == "collector_vnext"


def test_archive_info_progress_routes_to_archive_telemetry(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BTCTS_TELEMETRY_ENABLED", "1")
    cfg = SimpleNamespace(hot_root=tmp_path)

    append_archive_audit(cfg, "archive.copy.completed", extra={"plan_count": 1})
    append_archive_audit(cfg, "archive.copy.error", level="WARN", extra={"error_count": 1})

    archive_audit = tmp_path / "logs" / "collector_vnext" / "archive_audit.jsonl"
    telemetry_files = list((tmp_path / "logs" / "telemetry" / "collector_vnext_archive").glob("date=*/part-00001.jsonl"))
    assert len(telemetry_files) == 1
    telemetry_rows = _read_jsonl(telemetry_files[0])
    audit_rows = _read_jsonl(archive_audit)
    assert [row["event"] for row in telemetry_rows] == ["archive.copy.completed"]
    assert [row["event"] for row in audit_rows] == ["archive.copy.error"]


def test_high_frequency_event_set_is_complete() -> None:
    assert HIGH_FREQUENCY_SUCCESS_EVENTS == frozenset(
        {
            "collector_vnext.unified.board_snapshot.completed",
            "collector_vnext.unified.rest_trades.completed",
            "collector_vnext.unified.ws_board.message.received",
            "collector_vnext.unified.ws_executions.message.received",
            "collector_vnext.unified.ws_executions.trade.written",
        }
    )
