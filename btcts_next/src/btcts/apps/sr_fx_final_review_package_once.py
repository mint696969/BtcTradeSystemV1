# path: ./btcts_next/src/btcts/apps/sr_fx_final_review_package_once.py
# desc: Final SR-FX review package combining Data/UI readiness and execution safety boundaries. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.collector_vnext.config import load_config

STAGE = "sr_fx_final_review_package_once"
PACKAGE_VERSION = "sr_fx_final_review_package.v1"
EXPECTED_PRODUCT_CODE = "FX_BTC_JPY"
EXPECTED_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_root() -> Path:
    return load_config().roots()["state"]


def _paths() -> dict[str, Path]:
    root = _state_root()
    return {
        "data_ui_checkpoint": root / "operator_ui" / "sr_fx_final_readiness_checkpoint.json",
        "lineage_audit": root / "operator_ui" / "sr_fx_data_lineage_parity_audit.json",
        "public_market_readiness": root / "public" / "bitflyer_fx_public_market_readiness.json",
        "private_readiness": root / "private" / "bitflyer_fx_readiness.json",
        "live_readiness_contract": root / "private" / "bitflyer_fx_live_readiness_contract.json",
        "execution_safety_harness": root / "autotrade" / "sr_fx_execution_safety_harness.json",
        "pre_live_blocker_report": root / "autotrade" / "sr_fx_pre_live_blocker_report.json",
        "final_review_package": root / "operator_ui" / "sr_fx_final_review_package.json",
    }


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _read_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _read_json(path)


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return path


def _nested(payload: Mapping[str, Any] | None, key: str) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    value = payload.get(key)
    if isinstance(value, Mapping):
        return dict(value)
    return dict(payload)


def _blocked(payload: Mapping[str, Any] | None, *, nested_key: str | None = None) -> list[str]:
    target = _nested(payload, nested_key) if nested_key else dict(payload or {})
    raw = target.get("blocked_by") or target.get("primary_blockers") or []
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if isinstance(raw, tuple):
        return [str(item) for item in raw]
    return [str(raw)] if raw else []


def _bool(payload: Mapping[str, Any] | None, key: str, *, nested_key: str | None = None, default: bool = False) -> bool:
    target = _nested(payload, nested_key) if nested_key else dict(payload or {})
    return bool(target.get(key, default))


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _identity_ok(*payloads: Mapping[str, Any] | None) -> bool:
    for payload in payloads:
        if not isinstance(payload, Mapping) or not payload:
            continue
        context = dict(payload.get("context") or {}) if isinstance(payload.get("context"), Mapping) else dict(payload)
        product = str(context.get("product_code") or context.get("symbol_raw") or "")
        market_uid = str(context.get("market_uid") or "")
        if product and product != EXPECTED_PRODUCT_CODE:
            return False
        if market_uid and market_uid != EXPECTED_MARKET_UID:
            return False
    return True


def _section(payload: Mapping[str, Any] | None, *keys: str) -> dict[str, Any]:
    current: Mapping[str, Any] | None = payload
    for key in keys:
        if not isinstance(current, Mapping):
            return {}
        value = current.get(key)
        if not isinstance(value, Mapping):
            return {}
        current = value
    return dict(current or {})


