# path: ./tools/test_phase4a_autotrade_milestone_hc_shadow_prediction_context_design_guard.py
# desc: Guard S140 Shadow prediction context design packet remains documentation/status-only and does not authorize Shadow append, mode apply, grants, broker behavior, or live_shadow behavior changes.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/architecture/AUTOTRADE_SHADOW_DECISION_OPTIONAL_PREDICTION_CONTEXT_DESIGN_2026-06-18.md"
LIVE_SHADOW = REPO_ROOT / "btcts_next/src/btcts/autotrade/live_shadow.py"
S138_STATUS = REPO_ROOT / "btcts_next/src/btcts/autotrade/prediction_preview_status.py"
S139_DISPLAY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py"
REQUIRED_TERMS = (
    "design-only / documentation / non-executing",
    "Shadow Decision Optional Prediction Context Design / Non-Executing Seam",
    "AutoTradeShadowPredictionContext",
    "AutoTradePredictionPreviewStatus",
    "AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT",
    "S141 Shadow decision optional context contract, still persist=False only",
    "optional_context_only = True",
    "would_change_shadow_candidate = False",
    "would_append_shadow_decision = False",
    "would_apply_mode = False",
    "would_execute_prearmed_grant = False",
    "would_write_runtime_artifact = False",
    "would_send_to_broker = False",
    "broker_execution_requested = False",
    "mode_apply_requested = False",
    "command_ledger_append_requested = False",
    "approval_append_requested = False",
    "persist is False when a Shadow preview runner is used in tests",
    "no append_decision_jsonl token in any new prediction-context module",
    "no broker/private API/external API imports",
    "no collector imports",
)
REQUIRED_NON_PERMISSIONS = (
    "live_shadow.py behavior modification",
    "run_shadow_decision_from_snapshot modification",
    "run_latest_market_state_shadow_decision modification",
    "build_action_candidate modification",
    "append_decision_jsonl usage",
    "Shadow decision append",
    "persist=True usage from prediction context flow",
    "feeding preview output directly into build_action_candidate",
    "using prediction context to alter candidate action",
    "mode apply",
    "Pre-Armed grant execution",
    "broker execution",
    "real orders",
    "private API calls",
    "external API calls",
    "collector imports",
    "command ledger append",
    "approval ledger append",
)
FORBIDDEN_DOC_TOKENS = (
    "S140 permits broker execution",
    "S140 authorizes broker execution",
    "S140 permits append_decision_jsonl",
    "S140 modifies live_shadow.py",
    "mode apply is allowed",
    "real orders are allowed",
    "persist=True is allowed from prediction context flow",
)
ALLOWED_DIRTY_MARKERS = (
    "docs/architecture/AUTOTRADE_SHADOW_DECISION_OPTIONAL_PREDICTION_CONTEXT_DESIGN_2026-06-18.md",
    "tools/test_phase4a_autotrade_milestone_hc_shadow_prediction_context_design_guard.py",
    "tools/test_phase4a_autotrade_milestone_hc_shadow_prediction_context_design_close_guard.py",
)
PROTECTED_DIR_PREFIXES = (
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/apps/operator_ui/",
    "btcts_next/src/btcts/prediction/",
    "btcts_next/src/btcts/collector_vnext/",
)


def _syntax(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True
    except Exception:
        return False


def main() -> int:
    failures: list[str] = []
    text = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    live_shadow_text = LIVE_SHADOW.read_text(encoding="utf-8") if LIVE_SHADOW.exists() else ""
    s138_text = S138_STATUS.read_text(encoding="utf-8") if S138_STATUS.exists() else ""
    s139_text = S139_DISPLAY.read_text(encoding="utf-8") if S139_DISPLAY.exists() else ""

    checks = {
        "doc_exists": DOC.exists(),
        "doc_is_design_only": "Status: design-only / documentation / non-executing" in text and "does not change runtime behavior" in text,
        "required_terms_present": all(term in text for term in REQUIRED_TERMS),
        "required_non_permissions_present": all(term in text for term in REQUIRED_NON_PERMISSIONS),
        "forbidden_doc_tokens_absent": not any(token in text for token in FORBIDDEN_DOC_TOKENS),
        "next_slice_is_s141_persist_false_only": "S141 Shadow decision optional context contract, still persist=False only" in text and "S142" in text and "S143" in text,
        "live_shadow_existing_append_path_unchanged_by_design": "append_decision_jsonl" in live_shadow_text and "run_shadow_decision_from_snapshot" in live_shadow_text and "build_action_candidate" in live_shadow_text,
        "s138_status_contract_present": "AutoTradePredictionPreviewStatus" in s138_text and "build_autotrade_prediction_preview_status" in s138_text,
        "s139_display_contract_present": "AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT" in s139_text and "build_autotrade_prediction_preview_status_display_packet" in s139_text,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    dirty_lines = [line for line in proc.stdout.splitlines() if line.strip()]
    unexpected_dirty = [line for line in dirty_lines if not any(marker in line for marker in ALLOWED_DIRTY_MARKERS)]
    protected_dirty_hits = []
    for line in dirty_lines:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_DIR_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"unexpected dirty file during HC docs-only slice: {line}" for line in unexpected_dirty)
    failures.extend(f"protected code dirty during HC docs-only slice: {line}" for line in protected_dirty_hits)

    checks["only_doc_and_guard_dirty"] = not unexpected_dirty
    checks["protected_code_dirs_untouched"] = not protected_dirty_hits
    checks["guard_syntax_ok"] = _syntax(Path(__file__))

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_hc_shadow_prediction_context_design_guard",
        "status": "closed" if not failures else "open",
        "contract": checks,
        "sample": {
            "doc": str(DOC.relative_to(REPO_ROOT)),
            "chosen_seam": "Shadow Decision Optional Prediction Context Design / Non-Executing Seam",
            "next_slice": "S141 Shadow decision optional context contract, still persist=False only",
            "dirty_lines": dirty_lines,
        },
        "unexpected_dirty": unexpected_dirty,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_shadow_prediction_context_design_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
