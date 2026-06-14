# path: ./tools/test_phase4a_autotrade_milestone_ar_readiness_current_mode_from_mode_state_guard.py
# desc: Guard Live Readiness Preflight current-mode preview defaults from mode_state ledger and remains read-only.

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

from btcts.autotrade.execution import append_mode_state_record, current_mode_state, default_mode_state_ledger_path  # noqa: E402
from btcts.autotrade.execution.mode_state import ModeStateRecord  # noqa: E402
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.runtime_paths import ENV_AUTOTRADE_RUNTIME_ROOT  # noqa: E402

UI_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
PREFLIGHT_FORBIDDEN_TOKENS = (
    "apply_latest_mode_change_command_once",
    "append_mode_state_record",
    "validate_and_append_command",
    "append_command_ledger_record",
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


def main() -> int:
    failures: list[str] = []
    original_runtime = os.environ.get(ENV_AUTOTRADE_RUNTIME_ROOT)
    hot_root = REPO_ROOT / "tmp/btc_ts_readiness_mode_state_hot"
    try:
        os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = str(hot_root)
        mode_path = default_mode_state_ledger_path(ensure=True)
        if mode_path.exists():
            mode_path.unlink()
        append_mode_state_record(
            mode_path,
            ModeStateRecord(
                current_mode=AutoTradeMode.PAPER_OR_REPLAY,
                previous_mode=AutoTradeMode.SHADOW,
                changed_at="2026-06-13T05:00:00Z",
                source_command_id="cmd_readiness_mode_state_paper",
                requested_by="guard",
                accepted=True,
                mode_changed=True,
                reason_codes=("guard",),
                blocked_by=(),
                would_send_to_broker=False,
            ),
        )
        current = current_mode_state(max_lines=100)
    finally:
        if original_runtime is None:
            os.environ.pop(ENV_AUTOTRADE_RUNTIME_ROOT, None)
        else:
            os.environ[ENV_AUTOTRADE_RUNTIME_ROOT] = original_runtime

    source = function_source(UI_FILE, "_render_live_readiness_preflight")
    text = UI_FILE.read_text(encoding="utf-8")
    checks = {
        "preflight_reads_mode_state": "mode_state_current_mode" in source and "current_mode_state(max_lines=500).current_mode" in source,
        "preflight_default_index_from_mode_state": "mode_values.index(mode_state_current_mode.value)" in source,
        "preflight_json_shows_mode_state_current_mode": "mode_state_current_mode" in source and "mode_state_source" in source,
        "preflight_no_armed_dry_run_fixed_default": "index=mode_values.index(AutoTradeMode.ARMED_DRY_RUN.value)" not in source,
        "preflight_read_only_no_apply_no_broker": not any(token in source for token in PREFLIGHT_FORBIDDEN_TOKENS),
        "mode_state_contract_still_works": current.current_mode == AutoTradeMode.PAPER_OR_REPLAY,
        "mode_state_panel_still_present": "_render_mode_state_status()" in text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone AR: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ar_readiness_current_mode_from_mode_state_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "readiness_preflight_current_mode_from_mode_state": checks["preflight_reads_mode_state"] and checks["preflight_default_index_from_mode_state"],
            "mode_state_source_visible_in_preflight_json": checks["preflight_json_shows_mode_state_current_mode"],
            "fixed_armed_dry_run_default_removed": checks["preflight_no_armed_dry_run_fixed_default"],
            "preflight_read_only_no_apply_no_broker": checks["preflight_read_only_no_apply_no_broker"],
            "mode_state_contract_still_works": checks["mode_state_contract_still_works"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "current": current.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
