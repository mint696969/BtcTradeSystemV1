# path: ./btcts_next/src/btcts/apps/sr_fx_data_ui_gate_handoff_once.py
# desc: SR-FX Data/UI Integrity Gate handoff summary. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.collector_vnext.config import load_config

STAGE = "sr_fx_data_ui_gate_handoff_once"
HANDOFF_VERSION = "sr_fx_data_ui_gate_handoff.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_root() -> Path:
    return load_config().roots()["state"]


def _paths() -> dict[str, Path]:
    root = _state_root()
    return {
        "final_review_package": root / "operator_ui" / "sr_fx_final_review_package.json",
        "handoff": root / "operator_ui" / "sr_fx_data_ui_gate_handoff.json",
    }


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return path


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _next_execution_actions(blockers: list[str]) -> list[str]:
    actions: list[str] = []
    if "private_readiness_not_confirmed" in blockers or "account_not_clear_for_new_auto_entry" in blockers:
        actions.append("resolve_or_explicitly_accept_existing_fx_positions_and_open_orders")
    if "reconciliation_not_clean" in blockers:
        actions.append("rerun_private_reconciliation_until_clean")
    if "order_preview_not_ok" in blockers:
        actions.append("fix_order_preview_inputs_before_live_contract")
    if "bitflyer_order_send_flag_disabled" in blockers:
        actions.append("keep_bitflyer_order_send_disabled_until_final_human_approval")
    if "autotrade_live_order_flag_disabled" in blockers:
        actions.append("keep_autotrade_live_order_disabled_until_final_human_approval")
    if "order_sender_not_implemented" in blockers:
        actions.append("implement_and_review_order_sender_before_any_live_order")
    if "observer_run_missing" in blockers or "observer_run_not_fresh_for_live_target" in blockers:
        actions.append("run_fresh_autotrade_observer_cycle_before_live_readiness")
    if "runtime_health_blocked" in blockers:
        actions.append("clear_autotrade_runtime_health_blockers")
    if "execution_safety_harness_not_ready" in blockers or "sr_fx_live_readiness_not_ready" in blockers:
        actions.append("rerun_live_readiness_contract_and_execution_safety_harness_after_fixes")
    if "pre_live_blocker_report_not_clear" in blockers:
        actions.append("rerun_pre_live_blocker_report_until_primary_blockers_clear")
    if "runtime_control_not_confirmed" in blockers or "runtime_control_snapshot_missing" in blockers:
        actions.append("create_or_refresh_runtime_control_snapshot_before_final_review")
    if "runtime_control_not_clear" in blockers or "heartbeat_stale" in blockers or "heartbeat_missing" in blockers:
        actions.append("clear_runtime_control_heartbeat_kill_switch_incident_blockers")
    if "open_incident_present" in blockers:
        actions.append("resolve_or_explicitly_close_runtime_incident_before_live_review")
    if "kill_switch_active" in blockers:
        actions.append("keep_autotrade_halted_until_kill_switch_is_cleared_by_protocol")
    actions.append("require_final_human_review_before_any_mode_change")
    return list(dict.fromkeys(actions))


def build_sr_fx_data_ui_gate_handoff_payload(
    *,
    final_review_package: Mapping[str, Any],
    generated_at: str | None = None,
    paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    package = dict(final_review_package)
    summary = dict(package.get("summary") or {})
    checks = dict(package.get("checks") or {})
    execution_blockers = _list(package.get("execution_boundary_blocked_by"))
    runtime_control = dict(package.get("runtime_control") or {})
    data_ui_ready = bool(package.get("ok")) and bool(package.get("data_ui_integrity_ready_for_final_human_review"))
    execution_clear = bool(package.get("execution_boundary_clear"))

    safety_lock = {
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
    }

    return {
        "stage": STAGE,
        "handoff_version": HANDOFF_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "ok": data_ui_ready,
        "handoff_complete": data_ui_ready,
        "decision": (
            "data_ui_integrity_gate_complete_execution_boundary_blocked"
            if data_ui_ready and not execution_clear
            else "data_ui_integrity_gate_complete_execution_boundary_clear_but_not_authorized"
            if data_ui_ready
            else "data_ui_integrity_gate_not_complete"
        ),
        "completed_scope": {
            "sr_fx_public_private_identity_aligned": bool(checks.get("identity_ok")),
            "sr_fx_public_ws_data_ui_lineage_ready": data_ui_ready,
            "primary_lineage": summary.get("data_ui_primary_lineage"),
            "service_stale": summary.get("data_ui_service_stale"),
            "public_market_ready": bool(summary.get("public_market_ready")),
            "market_uid": summary.get("market_uid"),
            "product_code": summary.get("product_code"),
        },
        "execution_boundary": {
            "clear": execution_clear,
            "blocked_by": execution_blockers,
            "next_actions": _next_execution_actions(execution_blockers),
            "public_market_ready": bool(checks.get("public_market_ready")),
            "private_readiness_clear": bool(checks.get("private_readiness_clear")),
            "live_readiness_contract_ready": bool(checks.get("live_readiness_contract_ready")),
            "execution_safety_harness_ready": bool(checks.get("execution_safety_harness_ready")),
            "pre_live_blocker_report_clear": bool(checks.get("pre_live_blocker_report_clear")),
            "runtime_control_clear": bool(checks.get("runtime_control_clear")),
            "runtime_control": {
                "present": bool(runtime_control.get("present")),
                "clear": bool(runtime_control.get("clear")),
                "source": runtime_control.get("source"),
                "path": runtime_control.get("path"),
                "blocked_by": _list(runtime_control.get("blocked_by")),
                "kill_switch_active": bool(runtime_control.get("kill_switch_active")),
                "heartbeat_fresh": runtime_control.get("heartbeat_fresh"),
                "incident_count": runtime_control.get("incident_count"),
            },
        },
        "safety_lock": safety_lock,
        "source_package_decision": package.get("decision"),
        "source_package_version": package.get("package_version"),
        "source_package_generated_at": package.get("generated_at"),
        "warnings": [
            "handoff_is_not_autotrade_resume_authorization",
            "execution_boundary_must_clear_separately",
            "human_final_review_required_before_any_mode_change",
        ],
        "blocked_by": [] if data_ui_ready else ["final_review_package_not_data_ui_ready", *_list(package.get("blocked_by"))],
        "paths": {key: str(value) for key, value in dict(paths or {}).items()},
        **safety_lock,
    }


def build_from_state() -> dict[str, Any]:
    paths = _paths()
    package = _read_json(paths["final_review_package"])
    payload = build_sr_fx_data_ui_gate_handoff_payload(final_review_package=package, paths=paths)
    _write_json(paths["handoff"], payload)
    return payload


def main() -> int:
    try:
        payload = build_from_state()
    except Exception as exc:
        try:
            paths = _paths()
            out_path = paths["handoff"]
        except Exception:
            paths = {}
            out_path = Path("sr_fx_data_ui_gate_handoff.json")
        payload = {
            "stage": STAGE,
            "handoff_version": HANDOFF_VERSION,
            "generated_at": _utc_now_iso(),
            "ok": False,
            "handoff_complete": False,
            "decision": "data_ui_gate_handoff_failed",
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_data_ui_gate_handoff_failed"],
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
            "mode_changed": False,
            "read_only": True,
            "would_send_to_broker": False,
            "paths": {key: str(value) for key, value in paths.items()},
        }
        try:
            _write_json(out_path, payload)
        except Exception:
            pass
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
