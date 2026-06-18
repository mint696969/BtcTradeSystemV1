# path: ./tools/test_phase4a_autotrade_milestone_gf_authorization_grant_status_guard.py
# desc: Guard S117 authorization grant/status remains status-only, non-persisting, non-mode-applying, non-broker, and non-authorizing.

from __future__ import annotations



import ast

import json

import subprocess

import sys

from pathlib import Path



from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()



REPO_ROOT = Path(__file__).resolve().parents[1]

RUNNER = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_grant_status.py"

S116_SPEC_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ge_authorization_grant_design_spec_guard.py"

TMP_ROOT = REPO_ROOT / "tmp" / "_s117_authorization_grant_status_guard"

CHECK_FILES = (RUNNER, S116_SPEC_GUARD)

PROTECTED_PREFIXES = (

    "btcts_next/src/btcts/collector_vnext/",

    "btcts_next/src/btcts/ingestion/",

    "btcts_next/src/btcts/processing/l3_market_semantics/",

    "btcts_next/src/btcts/processing/l4_consumer_models/",

)

FORBIDDEN_TOKENS = (

    "place_order(",

    "send_order(",

    "broker_order(",

    "private_api",

    "pybitflyer",

    "ccxt",

    "requests.post",

    "httpx.post",

    "append_command_ledger_record(",

    "validate_and_append_command",

    "submit_mode_change_command_request",

    "mode_changed=True",

    "would_send_to_broker=True",

    "pre_armed_dry_run_authorized=True",

    "live_authorized=True",

    "authorization_grant_granted=True",

    "authorization_grant_executed=True",

    "authorization_grant_recorded=True",

    "approval_ledger_appended=True",

    "command_ledger_appended=True",

    "mode_change_requested=True",

    "mode_change_authorized=True",

    "record_persistence_executed=True",

    "authorization_record_appended=True",

    "mode_apply_executed=True",

    "while True",

)

ACKS = (

    "confirm_s114_authorization_request_status_reviewed",

    "confirm_ready_status_is_not_itself_approval",

    "confirm_grant_is_explicit_human_decision",

    "confirm_grant_does_not_send_orders",

    "confirm_grant_does_not_apply_mode",

    "confirm_grant_does_not_append_command_ledger",

    "confirm_record_persistence_or_mode_apply_requires_separate_slice",

    "confirm_broker_execution_requires_later_explicit_armed_or_live_boundary",

)





def _write_json(path: Path, payload: dict) -> Path:

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    return path





def _source(*, ready: bool) -> dict:

    payload = {

        "ok": True,

        "report_version": "pre_armed_dry_run_authorization_request_status.s114.v1",

        "decision": "authorization_request_status_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_status_blocked_not_authorized_not_recorded_not_executed",

        "authorization_request_status_ready": ready,

        "record_execution_authorization_request_blockers": [] if ready else ["source_guard_forced_not_ready"],

        "source_commit_head": "d5804361",

        "read_only": True,

        "status_only": True,

        "would_send_to_broker": False,

        "mode_changed": False,

        "pre_armed_dry_run_authorized": False,

        "live_authorized": False,

        "autotrade_resume_authorized": False,

        "authorization_grant_granted": False,

        "authorization_grant_executed": False,

        "authorization_grant_recorded": False,

        "authorization_request_recorded": False,

        "authorization_request_record_executed": False,

        "approval_ledger_appended": False,

        "command_ledger_appended": False,

        "mode_change_requested": False,

        "mode_change_authorized": False,

    }

    return payload





def _review(*, valid: bool) -> dict:

    payload = {

        "grant_reviewed": bool(valid),

        "source_authorization_request_status_path": "tmp/_s117_authorization_grant_status_guard/source.json" if valid else "",

        "source_authorization_request_status_report_version": "pre_armed_dry_run_authorization_request_status.s114.v1" if valid else "wrong",

        "source_authorization_request_status_decision": "authorization_request_status_ready_not_authorized_not_recorded_not_executed" if valid else "wrong",

        "source_authorization_request_status_ready": bool(valid),

        "source_commit_head": "d5804361" if valid else "wrong",

        "requested_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_REVIEW_ONLY" if valid else "LIVE",

        "operator_identity": "guard_human_operator" if valid else "",

        "granted_by": "guard_human_operator" if valid else "",

        "requested_at": "2026-06-18T00:00:00Z" if valid else "",

        "granted_at": "2026-06-18T00:01:00Z" if valid else "",

        "grant_expires_at": "2026-06-18T01:01:00Z" if valid else "",

        "acknowledgements": list(ACKS) if valid else ["confirm_s114_authorization_request_status_reviewed"],

        "safety_boundary_snapshot": {

            "broker_free": bool(valid),

            "no_broker_execution": bool(valid),

            "no_real_orders": bool(valid),

            "no_mode_apply": bool(valid),

            "no_ui_command_buttons": bool(valid),

            "no_watchdog_loop": bool(valid),

            "separate_record_persistence_slice_required": bool(valid),

            "separate_mode_apply_slice_required": bool(valid),

            "armed_dry_run_authorized": False,

            "live_authorized": False,

            "broker_execution_permitted": False,

            "mode_apply_permitted": False,

            "grant_append_execution_permitted": False,

        },

        "grant_append_requested": False,

        "authorization_grant_execution_requested": False,

        "record_persistence_requested": False,

        "authorization_record_append_requested": False,

        "approval_ledger_append_requested": False,

        "command_ledger_append_requested": False,

        "mode_change_requested": False,

        "mode_apply_requested": False,

        "broker_execution_requested": False,

        "restricted_api_requested": False,

        "real_order_requested": False,

        "ui_command_button_requested": False,

        "watchdog_autonomous_execution_requested": False,

    }

    return payload





