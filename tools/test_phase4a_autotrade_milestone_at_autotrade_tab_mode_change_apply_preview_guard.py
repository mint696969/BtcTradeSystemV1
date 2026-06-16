# path: ./tools/test_phase4a_autotrade_milestone_at_autotrade_tab_mode_change_apply_preview_guard.py
# desc: Guard AutoTrade UI tab displays read-only mode-change apply preview. No apply, no append, no broker.

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
    default_command_ledger_path,
    default_mode_state_ledger_path,
    preview_latest_mode_change_command_apply,
    read_mode_state_records,
)
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
PREVIEW_STATUS_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "validate_and_append_command",
    "append_command_ledger_record",
    "submit_mode_change_command_request",
    "st.button(",
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
            "requested_at": "2026-06-13T05:20:00Z",
            "current_mode": current_mode,
            "target": target,
            "confirmation": True,
            "reason_codes": ["guard", "ui_preview"],
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
    hot_root = REPO_ROOT / "tmp/btc_ts_ui_apply_preview_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        command_path = default_command_ledger_path(ensure=True)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        write_jsonl(
            command_path,
            [
                command_row("cmd_at_rejected", command_type="REQUEST_MODE_CHANGE", accepted=False, current_mode="OFF", target="LIVE_MIN_SIZE", blocked_by=["readiness_preflight_not_ready"]),
                command_row("cmd_at_shadow", command_type="REQUEST_MODE_CHANGE", accepted=True, current_mode="OFF", target="SHADOW", blocked_by=[]),
            ],
        )
        before_rows = read_mode_state_records(mode_path, max_lines=100)
        preview = preview_latest_mode_change_command_apply(max_lines=100)
        after_rows = read_mode_state_records(mode_path, max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    text = UI_FILE.read_text(encoding="utf-8")
    imports = imports_from(UI_FILE)
    source = function_source(UI_FILE, "_render_mode_change_apply_preview_status")
    render_source = function_source(UI_FILE, "render")
    checks = {
        "ui_imports_apply_preview": "btcts.autotrade.execution" in imports and "preview_latest_mode_change_command_apply" in text,
        "ui_has_apply_preview_panel": "_render_mode_change_apply_preview_status" in text and "Mode Change Apply Preview" in text,
        "ui_displays_apply_preview_fields": all(token in text for token in ("would_apply", "skip_reason", "command_id", "current_mode_before", "current_mode_after", "candidate_command_count", "already_applied_command_ids", "command_read_skipped_count", "mode_state_read_skipped_count")),
        "preview_status_read_only": bool(source) and not any(token in source for token in PREVIEW_STATUS_FORBIDDEN_TOKENS),
        "preview_status_rendered_after_mode_state": "_render_mode_state_status()" in render_source and "_render_mode_change_apply_preview_status()" in render_source and render_source.index("_render_mode_state_status()") < render_source.index("_render_mode_change_apply_preview_status()") < render_source.index("_render_command_request_status()"),
        "preview_contract_still_read_only": preview.would_apply is True and preview.command_id == "cmd_at_shadow" and len(before_rows.rows) == 0 and len(after_rows.rows) == 0,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AT: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_at_autotrade_tab_mode_change_apply_preview_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "autotrade_tab_mode_change_apply_preview_present": checks["ui_imports_apply_preview"] and checks["ui_has_apply_preview_panel"],
            "apply_preview_fields_displayed": checks["ui_displays_apply_preview_fields"],
            "preview_status_read_only_no_apply_no_broker": checks["preview_status_read_only"],
            "preview_status_rendered_after_mode_state": checks["preview_status_rendered_after_mode_state"],
            "preview_contract_still_read_only": checks["preview_contract_still_read_only"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "preview": preview.to_dict(),
        "mode_state_rows_after_preview": after_rows.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
