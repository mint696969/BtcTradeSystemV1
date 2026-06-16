# path: ./tools/test_phase4a_autotrade_milestone_ap_mode_change_command_applier_once_guard.py
# desc: Guard one-shot mode-change command applier updates mode_state only and is idempotent.

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandLedgerRecord,
    CommandRequest,
    CommandType,
    apply_latest_mode_change_command_once,
    current_mode_state,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    read_mode_state_records,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_once.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
)
FORBIDDEN_TEXT_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_apply_mode_change_once.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "btcts.apps.operator_ui",
    "streamlit",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "submit_mode_change_command_request",
    "validate_and_append_command",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


def imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def command_row(command_id: str, *, command_type: str, accepted: bool, current_mode: str, target: str | None, blocked_by: list[str]) -> dict:
    return {
        "ledger_event": "autotrade.mode_change_command_request_validated" if command_type == "REQUEST_MODE_CHANGE" else "autotrade.command_request_validated",
        "command_id": command_id,
        "accepted": accepted,
        "blocked_by": blocked_by,
        "command": {
            "command_id": command_id,
            "command_type": command_type,
            "requested_by": "guard",
            "requested_at": "2026-06-13T04:40:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "mode_applier"],
            "note": "{}",
            "confirmation_required": True,
        },
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_applier_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(
            command_path,
            [
                command_row("cmd_ap_rejected", command_type="REQUEST_MODE_CHANGE", accepted=False, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=["readiness_preflight_not_ready"]),
                command_row("cmd_ap_halt", command_type="REQUEST_HALT_NEW", accepted=True, current_mode="OFF", target="halt_new", blocked_by=[]),
                command_row("cmd_ap_shadow", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="SHADOW", blocked_by=[]),
            ],
        )
        first = apply_latest_mode_change_command_once(max_lines=100)
        after_first_rows = read_mode_state_records(mode_path, max_lines=100)
        after_first_current = current_mode_state(mode_path, max_lines=100)
        second = apply_latest_mode_change_command_once(max_lines=100)
        after_second_rows = read_mode_state_records(mode_path, max_lines=100)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        cli_proc = subprocess.run(
            [sys.executable, "-m", "btcts.apps.autotrade_apply_mode_change_once", "--max-lines", "100"],
            cwd=REPO_ROOT,
            env={**env, ENV_AUTOTRADE_RUNTIME_ROOT: str(hot_root)},
            text=True,
            capture_output=True,
        )
        cli_payload = json.loads(cli_proc.stdout) if cli_proc.stdout.strip() else {}
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in CHECK_FILES)
    forbidden_text = "\n".join(path.read_text(encoding="utf-8") for path in FORBIDDEN_TEXT_FILES)
    all_imports = set().union(*(imports_from(path) for path in CHECK_FILES))
    checks = {
        "applier_contract_present": "ModeChangeCommandApplyResult" in all_text and "apply_latest_mode_change_command_once" in all_text,
        "first_apply_changes_mode_state": first.applied is True and first.command_id == "cmd_ap_shadow" and first.current_mode_before == "OFF" and first.current_mode_after == "SHADOW" and first.mode_changed is True,
        "mode_state_appended_once": len(after_first_rows.rows) == 1 and after_first_current.current_mode.value == "SHADOW",
        "idempotent_second_apply": second.applied is False and second.skipped is True and second.skip_reason == "no_unapplied_accepted_mode_change_command" and len(after_second_rows.rows) == 1,
        "rejected_and_non_mode_ignored": "cmd_ap_rejected" not in second.already_applied_command_ids and "cmd_ap_halt" not in second.already_applied_command_ids,
        "cli_skip_exit_semantics": cli_proc.returncode == 2 and cli_payload.get("skipped") is True,
        "json_safe_result": json.loads(json.dumps(first.to_dict(), ensure_ascii=False, default=str))["applied"] is True,
        "no_ui_imports": not any(item.startswith("btcts.apps.operator_ui") for item in all_imports) and "streamlit" not in all_imports,
        "no_forbidden_tokens": not any(token in forbidden_text for token in FORBIDDEN_TOKENS),
        "no_broker": first.would_send_to_broker is False and second.would_send_to_broker is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    if cli_proc.returncode not in (0, 2):
        failures.append(f"cli stderr: {cli_proc.stderr}")

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AP: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ap_mode_change_command_applier_once_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_change_command_applier_present": checks["applier_contract_present"],
            "accepted_request_applies_once": checks["first_apply_changes_mode_state"] and checks["mode_state_appended_once"],
            "idempotency_present": checks["idempotent_second_apply"],
            "rejected_and_non_mode_ignored": checks["rejected_and_non_mode_ignored"],
            "cli_exit_semantics_present": checks["cli_skip_exit_semantics"],
            "no_ui_no_broker": checks["no_ui_imports"] and checks["no_forbidden_tokens"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "first": first.to_dict(),
        "second": second.to_dict(),
        "cli": {"returncode": cli_proc.returncode, "payload": cli_payload},
        "mode_state_rows": after_second_rows.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