def _runtime_control_visibility(
    *,
    execution_safety_harness: Mapping[str, Any] | None,
    pre_live_blocker_report: Mapping[str, Any] | None,
) -> dict[str, Any]:
    safety_runtime = _section(execution_safety_harness, "runtime_control")
    safety_leaf = _nested(execution_safety_harness, "execution_safety_harness")
    report_runtime = _section(pre_live_blocker_report, "runtime_control")
    report_runtime_section = _section(pre_live_blocker_report, "report", "sections", "runtime_control")

    source = "missing"
    runtime = {}
    if report_runtime:
        source = "pre_live_blocker_report.runtime_control"
        runtime = report_runtime
    elif safety_runtime:
        source = "execution_safety_harness.runtime_control"
        runtime = safety_runtime
    elif report_runtime_section:
        source = "pre_live_blocker_report.report.sections.runtime_control"
        runtime = report_runtime_section

    section_summary = dict(report_runtime_section.get("summary") or {}) if isinstance(report_runtime_section.get("summary"), Mapping) else {}
    safety_blocked = _blocked(safety_leaf)
    runtime_blocked = _blocked(runtime)
    section_blocked = _blocked(report_runtime_section)
    runtime_control_blocked_by = list(dict.fromkeys([
        *runtime_blocked,
        *section_blocked,
        *[str(item) for item in safety_leaf.get("runtime_control_blocked_by") or []],
    ]))

    present = bool(runtime or report_runtime_section or safety_leaf.get("runtime_control_ok") is not None)
    ok_values = []
    if runtime:
        ok_values.append(bool(runtime.get("ok")))
    if report_runtime_section:
        ok_values.append(bool(report_runtime_section.get("ok")))
    if safety_leaf.get("runtime_control_ok") is not None:
        ok_values.append(bool(safety_leaf.get("runtime_control_ok")))
    clear = bool(present and all(ok_values) and not runtime_control_blocked_by)

    kill_switch = dict(runtime.get("kill_switch") or {}) if isinstance(runtime.get("kill_switch"), Mapping) else {}
    heartbeat = dict(runtime.get("heartbeat") or {}) if isinstance(runtime.get("heartbeat"), Mapping) else {}
    return {
        "present": present,
        "clear": clear,
        "source": source,
        "path": runtime.get("path"),
        "exists": runtime.get("exists"),
        "blocked_by": runtime_control_blocked_by,
        "warnings": _list(runtime.get("warnings")) + _list(report_runtime_section.get("warnings")),
        "kill_switch_active": bool(kill_switch.get("active") or section_summary.get("kill_switch_active")),
        "kill_switch_action": kill_switch.get("action") or section_summary.get("kill_switch_action"),
        "heartbeat_fresh": heartbeat.get("fresh", section_summary.get("heartbeat_fresh")),
        "heartbeat_component": heartbeat.get("component") or section_summary.get("heartbeat_component"),
        "incident_count": len(runtime.get("incidents") or []) if isinstance(runtime.get("incidents"), list) else section_summary.get("incident_count", 0),
        "read_only": bool(runtime.get("read_only", True)),
        "would_send_to_broker": bool(runtime.get("would_send_to_broker", False)),
        "mode_changed": bool(runtime.get("mode_changed", False)),
    }


