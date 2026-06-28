# path: ./tools/test_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_executor.py
# desc: Focused guard for PS-Q23M gated legacy latest shrink executor.

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import build_latest_prediction_warroom_read_model  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once import (  # noqa: E402
    REQUIRED_CONFIRMATION,
    RUNNER_VERSION,
    build_compact_legacy_latest_payload,
    run_legacy_latest_shrink_once,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23M_GATED_LEGACY_LATEST_SHRINK_EXECUTOR_2026-06-28.md"
TOOL = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once.py"


def _sample_payload(record_count: int = 30) -> dict:
    records = []
    for idx in range(record_count):
        horizon = [15, 60, 300, 900][idx % 4]
        records.append({
            "family": "directional" if idx % 2 == 0 else "range",
            "generated_at": "2026-06-28T17:22:28Z",
            "horizon_sec": horizon,
            "horizon_key": str(horizon),
            "primary_label": "up" if idx % 2 == 0 else "flat",
            "confidence": "medium",
            "score": 0.01 * idx,
            "usable": True,
            "warnings": [],
            "drivers": [],
            "values_snapshot": {},
            "read_only": True,
            "non_executing": True,
            "would_send_to_broker": False,
            "would_write_runtime_artifact": False,
            "would_append_ledger": False,
        })
    return {
        "generated_at": "2026-06-28T17:22:28Z",
        "read_only": True,
        "non_executing": True,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "forecast_batch": {
            "generated_at": "2026-06-28T17:22:28Z",
            "read_only": True,
            "non_executing": True,
            "family_count": 2,
            "horizon_count": 4,
            "record_count": len(records),
            "records": records,
        },
    }


def test_spec_declares_gated_no_default_write_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q23m_gated_legacy_latest_shrink_executor=true",
        "legacy_latest_shrink_default_blocked=true",
        "legacy_latest_shrink_executed=false",
        "explicit_confirmation_required=SHRINK_D_HOT_LEGACY_LATEST_TO_COMPACT_READ_MODEL_COMPAT_ONCE",
        "backup_before_replace_required=true",
        "compact_read_model_compatible_payload=true",
        "scheduler_action_changed=false",
        "runtime_artifact_write_changed=false",
        "broker_autotrade=false",
    ):
        assert marker in text, marker


def test_compact_payload_is_smaller_and_read_model_compatible() -> None:
    payload = _sample_payload(40)
    compact = build_compact_legacy_latest_payload(distributed_payload=payload, now_utc="2026-06-28T17:23:00Z")
    assert compact["legacy_latest_shrunk_by"] == RUNNER_VERSION
    assert compact["original_record_count"] == 40
    assert 0 < compact["compact_record_count"] < 40
    assert compact["forecast_batch"]["record_count"] == compact["compact_record_count"]
    read_model = build_latest_prediction_warroom_read_model(payload=compact, market_state={}, market_diag={}, now_utc="2026-06-28T17:23:00Z")
    assert read_model["ok"] is True
    assert read_model["record_count"] == compact["compact_record_count"]
    assert read_model["runtime_artifact_write_allowed"] is False
    assert read_model["broker_private_api_allowed"] is False


def test_default_live_call_is_blocked_no_write() -> None:
    result = run_legacy_latest_shrink_once(
        hot_root=Path(r"D:\btc_ts_hot"),
        operator_acknowledged=False,
        execute_legacy_latest_shrink_once=False,
        confirmation="",
        require_clean_tree=False,
        allow_dirty_tree_for_test=True,
    )
    assert result["ok"] is True
    assert result["success"] is False
    assert result["execution_state"] == "ps_q23m_legacy_latest_shrink_blocked_no_write"
    for reason in (
        "operator_acknowledgement_required",
        "execute_legacy_latest_shrink_once_flag_required",
        "exact_legacy_latest_shrink_confirmation_required",
    ):
        assert reason in result["blocked_reasons"]
    assert result["legacy_latest_shrink_executed"] is False
    assert result["latest_prediction_artifact_written"] is False
    assert result["status_artifact_written"] is False
    assert result["latest_manifest_written"] is False
    assert result["run_sidecars_written"] is False
    assert result["runtime_artifact_write_enabled"] is False
    assert result["backup_written"] is False
    assert result["scheduler_action_changed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_test_root_execute_writes_backup_and_compact_only_under_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        latest = root / "prediction/latest_prediction_system_result.json"
        manifest = root / "prediction/latest_manifest.json"
        run_dir = root / "prediction/runs/2026-06-28/172228_test"
        run_dir.mkdir(parents=True)
        payload = _sample_payload(32)
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        records_path = run_dir / "forecast_records.jsonl"
        records_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in payload["forecast_batch"]["records"]), encoding="utf-8")
        for name, body in {
            "summary.json": {"generated_at": payload["generated_at"], "record_count": 32, "family_count": 2, "horizon_count": 4},
            "forecast_batch_summary.json": {"generated_at": payload["generated_at"], "record_count": 32, "family_count": 2, "horizon_count": 4},
            "safety.json": {"broker_execution_requested": False, "command_ledger_append_requested": False, "approval_append_requested": False},
        }.items():
            (run_dir / name).write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        manifest.write_text(json.dumps({
            "generated_at": payload["generated_at"],
            "record_count": 32,
            "run_dir": "prediction/runs/2026-06-28/172228_test",
            "sidecars": {
                "summary": "prediction/runs/2026-06-28/172228_test/summary.json",
                "forecast_batch_summary": "prediction/runs/2026-06-28/172228_test/forecast_batch_summary.json",
                "forecast_records": "prediction/runs/2026-06-28/172228_test/forecast_records.jsonl",
                "safety": "prediction/runs/2026-06-28/172228_test/safety.json",
            },
        }, ensure_ascii=False), encoding="utf-8")
        result = run_legacy_latest_shrink_once(
            hot_root=root,
            operator_acknowledged=True,
            execute_legacy_latest_shrink_once=True,
            confirmation=REQUIRED_CONFIRMATION,
            require_clean_tree=False,
            allow_test_root=True,
            allow_dirty_tree_for_test=True,
        )
        assert result["success"] is True
        assert result["legacy_latest_shrink_executed"] is True
        assert result["latest_prediction_artifact_written"] is True
        assert result["backup_written"] is True
        assert result["status_artifact_written"] is False
        assert result["latest_manifest_written"] is False
        assert result["run_sidecars_written"] is False
        assert result["scheduler_action_changed"] is False
        shrunk = json.loads(latest.read_text(encoding="utf-8"))
        assert shrunk["compact_record_count"] < shrunk["original_record_count"]
        assert (root / result["backup_relative_path"]).exists()


def test_tool_has_no_scheduler_broker_or_autotrade_code() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for forbidden in (
        "Set-ScheduledTask",
        "Enable-ScheduledTask",
        "Disable-ScheduledTask",
        "Register-ScheduledTask",
        "New-ScheduledTaskTrigger",
        "send_order(",
        "place_order(",
    ):
        assert forbidden not in text, forbidden


if __name__ == "__main__":
    test_spec_declares_gated_no_default_write_contract()
    test_compact_payload_is_smaller_and_read_model_compatible()
    test_default_live_call_is_blocked_no_write()
    test_test_root_execute_writes_backup_and_compact_only_under_gate()
    test_tool_has_no_scheduler_broker_or_autotrade_code()
    print(json.dumps({"ok": True}))
