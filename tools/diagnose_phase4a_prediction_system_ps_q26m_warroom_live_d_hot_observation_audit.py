# path: ./tools/diagnose_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit.py
# desc: Read-only diagnostic for PS-Q26M WarRoom live D-hot observation audit.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26m_warroom_live_d_hot_observation_audit.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26M_WARROOM_LIVE_D_HOT_OBSERVATION_AUDIT_2026-07-01.md"
UI_ENTRY_FILES = (
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/latest_prediction_warroom_read_model.py",
)
RELATIVE_INPUTS = {
    "daemon_status": "state/collector_vnext/unified_daemon_status.json",
    "unified_status": "state/collector_vnext/unified_status.json",
    "producer_status": "prediction/status/non_ui_scheduled_producer_status.json",
    "latest_prediction": "prediction/latest_prediction_system_result.json",
}


def _read_json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return {}, "missing"
    except Exception as exc:  # pragma: no cover - defensive CLI path
        return {}, f"read_error:{type(exc).__name__}:{exc}"
    return data if isinstance(data, dict) else {}, None


def _parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_sec(value: Any, now: datetime) -> float | None:
    parsed = _parse_ts(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds())


def _bool_map_ok(mapping: dict[str, Any], expectations: dict[str, bool], prefix: str, blockers: list[str]) -> None:
    for key, expected in expectations.items():
        if mapping.get(key) is not expected:
            blockers.append(f"{prefix}:{key}_expected_{str(expected).lower()}_actual_{mapping.get(key)!r}")


