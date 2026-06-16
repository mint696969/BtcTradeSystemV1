# path: ./tools/run_sr_fx_runtime_control_operational_evidence_report.py
# desc: Broker-free runtime_control operational evidence report from S51 wrapper output. Read-only; non-authorizing; no broker calls/no mode changes.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TOOL = "run_sr_fx_runtime_control_operational_evidence_report"
REPORT_VERSION = "runtime_control_operational_evidence_report.v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _read_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return _read_json(path)


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _path_from(paths: Mapping[str, Any], key: str) -> Path | None:
    raw = str(paths.get(key) or "").strip()
    return Path(raw) if raw else None


def _open_incident_count(runtime_control: Mapping[str, Any]) -> int:
    count = 0
    for row in runtime_control.get("incidents") or []:
        if isinstance(row, Mapping) and str(row.get("status") or "").lower() != "closed":
            count += 1
    return count


def build_operational_evidence_report(*, wrapper: Mapping[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    sequence = _as_dict(wrapper.get("sequence"))
    paths = _as_dict(wrapper.get("paths"))
    runtime_control = _as_dict(wrapper.get("runtime_control"))
    safety_lock = _as_dict(wrapper.get("operator_safety_lock"))
    runtime_control_state_path = _path_from(paths, "runtime_control_state")
    final_review_path = _path_from(paths, "final_review_package")
    handoff_path = _path_from(paths, "data_ui_gate_handoff")
    safety_path = _path_from(paths, "execution_safety_harness")
    pre_live_path = _path_from(paths, "pre_live_blocker_report")

    runtime_control_state = _read_optional(runtime_control_state_path)
    final_review = _read_optional(final_review_path)
    handoff = _read_optional(handoff_path)
    safety = _read_optional(safety_path)
    pre_live = _read_optional(pre_live_path)

    runtime_from_state = _as_dict(runtime_control_state)
    runtime_from_final = _as_dict((_as_dict(final_review).get("runtime_control")))
    runtime_from_handoff = _as_dict(_as_dict(_as_dict(handoff).get("execution_boundary")).get("runtime_control"))
    heartbeat = _as_dict(runtime_control.get("heartbeat") or runtime_from_state.get("heartbeat"))
    kill_switch = _as_dict(runtime_control.get("kill_switch") or runtime_from_state.get("kill_switch"))
    command_summary = _as_dict(runtime_control_state.get("command_ledger_summary")) if isinstance(runtime_control_state, Mapping) else {}
    runtime_blocked_by = _as_list(runtime_control.get("blocked_by") or runtime_from_state.get("blocked_by"))
    final_blocked_by = _as_list(_as_dict(final_review).get("execution_boundary_blocked_by"))
    handoff_runtime_blocked_by = _as_list(runtime_from_handoff.get("blocked_by"))
    handoff_next_actions = _as_list(_as_dict(_as_dict(handoff).get("execution_boundary")).get("next_actions"))

    propagation_checks = {
        "wrapper_ok": wrapper.get("ok") is True,
        "sequence_complete": sequence.get("sequence_complete") is True,
        "runtime_control_state_exists": runtime_control_state_path is not None and runtime_control_state_path.exists(),
        "final_review_exists": final_review_path is not None and final_review_path.exists(),
        "handoff_exists": handoff_path is not None and handoff_path.exists(),
        "runtime_control_present_in_final_review": bool(runtime_from_final.get("present")),
        "runtime_control_present_in_handoff": bool(runtime_from_handoff.get("present")),
        "blocked_by_propagates_to_final_review": set(runtime_blocked_by).issubset(set(final_blocked_by)) if runtime_blocked_by else True,
        "blocked_by_propagates_to_handoff": set(runtime_blocked_by).issubset(set(handoff_runtime_blocked_by)) if runtime_blocked_by else True,
    }
    safety_checks = {
        "wrapper_non_authorizing": safety_lock.get("non_authorizing") is True,
        "wrapper_read_only": wrapper.get("read_only") is True and safety_lock.get("read_only") is True,
        "wrapper_would_send_false": wrapper.get("would_send_to_broker") is False and safety_lock.get("would_send_to_broker") is False,
        "wrapper_mode_changed_false": wrapper.get("mode_changed") is False and safety_lock.get("mode_changed") is False,
        "wrapper_resume_not_authorized": wrapper.get("autotrade_resume_authorized") is False and safety_lock.get("autotrade_resume_authorized") is False,
        "final_review_non_authorizing": _as_dict(final_review).get("autotrade_resume_authorized") is False if final_review is not None else False,
        "handoff_non_authorizing": _as_dict(handoff).get("autotrade_resume_authorized") is False if handoff is not None else False,
    }
    evidence_ok = all(propagation_checks.values()) and all(safety_checks.values())

    return {
        "ok": evidence_ok,
        "tool": TOOL,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "decision": "runtime_control_operational_evidence_collected" if evidence_ok else "runtime_control_operational_evidence_incomplete",
        "runtime_control_clear": bool(runtime_control.get("ok") or runtime_from_state.get("ok")),
        "runtime_control_blocked_by": runtime_blocked_by,
        "evidence": {
            "heartbeat": {
                "fresh": heartbeat.get("fresh"),
                "component": heartbeat.get("component"),
                "observed_at": heartbeat.get("observed_at"),
                "age_sec": heartbeat.get("age_sec"),
                "max_age_sec": heartbeat.get("max_age_sec"),
                "blocked_by": _as_list(heartbeat.get("blocked_by")),
            },
            "kill_switch": {
                "active": bool(kill_switch.get("active")),
                "action": kill_switch.get("action"),
                "reason": kill_switch.get("reason"),
                "source": kill_switch.get("source"),
                "command_id": kill_switch.get("command_id"),
            },
            "incidents": {
                "count": len(runtime_control.get("incidents") or runtime_from_state.get("incidents") or []),
                "open_count": _open_incident_count(runtime_control or runtime_from_state),
                "rows": list(runtime_control.get("incidents") or runtime_from_state.get("incidents") or []),
            },
            "command_ledger": {
                "exists": command_summary.get("exists"),
                "latest_command_id": command_summary.get("latest_command_id"),
                "latest_command_type": command_summary.get("latest_command_type"),
                "latest_target": command_summary.get("latest_target"),
                "latest_accepted": command_summary.get("latest_accepted"),
                "read_only": command_summary.get("read_only", True),
                "would_send_to_broker": command_summary.get("would_send_to_broker", False),
            },
            "propagation": {
                "runtime_control_state_path": str(runtime_control_state_path) if runtime_control_state_path else None,
                "final_review_path": str(final_review_path) if final_review_path else None,
                "handoff_path": str(handoff_path) if handoff_path else None,
                "final_review_blocked_by": final_blocked_by,
                "handoff_runtime_blocked_by": handoff_runtime_blocked_by,
                "handoff_next_actions": handoff_next_actions,
            },
        },
        "checks": {
            **propagation_checks,
            **safety_checks,
            "safety_report_exists": safety_path is not None and safety_path.exists(),
            "pre_live_report_exists": pre_live_path is not None and pre_live_path.exists(),
        },
        "source_status": {
            "wrapper_out_present": True,
            "runtime_control_state_present": runtime_control_state is not None,
            "final_review_present": final_review is not None,
            "handoff_present": handoff is not None,
            "safety_present": safety is not None,
            "pre_live_present": pre_live is not None,
        },
        "operator_safety_lock": {
            "non_authorizing": True,
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
        },
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
        "paths": {
            "runtime_control_state": str(runtime_control_state_path) if runtime_control_state_path else None,
            "execution_safety_harness": str(safety_path) if safety_path else None,
            "pre_live_blocker_report": str(pre_live_path) if pre_live_path else None,
            "final_review_package": str(final_review_path) if final_review_path else None,
            "data_ui_gate_handoff": str(handoff_path) if handoff_path else None,
        },
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build broker-free runtime_control operational evidence report from S51 wrapper JSON output.")
    parser.add_argument("--wrapper-out", required=True, help="Path to S51 wrapper JSON output.")
    parser.add_argument("--out", default="", help="Optional report output JSON path.")
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    try:
        wrapper = _read_json(Path(args.wrapper_out))
        payload = build_operational_evidence_report(wrapper=wrapper)
    except Exception as exc:
        payload = {
            "ok": False,
            "tool": TOOL,
            "report_version": REPORT_VERSION,
            "generated_at": _utc_now_iso(),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["runtime_control_operational_evidence_report_failed"],
            "operator_safety_lock": {
                "non_authorizing": True,
                "read_only": True,
                "would_send_to_broker": False,
                "mode_changed": False,
                "autotrade_resume_authorized": False,
                "final_human_review_required": True,
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
        }
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
