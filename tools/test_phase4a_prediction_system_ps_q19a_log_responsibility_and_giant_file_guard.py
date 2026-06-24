# path: ./tools/test_phase4a_prediction_system_ps_q19a_log_responsibility_and_giant_file_guard.py
# desc: Focused guard for PS-Q19A log responsibility split design and giant hot audit containment tool.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19A_LOG_RESPONSIBILITY_AND_GIANT_FILE_GUARD_2026-06-25.md"
ROTATE_TOOL = REPO_ROOT / "tools/rotate_hot_audit_log_ps_q19a.py"

REQUIRED_MARKERS = (
    "ps_q19a_log_responsibility_gate=true",
    "giant_active_audit_file_observed=true",
    "warroom_realtime_prediction_work_deferred_until_log_gate=true",
    "audit_responsibility_too_broad=true",
    "high_frequency_success_events_written_to_audit=true",
    "single_active_file_append_without_rotation=true",
    "audit=important_low_frequency_human_and_safety_events",
    "telemetry=high_frequency_collector_api_ws_latency_and_throughput_events",
    "state=small_current_atomic_json_for_ui_and_guards",
    "tools/rotate_hot_audit_log_ps_q19a.py",
    "tools/prune_giant_log_candidates_ps_q19a.py",
    "prune_giant_log_candidates_tool_added=true",
    "active_hot_audit_delete_allowed=false",
    "hot_archive_log_delete_allowed=true",
    "cold_log_delete_allowed_with_include_cold=true",
    "PS-Q19B_AUDIT_TELEMETRY_SPLIT_MINIMAL",
)

FALSE_BOUNDARIES = (
    "runtime_behavior_changed=false",
    "collector_behavior_changed=false",
    "ui_code_changed=false",
    "prediction_runtime_changed=false",
    "collector_runtime_behavior_changed=false",
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

HIGH_FREQ_EVENTS = (
    "collector_vnext.unified.board_snapshot.completed",
    "collector_vnext.unified.rest_trades.completed",
    "collector_vnext.unified.ws_executions.message.received",
    "collector_vnext.unified.ws_executions.trade.written",
)


def test_ps_q19a_spec_declares_log_responsibility_split_and_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker
    for event in HIGH_FREQ_EVENTS:
        assert event in text, event
    assert "delete_performed=False" not in text  # use explicit text block semantics, not Python repr
    assert "avoid_delete_by_default=true" in text
    assert "avoid_compress_by_default=true" in text


def test_ps_q19a_rotation_tool_dry_run_blocks_without_fake_active_audit(tmp_path: Path) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            str(ROTATE_TOOL),
            "--root",
            str(tmp_path),
            "--allow-test-root",
            "--min-size-bytes",
            "1",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["dry_run"] is True
    assert payload["active_audit_exists"] is False
    assert any("active_audit_missing" in item for item in payload["blockers"])
    assert payload["delete_performed"] is False
    assert payload["compress_performed"] is False
    assert payload["would_send_to_broker"] is False


def test_ps_q19a_rotation_tool_execute_rotates_test_root_with_ack(tmp_path: Path) -> None:
    active = tmp_path / "logs" / "audit.jsonl"
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_text('{"event":"old"}\n', encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(ROTATE_TOOL),
            "--root",
            str(tmp_path),
            "--allow-test-root",
            "--min-size-bytes",
            "1",
            "--execute",
            "--ack",
            "PS_Q19A_ROTATE_HOT_AUDIT_LOG",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["dry_run"] is False
    assert payload["archive_exists_after"] is True
    assert payload["marker_written"] is True
    assert payload["delete_performed"] is False
    assert payload["compress_performed"] is False
    marker = active.read_text(encoding="utf-8")
    assert "audit.rotation.ps_q19a.completed" in marker
    assert "would_send_to_broker" in marker
    assert Path(payload["archive_path"]).read_text(encoding="utf-8") == '{"event":"old"}\n'