def run_warroom_live_d_hot_observation_audit(hot_root: str | Path = DEFAULT_HOT_ROOT, now: datetime | str | None = None) -> dict[str, Any]:
    root = Path(hot_root)
    if isinstance(now, str):
        parsed_now = _parse_ts(now)
        now_dt = parsed_now or datetime.now(timezone.utc)
    else:
        now_dt = now or datetime.now(timezone.utc)
    now_dt = now_dt.astimezone(timezone.utc)

    blockers: list[str] = []
    warnings: list[str] = []
    inputs: dict[str, dict[str, Any]] = {}
    read_errors: dict[str, str] = {}
    for key, rel in RELATIVE_INPUTS.items():
        payload, error = _read_json(root / rel)
        inputs[key] = payload
        if error:
            read_errors[key] = error
            blockers.append(f"input_{key}_{error}:{rel}")

    doc_text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    for marker in (
        "ps_q26m_warroom_live_d_hot_observation_audit=true",
        "selected_human_lane=B_WARROOM_DATA_FRESHNESS_LIVE_D_HOT_OBSERVATION_AUDIT",
        "production_ui_code_changed=false",
        "ready_for_ui_visual_cleanup_intake=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc_text:
            blockers.append(f"doc_marker_required:{marker}")
    for rel in UI_ENTRY_FILES:
        if not (REPO_ROOT / rel).exists():
            blockers.append(f"ui_entry_missing:{rel}")

    daemon = inputs["daemon_status"]
    unified = inputs["unified_status"]
    producer = inputs["producer_status"]
    latest = inputs["latest_prediction"]

    lane_health = daemon.get("lane_health") if isinstance(daemon.get("lane_health"), dict) else {}
    if daemon.get("mode") != "RUNNING":
        blockers.append(f"daemon_mode_not_running:{daemon.get('mode')!r}")
    if daemon.get("daemon") is not True:
        blockers.append("daemon_flag_not_true")
    if daemon.get("consecutive_failures") not in (0, 0.0, None):
        blockers.append(f"daemon_consecutive_failures_nonzero:{daemon.get('consecutive_failures')!r}")
    if daemon.get("last_error") not in (None, ""):
        blockers.append(f"daemon_last_error_present:{daemon.get('last_error')!r}")
    for lane, accepted in {
        "rest_lane": {"running", "normal"},
        "ws_board_lane": {"live", "running"},
        "ws_executions_lane": {"live", "running"},
    }.items():
        if lane_health.get(lane) not in accepted:
            blockers.append(f"daemon_lane_health_not_live:{lane}:{lane_health.get(lane)!r}")

    if unified.get("mode") != "RUNNING":
        blockers.append(f"unified_mode_not_running:{unified.get('mode')!r}")
    ws_board = unified.get("ws_board_lane") if isinstance(unified.get("ws_board_lane"), dict) else {}
    ws_exec = unified.get("ws_executions_lane") if isinstance(unified.get("ws_executions_lane"), dict) else {}
    rate = unified.get("rate_control") if isinstance(unified.get("rate_control"), dict) else {}
    if ws_board.get("ws_state") != "LIVE" or ws_board.get("ws_freshness") != "LIVE":
        blockers.append(f"ws_board_not_live:{ws_board.get('ws_state')!r}/{ws_board.get('ws_freshness')!r}")
    if ws_exec.get("ws_state") != "LIVE" or ws_exec.get("ws_freshness") not in {"LIVE", "QUIET"}:
        blockers.append(f"ws_executions_not_acceptable:{ws_exec.get('ws_state')!r}/{ws_exec.get('ws_freshness')!r}")
    if rate.get("engaged") is True:
        warnings.append("rate_control_engaged_true")
    if rate.get("summary_state") not in {None, "NORMAL"}:
        warnings.append(f"rate_control_summary_state:{rate.get('summary_state')!r}")

    _bool_map_ok(producer, {"producer_enabled": False, "scheduler_enabled": False}, "producer_status", blockers)
    safe_flags = producer.get("safe_flags") if isinstance(producer.get("safe_flags"), dict) else {}
    expected_safe = {
        "producer_enabled_false": True,
        "scheduled_loop_enabled_false": True,
        "scheduler_enabled_false": True,
        "autotrade_trigger_allowed_false": True,
        "broker_private_api_allowed_false": True,
        "ledger_append_allowed_false": True,
        "would_send_to_broker_false": True,
    }
    _bool_map_ok(safe_flags, expected_safe, "producer_safe_flags", blockers)

    _bool_map_ok(latest, {"read_only": True, "non_executing": True}, "latest_prediction", blockers)
    _bool_map_ok(latest, {
        "approval_append_requested": False,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
    }, "latest_prediction", blockers)

    daemon_age = _age_sec(daemon.get("ts"), now_dt)
    unified_age = _age_sec(unified.get("ts"), now_dt)
    prediction_age = _age_sec(latest.get("generated_at"), now_dt)
    status_age = _age_sec(producer.get("last_success_generated_at") or producer.get("last_success_at"), now_dt)
    if daemon_age is not None and daemon_age > 300:
        warnings.append(f"daemon_status_age_sec_gt_300:{round(daemon_age, 3)}")
    if unified_age is not None and unified_age > 300:
        warnings.append(f"unified_status_age_sec_gt_300:{round(unified_age, 3)}")
    if prediction_age is not None and prediction_age > int(producer.get("freshness_max_age_sec") or 3600):
        warnings.append(f"prediction_age_exceeds_status_freshness_max:{round(prediction_age, 3)}")
    if status_age is not None and status_age > int(producer.get("freshness_max_age_sec") or 3600):
        warnings.append(f"producer_success_age_exceeds_freshness_max:{round(status_age, 3)}")

    result = {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "hot_root": str(root),
        "now_utc": now_dt.isoformat().replace("+00:00", "Z"),
        "read_errors": read_errors,
        "observed": {
            "daemon_ts": daemon.get("ts"),
            "daemon_mode": daemon.get("mode"),
            "daemon_cycle_no": daemon.get("cycle_no"),
            "daemon_lane_health": lane_health,
            "unified_status_ts": unified.get("ts"),
            "ws_board_state": ws_board.get("ws_state"),
            "ws_board_freshness": ws_board.get("ws_freshness"),
            "ws_executions_state": ws_exec.get("ws_state"),
            "ws_executions_freshness": ws_exec.get("ws_freshness"),
            "rate_control_summary_state": rate.get("summary_state"),
            "rate_control_engaged": rate.get("engaged"),
            "prediction_generated_at": latest.get("generated_at"),
            "prediction_record_count": latest.get("compact_record_count") or latest.get("record_count"),
            "prediction_original_record_count": latest.get("original_record_count"),
            "producer_enabled": producer.get("producer_enabled"),
            "scheduler_enabled": producer.get("scheduler_enabled"),
            "producer_state": producer.get("producer_state"),
            "last_success_generated_at": producer.get("last_success_generated_at"),
        },
        "ages_sec": {
            "daemon_status": daemon_age,
            "unified_status": unified_age,
            "prediction_generated_at": prediction_age,
            "producer_success_generated_at": status_age,
        },
        "ui_entry_reconfirmed": all((REPO_ROOT / rel).exists() for rel in UI_ENTRY_FILES),
        "ui_entry_files": list(UI_ENTRY_FILES),
        "ready_for_ui_visual_cleanup_intake": not blockers,
        "safety": {
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "production_ui_code_changed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q26M WarRoom live D-hot observation audit")
    parser.add_argument("--hot-root", default=str(DEFAULT_HOT_ROOT))
    parser.add_argument("--now", default=None)
    args = parser.parse_args(argv)
    result = run_warroom_live_d_hot_observation_audit(args.hot_root, args.now)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
