# path: ./tools/test_phase4a_autotrade_milestone_dx_pre_armed_dry_run_approval_record_append_preflight_status_guard.py
# desc: Guard S58 approval record append preflight/status remains status-only and non-authorizing.

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "tools/run_sr_fx_runtime_control_report_sequence_once.py"
EVIDENCE = REPO_ROOT / "tools/run_sr_fx_runtime_control_operational_evidence_report.py"
CLEARANCE = REPO_ROOT / "tools/run_sr_fx_runtime_control_clearance_runbook_report.py"
ROLLUP = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_readiness_blocker_rollup.py"
PACKET = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_human_review_packet.py"
STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_request_status.py"
VALIDATOR = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_evidence_dry_run_validator.py"
PREFLIGHT = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_preflight_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s58_pre_armed_dry_run_approval_record_append_preflight_status_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (PREFLIGHT, VALIDATOR, STATUS, PACKET, ROLLUP, CLEARANCE, EVIDENCE, WRAPPER, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "armed_dry_run_authorized=True", "live_authorized=True", "approval_recorded=True", "human_approval_recorded=True", "operator_acknowledgement_recorded=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_persisted=True", "while True")
REQUIRED_ACKS = ("review_all_runtime_control_evidence", "review_all_remaining_execution_boundary_blockers", "confirm_no_broker_send_or_mode_change_is_authorized_by_this_packet", "confirm_pre_armed_dry_run_authorization_requires_separate_later_slice", "confirm_final_human_review_required_before_any_mode_change")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _seed_state(state_root: Path) -> None:
    state = state_root / "collector_vnext"
    _write_json(state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json", {"ok": True, "data_ui_integrity_ready_for_final_human_review": True, "autotrade_resume_authorized": False, "blocked_by": [], "summary": {"primary_lineage": "continuous_ws", "service_stale": False}, "context": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"}, "read_only": True, "would_send_to_broker": False})
    _write_json(state / "public" / "bitflyer_fx_public_market_readiness.json", {"public_market_readiness": {"ok": True, "product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "blocked_by": [], "warnings": [], "read_only": True, "would_send_to_broker": False}})
    _write_json(state / "private" / "bitflyer_fx_readiness.json", {"readiness": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "private_state_known_and_fresh": True, "account_clear_for_new_auto_entry": True, "blocked_by": [], "read_only": True, "would_send_to_broker": False}})
    _write_json(state / "private" / "bitflyer_fx_live_readiness_contract.json", {"live_readiness_contract": {"ready": False, "product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "blocked_by": ["order_sender_not_implemented"], "read_only": True, "would_send_to_broker": False}})


def _evidence(path: Path, *, valid: bool) -> Path:
    payload = {"evidence_id": "approval_evidence_guard_valid_001" if valid else "bad_evidence_guard_001", "approval_scope": "PRE_ARMED_DRY_RUN_REVIEW_ONLY" if valid else "LIVE", "target_mode": "PRE_ARMED_DRY_RUN" if valid else "LIVE_MIN_SIZE", "requested_by": "guard_operator" if valid else "", "requested_at": "2026-06-17T00:00:20Z" if valid else "", "operator_identity": "guard_human_operator" if valid else "", "human_review_packet_ready": True if valid else False, "approval_recording_requested": False, "command_ledger_append_requested": False, "mode_change_requested": False, "reason_codes": ["operator_final_human_review", "pre_armed_dry_run_review_only"] if valid else ["invalid"], "acknowledgements": list(REQUIRED_ACKS) if valid else ["review_all_runtime_control_evidence"]}
    _write_json(path, payload)
    return path


def _run_case(case_name: str, extra_args: list[str], *, valid_evidence: bool) -> dict[str, Any]:
    case_root = TMP_ROOT / case_name
    if case_root.exists():
        shutil.rmtree(case_root)
    data_root = case_root / "data"; logs_root = case_root / "logs"; state_root = case_root / "state"; runtime_root = case_root / "runtime_hot"
    for path in (data_root, logs_root, state_root, runtime_root):
        path.mkdir(parents=True, exist_ok=True)
    _seed_state(state_root)
    wrapper_out = case_root / "wrapper_out.json"; evidence_out = case_root / "evidence_report.json"; clearance_out = case_root / "clearance_runbook.json"; rollup_out = case_root / "pre_armed_rollup.json"; packet_out = case_root / "human_review_packet.json"; status_out = case_root / "approval_request_status.json"; approval_evidence = _evidence(case_root / "approval_evidence.json", valid=valid_evidence); validator_out = case_root / "approval_evidence_validator.json"; preflight_out = case_root / "approval_record_append_preflight_status.json"
    wrapper_proc = subprocess.run([sys.executable, str(WRAPPER), "--data-root", str(data_root), "--logs-root", str(logs_root), "--state-root", str(state_root), "--runtime-root", str(runtime_root), "--now", "2026-06-17T00:00:10Z", "--out", str(wrapper_out), *extra_args], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    evidence_proc = subprocess.run([sys.executable, str(EVIDENCE), "--wrapper-out", str(wrapper_out), "--out", str(evidence_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    clearance_proc = subprocess.run([sys.executable, str(CLEARANCE), "--evidence-report", str(evidence_out), "--out", str(clearance_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    rollup_proc = subprocess.run([sys.executable, str(ROLLUP), "--clearance-runbook", str(clearance_out), "--out", str(rollup_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    packet_proc = subprocess.run([sys.executable, str(PACKET), "--readiness-rollup", str(rollup_out), "--out", str(packet_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    status_proc = subprocess.run([sys.executable, str(STATUS), "--human-review-packet", str(packet_out), "--out", str(status_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    validator_proc = subprocess.run([sys.executable, str(VALIDATOR), "--approval-request-status", str(status_out), "--approval-evidence", str(approval_evidence), "--out", str(validator_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    preflight_proc = subprocess.run([sys.executable, str(PREFLIGHT), "--approval-evidence-validator", str(validator_out), "--out", str(preflight_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    try:
        preflight = json.loads(preflight_proc.stdout)
    except Exception as exc:
        preflight = {"ok": False, "error": f"preflight stdout was not JSON: {exc}", "stdout_tail": preflight_proc.stdout[-1600:]}
    return {"case": case_name, "wrapper_returncode": wrapper_proc.returncode, "evidence_returncode": evidence_proc.returncode, "clearance_returncode": clearance_proc.returncode, "rollup_returncode": rollup_proc.returncode, "packet_returncode": packet_proc.returncode, "status_returncode": status_proc.returncode, "validator_returncode": validator_proc.returncode, "preflight_returncode": preflight_proc.returncode, "preflight": preflight}


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}"); continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {path.relative_to(REPO_ROOT)}: {exc}")
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")
        blocked_imports = _imports_from(path).intersection({"requests", "httpx", "ccxt", "pybitflyer"})
        if blocked_imports:
            failures.append(f"forbidden imports in {path.relative_to(REPO_ROOT)}: {sorted(blocked_imports)}")

    clear_valid = _run_case("clear_valid", [], valid_evidence=True)
    clear_invalid = _run_case("clear_invalid", [], valid_evidence=False)
    blocked_valid = _run_case("blocked_valid", ["--heartbeat-observed-at", "2026-06-17T00:00:00Z", "--heartbeat-max-age-sec", "5", "--incident-open", "1", "--incident-reason", "guard_open_incident", "--kill-switch-active", "1", "--kill-switch-action", "HALT_AND_CANCEL", "--kill-switch-reason", "guard_kill_switch"], valid_evidence=True)
    cv = clear_valid["preflight"]; ci = clear_invalid["preflight"]; bv = blocked_valid["preflight"]
    checks = {
        "clear_valid_pipeline_returncode_zero": all(clear_valid[name] == 0 for name in ("wrapper_returncode", "evidence_returncode", "clearance_returncode", "rollup_returncode", "packet_returncode", "status_returncode", "validator_returncode", "preflight_returncode")),
        "clear_valid_preflight_ready_not_appended": cv.get("approval_record_append_preflight_ready") is True and cv.get("decision") == "approval_record_append_preflight_ready_not_appended" and cv.get("approval_record_persisted") is False,
        "clear_valid_no_ledger_or_mode_request": cv.get("approval_ledger_appended") is False and cv.get("command_ledger_appended") is False and cv.get("mode_change_requested") is False and cv.get("mode_change_authorized") is False,
        "clear_valid_not_authorizing": cv.get("pre_armed_dry_run_authorized") is False and cv.get("live_authorized") is False and cv.get("autotrade_resume_authorized") is False,
        "clear_invalid_pipeline_returncode_zero": all(clear_invalid[name] == 0 for name in ("wrapper_returncode", "evidence_returncode", "clearance_returncode", "rollup_returncode", "packet_returncode", "status_returncode", "validator_returncode", "preflight_returncode")),
        "clear_invalid_preflight_blocked_visible": ci.get("approval_record_append_preflight_ready") is False and ci.get("preflight_blockers") and any("approval_evidence_not_valid" in item for item in ci.get("preflight_blockers", [])),
        "blocked_valid_pipeline_returncode_zero": all(blocked_valid[name] == 0 for name in ("wrapper_returncode", "evidence_returncode", "clearance_returncode", "rollup_returncode", "packet_returncode", "status_returncode", "validator_returncode", "preflight_returncode")),
        "blocked_valid_preflight_blocked_by_source_status": bv.get("approval_record_append_preflight_ready") is False and "approval_request_status_not_ready_for_human_review" in (bv.get("preflight_blockers") or []),
        "blocked_valid_no_ledger_or_mode_request": bv.get("approval_ledger_appended") is False and bv.get("command_ledger_appended") is False and bv.get("mode_change_requested") is False,
        "blocked_valid_not_authorizing": bv.get("pre_armed_dry_run_authorized") is False and bv.get("live_authorized") is False and bv.get("autotrade_resume_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DX: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_dx_pre_armed_dry_run_approval_record_append_preflight_status_guard", "status": "closed" if not failures else "open", "contract": {"approval_record_append_preflight_status_present": PREFLIGHT.exists(), "clear_valid_preflight_ready_without_append": checks.get("clear_valid_preflight_ready_not_appended", False), "clear_invalid_preflight_blocked_visible": checks.get("clear_invalid_preflight_blocked_visible", False), "blocked_source_status_blocks_preflight": checks.get("blocked_valid_preflight_blocked_by_source_status", False), "no_ledger_append_no_mode_request": checks.get("clear_valid_no_ledger_or_mode_request", False) and checks.get("blocked_valid_no_ledger_or_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("clear_valid_not_authorizing", False) and checks.get("blocked_valid_not_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"clear_valid": {"ok": cv.get("ok"), "decision": cv.get("decision"), "approval_record_append_preflight_ready": cv.get("approval_record_append_preflight_ready"), "approval_record_persisted": cv.get("approval_record_persisted"), "approval_ledger_appended": cv.get("approval_ledger_appended"), "command_ledger_appended": cv.get("command_ledger_appended"), "mode_change_requested": cv.get("mode_change_requested")}, "clear_invalid": {"ok": ci.get("ok"), "decision": ci.get("decision"), "approval_record_append_preflight_ready": ci.get("approval_record_append_preflight_ready"), "preflight_blockers": ci.get("preflight_blockers")}, "blocked_valid": {"ok": bv.get("ok"), "decision": bv.get("decision"), "approval_record_append_preflight_ready": bv.get("approval_record_append_preflight_ready"), "preflight_blockers": bv.get("preflight_blockers")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