def build_sr_fx_final_review_package_payload(
    *,
    data_ui_checkpoint: Mapping[str, Any],
    lineage_audit: Mapping[str, Any] | None = None,
    public_market_readiness: Mapping[str, Any] | None = None,
    private_readiness: Mapping[str, Any] | None = None,
    live_readiness_contract: Mapping[str, Any] | None = None,
    execution_safety_harness: Mapping[str, Any] | None = None,
    pre_live_blocker_report: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
    paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    p = dict(paths or {})
    public_leaf = _nested(public_market_readiness, "public_market_readiness")
    private_leaf = _nested(private_readiness, "readiness")
    live_leaf = _nested(live_readiness_contract, "live_readiness_contract")
    safety_leaf = _nested(execution_safety_harness, "execution_safety_harness")
    blocker_report_leaf = _nested(pre_live_blocker_report, "report")
    runtime_control = _runtime_control_visibility(
        execution_safety_harness=execution_safety_harness,
        pre_live_blocker_report=pre_live_blocker_report,
    )

    data_ui_ready = bool(data_ui_checkpoint.get("ok")) and bool(data_ui_checkpoint.get("data_ui_integrity_ready_for_final_human_review"))
    public_ready = bool(public_leaf.get("ok"))
    private_ready = bool(private_leaf.get("private_state_known_and_fresh")) and bool(private_leaf.get("account_clear_for_new_auto_entry"))
    live_contract_ready = bool(live_leaf.get("ready"))
    safety_ready = bool(safety_leaf.get("ok"))
    blocker_report_ready = bool(blocker_report_leaf.get("ok")) if blocker_report_leaf else False

    execution_boundary_blocked_by: list[str] = []
    if not public_ready:
        execution_boundary_blocked_by.append("public_market_readiness_not_confirmed")
        execution_boundary_blocked_by.extend(_blocked(public_market_readiness, nested_key="public_market_readiness"))
    if not private_ready:
        execution_boundary_blocked_by.append("private_readiness_not_confirmed")
        execution_boundary_blocked_by.extend(_blocked(private_readiness, nested_key="readiness"))
    if not live_contract_ready:
        execution_boundary_blocked_by.append("live_readiness_contract_not_ready")
        execution_boundary_blocked_by.extend(_blocked(live_readiness_contract, nested_key="live_readiness_contract"))
    if execution_safety_harness is None:
        execution_boundary_blocked_by.append("execution_safety_harness_missing")
    elif not safety_ready:
        execution_boundary_blocked_by.append("execution_safety_harness_not_ready")
        execution_boundary_blocked_by.extend(_blocked(execution_safety_harness, nested_key="execution_safety_harness"))
    if pre_live_blocker_report is None:
        execution_boundary_blocked_by.append("pre_live_blocker_report_missing")
    elif not blocker_report_ready:
        execution_boundary_blocked_by.append("pre_live_blocker_report_not_clear")
        execution_boundary_blocked_by.extend(_blocked(pre_live_blocker_report, nested_key="report"))
    if not runtime_control["present"]:
        execution_boundary_blocked_by.append("runtime_control_not_confirmed")
        execution_boundary_blocked_by.append("runtime_control_snapshot_missing")
    elif not runtime_control["clear"]:
        execution_boundary_blocked_by.append("runtime_control_not_clear")
        execution_boundary_blocked_by.extend(runtime_control["blocked_by"])
    if runtime_control["would_send_to_broker"]:
        execution_boundary_blocked_by.append("runtime_control_unexpected_broker_send_signal")
    if runtime_control["mode_changed"]:
        execution_boundary_blocked_by.append("runtime_control_unexpected_mode_change")
    if not runtime_control["read_only"]:
        execution_boundary_blocked_by.append("runtime_control_not_read_only")

    identity_ok = _identity_ok(data_ui_checkpoint, lineage_audit, public_leaf, private_leaf, live_leaf, safety_leaf)
    if not identity_ok:
        execution_boundary_blocked_by.append("execution_market_identity_mismatch")

    unexpected_send_flags = []
    for name, payload in {
        "data_ui_checkpoint": data_ui_checkpoint,
        "lineage_audit": lineage_audit,
        "public_market_readiness": public_leaf,
        "private_readiness": private_leaf,
        "live_readiness_contract": live_leaf,
        "execution_safety_harness": safety_leaf,
        "pre_live_blocker_report": blocker_report_leaf,
    }.items():
        if isinstance(payload, Mapping) and bool(payload.get("would_send_to_broker")):
            unexpected_send_flags.append(name)
    if unexpected_send_flags:
        execution_boundary_blocked_by.append("unexpected_would_send_to_broker_flag")

    execution_boundary_blocked_by = list(dict.fromkeys(execution_boundary_blocked_by))
    data_ui_blocked_by = list(data_ui_checkpoint.get("blocked_by") or [])
    package_blocked_by = [] if data_ui_ready else ["data_ui_integrity_checkpoint_not_ready", *[str(x) for x in data_ui_blocked_by]]

    return {
        "stage": STAGE,
        "package_version": PACKAGE_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "ok": data_ui_ready,
        "data_ui_integrity_ready_for_final_human_review": data_ui_ready,
        "execution_boundary_clear": not execution_boundary_blocked_by,
        "execution_boundary_blocked_by": execution_boundary_blocked_by,
        "autotrade_resume_authorized": False,
        "final_human_review_required": True,
        "mode_changed": False,
        "read_only": True,
        "would_send_to_broker": False,
        "decision": (
            "data_ui_ready_but_execution_safety_boundaries_remain_separate"
            if data_ui_ready
            else "hold_final_review_package_until_data_ui_ready"
        ),
        "blocked_by": list(dict.fromkeys(package_blocked_by)),
        "warnings": [
            "package_does_not_authorize_autotrade_resume",
            "execution_boundary_clear_is_informational_only",
            "private_rest_live_contract_safety_harness_and_human_approval_remain_required",
        ],
        "checks": {
            "data_ui_checkpoint_ok": bool(data_ui_checkpoint.get("ok")),
            "data_ui_final_review_ready": bool(data_ui_checkpoint.get("data_ui_integrity_ready_for_final_human_review")),
            "data_ui_does_not_authorize_resume": not bool(data_ui_checkpoint.get("autotrade_resume_authorized")),
            "identity_ok": identity_ok,
            "public_market_ready": public_ready,
            "private_readiness_clear": private_ready,
            "live_readiness_contract_ready": live_contract_ready,
            "execution_safety_harness_ready": safety_ready,
            "pre_live_blocker_report_clear": blocker_report_ready,
            "runtime_control_present": bool(runtime_control["present"]),
            "runtime_control_clear": bool(runtime_control["clear"]),
            "no_unexpected_send_flags": not unexpected_send_flags,
        },
        "runtime_control": runtime_control,
        "summary": {
            "product_code": EXPECTED_PRODUCT_CODE,
            "market_uid": EXPECTED_MARKET_UID,
            "data_ui_primary_lineage": (data_ui_checkpoint.get("summary") or {}).get("primary_lineage") if isinstance(data_ui_checkpoint.get("summary"), Mapping) else None,
            "data_ui_service_stale": (data_ui_checkpoint.get("summary") or {}).get("service_stale") if isinstance(data_ui_checkpoint.get("summary"), Mapping) else None,
            "public_market_ready": public_ready,
            "private_state_known_and_fresh": bool(private_leaf.get("private_state_known_and_fresh")),
            "account_clear_for_new_auto_entry": bool(private_leaf.get("account_clear_for_new_auto_entry")),
            "live_readiness_contract_ready": live_contract_ready,
            "execution_safety_harness_ready": safety_ready,
            "pre_live_blocker_report_clear": blocker_report_ready,
            "runtime_control_clear": bool(runtime_control["clear"]),
            "runtime_control_source": runtime_control["source"],
        },
        "source_status": {
            "data_ui_checkpoint_present": True,
            "lineage_audit_present": lineage_audit is not None,
            "public_market_readiness_present": public_market_readiness is not None,
            "private_readiness_present": private_readiness is not None,
            "live_readiness_contract_present": live_readiness_contract is not None,
            "execution_safety_harness_present": execution_safety_harness is not None,
            "pre_live_blocker_report_present": pre_live_blocker_report is not None,
            "runtime_control_present": bool(runtime_control["present"]),
        },
        "paths": {key: str(value) for key, value in p.items()},
    }


def build_from_state() -> dict[str, Any]:
    paths = _paths()
    data_ui_checkpoint = _read_json(paths["data_ui_checkpoint"])
    payload = build_sr_fx_final_review_package_payload(
        data_ui_checkpoint=data_ui_checkpoint,
        lineage_audit=_read_optional(paths["lineage_audit"]),
        public_market_readiness=_read_optional(paths["public_market_readiness"]),
        private_readiness=_read_optional(paths["private_readiness"]),
        live_readiness_contract=_read_optional(paths["live_readiness_contract"]),
        execution_safety_harness=_read_optional(paths["execution_safety_harness"]),
        pre_live_blocker_report=_read_optional(paths["pre_live_blocker_report"]),
        paths=paths,
    )
    _write_json(paths["final_review_package"], payload)
    return payload


def main() -> int:
    try:
        payload = build_from_state()
    except Exception as exc:
        try:
            paths = _paths()
            out_path = paths["final_review_package"]
        except Exception:
            paths = {}
            out_path = Path("sr_fx_final_review_package.json")
        payload = {
            "stage": STAGE,
            "package_version": PACKAGE_VERSION,
            "generated_at": _utc_now_iso(),
            "ok": False,
            "data_ui_integrity_ready_for_final_human_review": False,
            "execution_boundary_clear": False,
            "autotrade_resume_authorized": False,
            "final_human_review_required": True,
            "mode_changed": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_final_review_package_failed"],
            "paths": {key: str(value) for key, value in paths.items()},
            "read_only": True,
            "would_send_to_broker": False,
        }
        try:
            _write_json(out_path, payload)
        except Exception:
            pass
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
