# path: ./tools/test_phase4a_autotrade_milestone_dy_pre_armed_dry_run_approval_record_ledger_status_guard.py
# desc: Guard S59 approval record ledger status reader remains read-only and non-authorizing.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_ledger_status.py"
PREFLIGHT = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_preflight_status.py"
VALIDATOR = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_evidence_dry_run_validator.py"
REQUEST_STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_request_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s59_pre_armed_dry_run_approval_record_ledger_status_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (STATUS, PREFLIGHT, VALIDATOR, REQUEST_STATUS, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "armed_dry_run_authorized=True", "live_authorized=True", "approval_recorded=True", "human_approval_recorded=True", "operator_acknowledgement_recorded=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_persisted_by_this_tool=True", "while True")
REQUIRED_ACKS = ("review_all_runtime_control_evidence", "review_all_remaining_execution_boundary_blockers", "confirm_no_broker_send_or_mode_change_is_authorized_by_this_packet", "confirm_pre_armed_dry_run_authorization_requires_separate_later_slice", "confirm_final_human_review_required_before_any_mode_change")


def _write_jsonl(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    valid = {"record_kind": "pre_armed_dry_run_review_approval_record", "record_id": "approval_record_guard_valid_001", "evidence_id": "approval_evidence_guard_valid_001", "approval_scope": "PRE_ARMED_DRY_RUN_REVIEW_ONLY", "target_mode": "PRE_ARMED_DRY_RUN", "requested_by": "guard_operator", "requested_at": "2026-06-17T00:00:20Z", "recorded_at": "2026-06-17T00:00:30Z", "operator_identity": "guard_human_operator", "reason_codes": ["operator_final_human_review", "pre_armed_dry_run_review_only"], "acknowledgements": list(REQUIRED_ACKS), "approval_record_persisted": True, "approval_recorded": True, "pre_armed_dry_run_authorized": False, "live_authorized": False, "autotrade_resume_authorized": False, "mode_change_requested": False, "mode_change_authorized": False, "command_ledger_appended": False}
    invalid = {"record_kind": "wrong", "record_id": "bad", "evidence_id": "bad", "approval_scope": "LIVE", "target_mode": "LIVE_MIN_SIZE", "requested_by": "", "requested_at": "", "recorded_at": "", "operator_identity": "", "reason_codes": ["bad"], "acknowledgements": [], "approval_record_persisted": False, "pre_armed_dry_run_authorized": True, "live_authorized": True, "mode_change_requested": True, "command_ledger_appended": True}
    path.write_text(json.dumps(valid, ensure_ascii=False, sort_keys=True) + "\n" + json.dumps(invalid, ensure_ascii=False, sort_keys=True) + "\n{broken_json\n", encoding="utf-8")


def _run_status(path: Path) -> dict:
    proc = subprocess.run([sys.executable, str(STATUS), "--approval-record-ledger", str(path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=60)
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        payload = {"ok": False, "error": f"stdout was not JSON: {exc}", "stdout_tail": proc.stdout[-1600:]}
    payload["returncode"] = proc.returncode
    return payload


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

    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    missing_path = TMP_ROOT / "missing_approval_records.jsonl"
    populated_path = TMP_ROOT / "approval_records.jsonl"
    if missing_path.exists():
        missing_path.unlink()
    _write_jsonl(populated_path)
    missing = _run_status(missing_path)
    populated = _run_status(populated_path)
    latest = populated.get("latest_valid_approval_record") or {}
    checks = {
        "missing_ledger_returncode_zero": missing.get("returncode") == 0 and missing.get("ok") is True,
        "missing_ledger_fail_soft": missing.get("approval_record_ledger_exists") is False and missing.get("decision") == "approval_record_ledger_status_read_only_missing",
        "populated_ledger_returncode_zero": populated.get("returncode") == 0 and populated.get("ok") is True,
        "valid_record_observed": populated.get("valid_record_count") == 1 and populated.get("ledger_human_approval_records_observed") is True and latest.get("record_id") == "approval_record_guard_valid_001",
        "invalid_and_skipped_visible": populated.get("invalid_record_count") == 1 and populated.get("skipped_row_count") == 1 and populated.get("invalid_records") and populated.get("skipped_rows"),
        "status_reader_does_not_persist_or_record": populated.get("approval_record_persisted_by_this_tool") is False and populated.get("approval_record_persisted") is False and populated.get("human_approval_recorded") is False,
        "no_ledger_append_no_mode_request": populated.get("approval_ledger_appended") is False and populated.get("command_ledger_appended") is False and populated.get("mode_change_requested") is False and populated.get("mode_change_authorized") is False,
        "read_only_no_broker_non_authorizing": populated.get("read_only") is True and populated.get("would_send_to_broker") is False and populated.get("pre_armed_dry_run_authorized") is False and populated.get("live_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DY: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_dy_pre_armed_dry_run_approval_record_ledger_status_guard", "status": "closed" if not failures else "open", "contract": {"approval_record_ledger_status_reader_present": STATUS.exists(), "missing_ledger_fail_soft": checks.get("missing_ledger_fail_soft", False), "valid_record_observed_read_only": checks.get("valid_record_observed", False), "invalid_and_skipped_rows_visible": checks.get("invalid_and_skipped_visible", False), "status_reader_does_not_persist_or_record": checks.get("status_reader_does_not_persist_or_record", False), "no_ledger_append_no_mode_request": checks.get("no_ledger_append_no_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("read_only_no_broker_non_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"missing": {"ok": missing.get("ok"), "decision": missing.get("decision"), "approval_record_ledger_exists": missing.get("approval_record_ledger_exists"), "valid_record_count": missing.get("valid_record_count")}, "populated": {"ok": populated.get("ok"), "decision": populated.get("decision"), "valid_record_count": populated.get("valid_record_count"), "invalid_record_count": populated.get("invalid_record_count"), "skipped_row_count": populated.get("skipped_row_count"), "latest_valid_approval_record": latest, "approval_record_persisted_by_this_tool": populated.get("approval_record_persisted_by_this_tool"), "approval_ledger_appended": populated.get("approval_ledger_appended"), "command_ledger_appended": populated.get("command_ledger_appended"), "mode_change_requested": populated.get("mode_change_requested")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
