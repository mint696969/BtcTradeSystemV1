# path: ./tools/test_phase4a_autotrade_milestone_as_mode_change_applier_preview_status_guard.py
# desc: Guard read-only mode-change applier preview/status. No mode_state append, no broker execution.

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
    apply_latest_mode_change_command_once,
    default_command_ledger_path,
    default_mode_state_ledger_path,
    preview_latest_mode_change_command_apply,
    read_mode_state_records,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

CHECK_FILES = (
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_preview_mode_change_once.py",
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/__init__.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
PREVIEW_FORBIDDEN_TOKENS = (
    "append_mode_state_record",
    "append_command_ledger_record",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "btcts.apps.operator_ui",
    "streamlit",
    "run_observer_cycle_bounded",
    "run_observer_cycle_once",
    "run_shadow_cycle_once",
    "run_shadow_cycle_bounded",
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)


def function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(text, node) or ""
    return ""


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
            "requested_at": "2026-06-13T05:10:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "mode_preview"],
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
    hot_root = REPO_ROOT / "tmp/btc_ts_mode_preview_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(
            command_path,
            [
                command_row("cmd_as_rejected", command_type="REQUEST_MODE_CHANGE", accepted=False, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=["readiness_preflight_not_ready"]),
                command_row("cmd_as_halt", command_type="REQUEST_HALT_NEW", accepted=True, current_mode="OFF", target="halt_new", blocked_by=[]),
                command_row("cmd_as_shadow", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="SHADOW", blocked_by=[]),
            ],
        )
        before_rows = read_mode_state_records(mode_path, max_lines=100)
        preview = preview_latest_mode_change_command_apply(max_lines=100)
        after_preview_rows = read_mode_state_records(mode_path, max_lines=100)
        applied = apply_latest_mode_change_command_once(max_lines=100)
        after_apply_preview = preview_latest_mode_change_command_apply(max_lines=100)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        cli_proc = subprocess.run(
            [sys.executable, "-m", "btcts.apps.autotrade_preview_mode_change_once", "--max-lines", "100"],
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
    preview_source = function_source(REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/mode_command_applier.py", "preview_latest_mode_change_command_apply")
    cli_text = (REPO_ROOT / "btcts_next/src/btcts/apps/autotrade_preview_mode_change_once.py").read_text(encoding="utf-8")
    checks = {
        "preview_contract_present": "ModeChangeCommandApplyPreview" in all_text and "preview_latest_mode_change_command_apply" in all_text,
        "preview_would_apply_without_append": preview.would_apply is True and preview.command_id == "cmd_as_shadow" and preview.current_mode_before == "OFF" and preview.current_mode_after == "SHADOW" and len(before_rows.rows) == 0 and len(after_preview_rows.rows) == 0,
        "preview_counts_present": preview.candidate_command_count == 1 and preview.command_read_skipped_count == 0 and preview.mode_state_read_skipped_count == 0,
        "after_apply_preview_idempotent_skip": applied.applied is True and after_apply_preview.would_apply is False and after_apply_preview.skip_reason == "no_unapplied_accepted_mode_change_command",
        "cli_skip_exit_semantics": cli_proc.returncode == 2 and cli_payload.get("would_apply") is False and cli_payload.get("skip_reason") == "no_unapplied_accepted_mode_change_command",
        "json_safe_preview": json.loads(json.dumps(preview.to_dict(), ensure_ascii=False, default=str))["would_apply"] is True,
        "preview_function_read_only": bool(preview_source) and not any(token in preview_source for token in PREVIEW_FORBIDDEN_TOKENS),
        "preview_cli_read_only": not any(token in cli_text for token in PREVIEW_FORBIDDEN_TOKENS),
        "no_broker": preview.would_send_to_broker is False and after_apply_preview.would_send_to_broker is False,
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
    failures.extend(f"protected lower-layer dirty during milestone AS: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_as_mode_change_applier_preview_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_change_applier_preview_present": checks["preview_contract_present"],
            "preview_would_apply_without_append": checks["preview_would_apply_without_append"],
            "preview_counts_present": checks["preview_counts_present"],
            "idempotent_skip_visible_after_apply": checks["after_apply_preview_idempotent_skip"],
            "cli_exit_semantics_present": checks["cli_skip_exit_semantics"],
            "preview_read_only_no_broker": checks["preview_function_read_only"] and checks["preview_cli_read_only"] and checks["no_broker"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "preview": preview.to_dict(),
        "applied": applied.to_dict(),
        "after_apply_preview": after_apply_preview.to_dict(),
        "cli": {"returncode": cli_proc.returncode, "payload": cli_payload},
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
