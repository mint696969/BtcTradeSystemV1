# path: ./tools/test_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit.py
# desc: Focused pytest guard for PS-Q26M WarRoom live D-hot observation audit.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit import run_warroom_live_d_hot_observation_audit  # noqa: E402

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26M_WARROOM_LIVE_D_HOT_OBSERVATION_AUDIT_2026-07-01.md"


def _write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "hot"
    _write_json(root, "state/collector_vnext/unified_daemon_status.json", {
        "ts": "2026-07-01T07:05:47Z",
        "mode": "RUNNING",
        "daemon": True,
        "cycle_no": 569,
        "lane_health": {"rest_lane": "running", "ws_board_lane": "live", "ws_executions_lane": "live"},
        "consecutive_failures": 0,
        "last_error": None,
    })
    _write_json(root, "state/collector_vnext/unified_status.json", {
        "ts": "2026-07-01T07:05:26Z",
        "mode": "RUNNING",
        "ws_board_lane": {"ws_state": "LIVE", "ws_freshness": "LIVE"},
        "ws_executions_lane": {"ws_state": "LIVE", "ws_freshness": "QUIET"},
        "rate_control": {"summary_state": "NORMAL", "engaged": False},
    })
    _write_json(root, "prediction/status/non_ui_scheduled_producer_status.json", {
        "producer_enabled": False,
        "scheduler_enabled": False,
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_generated_at": "2026-07-01T07:00:22Z",
        "freshness_max_age_sec": 3600,
        "safe_flags": {
            "producer_enabled_false": True,
            "scheduled_loop_enabled_false": True,
            "scheduler_enabled_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "ledger_append_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    })
    _write_json(root, "prediction/latest_prediction_system_result.json", {
        "generated_at": "2026-07-01T07:00:22Z",
        "compact_record_count": 24,
        "original_record_count": 110,
        "read_only": True,
        "non_executing": True,
        "approval_append_requested": False,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
    })
    return root


def test_q26m_doc_markers() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q26m_warroom_live_d_hot_observation_audit=true",
        "selected_human_lane=B_WARROOM_DATA_FRESHNESS_LIVE_D_HOT_OBSERVATION_AUDIT",
        "production_ui_code_changed=false",
        "warroom_ui_cleanup_deferred=true",
        "ready_for_ui_visual_cleanup_intake=true",
        "would_send_to_broker=false",
    ):
        assert marker in text, marker


def test_q26m_live_d_hot_observation_fixture_ready(tmp_path: Path) -> None:
    result = run_warroom_live_d_hot_observation_audit(_fixture_root(tmp_path), now="2026-07-01T07:05:52Z")
    assert result["ok"] is True
    assert result["ready"] is True, result["blockers"]
    assert result["blockers"] == []
    assert result["observed"]["daemon_mode"] == "RUNNING"
    assert result["observed"]["ws_board_freshness"] == "LIVE"
    assert result["observed"]["ws_executions_freshness"] == "QUIET"
    assert result["observed"]["producer_enabled"] is False
    assert result["observed"]["scheduler_enabled"] is False
    assert result["observed"]["prediction_record_count"] == 24
    assert result["ui_entry_reconfirmed"] is True
    assert result["ready_for_ui_visual_cleanup_intake"] is True
    safety = result["safety"]
    assert safety["read_only"] is True
    assert safety["display_only"] is True
    assert safety["non_executing"] is True
    for key in ("production_ui_code_changed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert safety[key] is False


def test_q26m_blocks_when_producer_enabled(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    status_path = root / "prediction/status/non_ui_scheduled_producer_status.json"
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    payload["producer_enabled"] = True
    status_path.write_text(json.dumps(payload), encoding="utf-8")
    result = run_warroom_live_d_hot_observation_audit(root, now="2026-07-01T07:05:52Z")
    assert result["ready"] is False
    assert any("producer_status:producer_enabled_expected_false" in blocker for blocker in result["blockers"])


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root = _fixture_root(Path(temp))
        print(json.dumps(run_warroom_live_d_hot_observation_audit(root, now="2026-07-01T07:05:52Z"), ensure_ascii=False, indent=2))