def _run_case(name: str, *, source_ready: bool, review_valid: bool) -> dict:

    case = TMP_ROOT / name

    source_path = _write_json(case / "source.json", _source(ready=source_ready))

    review_path = _write_json(case / "review.json", _review(valid=review_valid))

    out_path = case / "grant_status.json"

    proc = subprocess.run(

        [sys.executable, str(RUNNER), "--source-authorization-request-status", str(source_path), "--grant-review", str(review_path), "--out", str(out_path)],

        cwd=str(REPO_ROOT),

        text=True,

        capture_output=True,

        timeout=60,

    )

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

            out.update(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom) and node.module:

            out.add(node.module)

    return out





def main() -> int:

    failures: list[str] = []

    for path in CHECK_FILES:

        if not path.exists():

            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")

            continue

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



    ready = _run_case("ready_valid_review", source_ready=True, review_valid=True)

    missing_review = _run_case("ready_missing_review", source_ready=True, review_valid=False)

    blocked_source = _run_case("blocked_source_valid_review", source_ready=False, review_valid=True)



    checks = {

        "ready_case_returncode_zero": ready.get("returncode") == 0 and ready.get("ok") is True,

        "ready_case_ready_not_granted": ready.get("authorization_grant_ready") is True and ready.get("decision") == "authorization_grant_status_ready_not_granted_not_recorded_not_executed" and ready.get("authorization_grant_granted") is False,

        "ready_case_no_persistence_mode_broker": ready.get("authorization_grant_executed") is False and ready.get("authorization_grant_recorded") is False and ready.get("record_persistence_executed") is False and ready.get("authorization_record_appended") is False and ready.get("mode_change_requested") is False and ready.get("mode_changed") is False and ready.get("would_send_to_broker") is False and ready.get("pre_armed_dry_run_authorized") is False and ready.get("live_authorized") is False,

        "missing_review_blocks_visible": missing_review.get("returncode") == 0 and missing_review.get("authorization_grant_ready") is False and "grant_review_not_confirmed" in (missing_review.get("authorization_grant_blockers") or []),

        "blocked_source_blocks_visible": blocked_source.get("returncode") == 0 and blocked_source.get("authorization_grant_ready") is False and "source_authorization_request_status_not_ready" in (blocked_source.get("authorization_grant_blockers") or []),

        "ready_is_not_approval_check_visible": ((ready.get("checks") or {}).get("ready_is_not_approval") is True),

    }

    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)



    protected_dirty_hits: list[str] = []

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)

    for line in proc.stdout.splitlines():

        rel = line[3:] if len(line) > 3 else line

        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):

            protected_dirty_hits.append(line)

    failures.extend(f"protected lower-layer dirty during milestone GF: {hit}" for hit in protected_dirty_hits)



    payload = {

        "ok": not failures,

        "phase": "phase4a_autotrade_milestone_gf_authorization_grant_status_guard",

        "status": "closed" if not failures else "open",

        "contract": {

            "authorization_grant_status_runner_present": RUNNER.exists(),

            "ready_case_ready_not_granted": checks.get("ready_case_ready_not_granted", False),

            "missing_review_blocks_status": checks.get("missing_review_blocks_visible", False),

            "blocked_source_blocks_status": checks.get("blocked_source_blocks_visible", False),

            "no_persistence_mode_broker_or_authorization": checks.get("ready_case_no_persistence_mode_broker", False),

            "ready_is_not_approval_check_visible": checks.get("ready_is_not_approval_check_visible", False),

            "protected_lower_layers_untouched": not protected_dirty_hits,

        },

        "checks": checks,

        "cases": {

            "ready": {"ok": ready.get("ok"), "decision": ready.get("decision"), "authorization_grant_ready": ready.get("authorization_grant_ready"), "authorization_grant_granted": ready.get("authorization_grant_granted"), "authorization_grant_recorded": ready.get("authorization_grant_recorded"), "mode_change_requested": ready.get("mode_change_requested")},

            "missing_review": {"ok": missing_review.get("ok"), "decision": missing_review.get("decision"), "authorization_grant_ready": missing_review.get("authorization_grant_ready"), "authorization_grant_blockers": missing_review.get("authorization_grant_blockers")},

            "blocked_source": {"ok": blocked_source.get("ok"), "decision": blocked_source.get("decision"), "authorization_grant_ready": blocked_source.get("authorization_grant_ready"), "authorization_grant_blockers": blocked_source.get("authorization_grant_blockers")},

        },

        "protected_dirty_hits": protected_dirty_hits,

        "failures": failures,

    }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))

    return 0 if not failures else 1





if __name__ == "__main__":

    raise SystemExit(main())
