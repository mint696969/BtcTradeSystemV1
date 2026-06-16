# path: ./tools/test_phase4a_autotrade_milestone_dp_formal_spec_next_thread_bootstrap_guard.py
# desc: Guard AutoTrade formal spec and next-thread bootstrap first-read alignment.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_SYSTEM_FORMAL_SPEC_2026-06-13.md"
DOCS_INDEX = REPO_ROOT / "tmp/docs/_INDEX.md"
START_HERE = REPO_ROOT / "tmp/gpt_room/02_START_HERE.md"
STATUS = REPO_ROOT / "tmp/gpt_room/08_STATUS.md"
FOCUS = REPO_ROOT / "tmp/gpt_room/09_FOCUS.json"
STATE = REPO_ROOT / "tmp/gpt_room/11_STATE.json"
HANDOFF = REPO_ROOT / "tmp/gpt_room/memory/handoffs/2026-06-13_autotrade_phase3_closed_pre_live_locked_thread_handoff.md"
DN_DECISION = REPO_ROOT / "tmp/gpt_room/memory/decisions/2026-06-13_autotrade_pre_live_operational_decision_lock.md"
DN_BOUNDARY = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_PRE_LIVE_OPERATIONAL_BOUNDARY_2026-06-13.md"
CLOSURE_DOC = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_PHASE3_CLOSURE_AND_NEXT_STEPS_2026-06-13.md"
DM_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_dm_phase3_shadow_mode_closure_guard.py"
DN_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_dn_pre_live_operational_decision_lock_guard.py"
DO_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_do_room_docs_handoff_refresh_guard.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)

REQUIRED_SPEC_TOKENS = (
    "How to resume in a new thread",
    "現状を把握してください。",
    "spot-as-signal / FX-as-execution",
    "Real AutoTrade execution is bitFlyer FX only",
    "Spot real trading is forbidden",
    "FX market data acquisition/storage",
    "Phase 3 Shadow Mode: closed",
    "Pre-live operational decisions: locked",
    "execution_product_code = unconfirmed_in_repo",
    "No implicit fallback",
    "Mode model",
    "AutoTrade read model",
    "Temporal flow features",
    "5-minute forecast",
    "Forecast outcome and calibration",
    "Strategy and candidate generation",
    "Risk gate",
    "Shadow and observer cycles",
    "Runtime health and live readiness",
    "Command and mode control",
    "Operator UI role",
    "Ledger model",
    "Performance and review",
    "Parameter governance",
    "Initial safety defaults",
    "Emergency and kill switch policy",
    "Long/short policy",
    "Paper/Replay next phase",
    "Execution Safety Harness future phase",
    "Armed Dry Run future phase",
    "Live Minimum Size future phase",
    "Completed milestone summary",
    "Non-negotiable prohibitions",
)

FIRST_READ_FILES = (
    "gpt_room/08_STATUS.md",
    "gpt_room/09_FOCUS.json",
    "gpt_room/11_STATE.json",
    "gpt_room/memory/handoffs/2026-06-13_autotrade_phase3_closed_pre_live_locked_thread_handoff.md",
    "docs/architecture/AUTOTRADE_SYSTEM_FORMAL_SPEC_2026-06-13.md",
    "gpt_room/memory/decisions/2026-06-13_autotrade_pre_live_operational_decision_lock.md",
    "docs/architecture/AUTOTRADE_PRE_LIVE_OPERATIONAL_BOUNDARY_2026-06-13.md",
    "docs/architecture/AUTOTRADE_PHASE3_CLOSURE_AND_NEXT_STEPS_2026-06-13.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    failures: list[str] = []
    spec_text = read(SPEC)
    index_text = read(DOCS_INDEX)
    start_text = read(START_HERE)
    status_text = read(STATUS)
    handoff_text = read(HANDOFF)
    focus_data = json.loads(read(FOCUS)) if FOCUS.exists() else {}
    state_data = json.loads(read(STATE)) if STATE.exists() else {}

    first_reads = tuple(focus_data.get("must_read_first") or ())
    checks = {
        "formal_spec_exists_and_is_comprehensive": SPEC.exists() and all(token in spec_text for token in REQUIRED_SPEC_TOKENS),
        "formal_spec_declares_next_thread_resume_phrase": "現状を把握してください。" in spec_text and "project_bootstrap" in spec_text,
        "start_here_current_override_points_to_autotrade_not_dashboard": START_HERE.exists() and "2026-06-13 CURRENT OVERRIDE: AutoTrade Phase 3 closed" in start_text and "Do not use old Operator UI dashboard current override as the active task" in start_text and "docs/architecture/AUTOTRADE_SYSTEM_FORMAL_SPEC_2026-06-13.md" in start_text,
        "docs_index_points_to_formal_spec_first": DOCS_INDEX.exists() and "Current active work is AutoTrade" in index_text and "docs/architecture/AUTOTRADE_SYSTEM_FORMAL_SPEC_2026-06-13.md" in index_text and "Historical Operator UI/dashboard anchors" in index_text,
        "focus_first_reads_include_formal_spec_and_handoff": all(path in first_reads for path in FIRST_READ_FILES),
        "state_and_status_keep_phase3_closed_fx_only_truth": state_data.get("closed_phase3", {}).get("status") == "closed" and state_data.get("pre_live_decision_lock", {}).get("core_rule") == "spot-as-signal / FX-as-execution" and ("AutoTrade Phase 3 is closed" in status_text or "Phase 3 Shadow Mode is closed" in status_text),
        "handoff_points_to_formal_spec_or_same_truth": "spot-as-signal / FX-as-execution" in handoff_text and "FX market identity / product config model" in handoff_text,
        "dn_do_anchors_exist": DN_DECISION.exists() and DN_BOUNDARY.exists() and CLOSURE_DOC.exists() and DM_GUARD.exists() and DN_GUARD.exists() and DO_GUARD.exists(),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DP: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dp_formal_spec_next_thread_bootstrap_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "formal_spec_exists_and_is_comprehensive": checks["formal_spec_exists_and_is_comprehensive"],
            "formal_spec_declares_next_thread_resume_phrase": checks["formal_spec_declares_next_thread_resume_phrase"],
            "start_here_current_override_points_to_autotrade_not_dashboard": checks["start_here_current_override_points_to_autotrade_not_dashboard"],
            "docs_index_points_to_formal_spec_first": checks["docs_index_points_to_formal_spec_first"],
            "focus_first_reads_include_formal_spec_and_handoff": checks["focus_first_reads_include_formal_spec_and_handoff"],
            "state_and_status_keep_phase3_closed_fx_only_truth": checks["state_and_status_keep_phase3_closed_fx_only_truth"],
            "handoff_points_to_formal_spec_or_same_truth": checks["handoff_points_to_formal_spec_or_same_truth"],
            "dn_do_anchors_exist": checks["dn_do_anchors_exist"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "formal_spec": str(SPEC.relative_to(REPO_ROOT)),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
