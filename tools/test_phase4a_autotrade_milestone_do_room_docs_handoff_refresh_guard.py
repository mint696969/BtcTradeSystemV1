# path: ./tools/test_phase4a_autotrade_milestone_do_room_docs_handoff_refresh_guard.py
# desc: Guard gpt_room/docs/handoff refresh after AutoTrade Phase 3 closure and pre-live decision lock.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS = REPO_ROOT / "tmp/gpt_room/08_STATUS.md"
FOCUS = REPO_ROOT / "tmp/gpt_room/09_FOCUS.json"
STATE = REPO_ROOT / "tmp/gpt_room/11_STATE.json"
DECISIONS = REPO_ROOT / "tmp/gpt_room/10_DECISIONS.md"
HANDOFF = REPO_ROOT / "tmp/gpt_room/memory/handoffs/2026-06-13_autotrade_phase3_closed_pre_live_locked_thread_handoff.md"
DN_DECISION = REPO_ROOT / "tmp/gpt_room/memory/decisions/2026-06-13_autotrade_pre_live_operational_decision_lock.md"
DN_BOUNDARY = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_PRE_LIVE_OPERATIONAL_BOUNDARY_2026-06-13.md"
CLOSURE_DOC = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_PHASE3_CLOSURE_AND_NEXT_STEPS_2026-06-13.md"
DM_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_dm_phase3_shadow_mode_closure_guard.py"
DN_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_dn_pre_live_operational_decision_lock_guard.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    failures: list[str] = []
    status_text = read(STATUS)
    decisions_text = read(DECISIONS)
    handoff_text = read(HANDOFF)
    dn_decision_text = read(DN_DECISION)
    dn_boundary_text = read(DN_BOUNDARY)
    closure_doc_text = read(CLOSURE_DOC)
    focus_data = json.loads(read(FOCUS)) if FOCUS.exists() else {}
    state_data = json.loads(read(STATE)) if STATE.exists() else {}

    checks = {
        "canonical_status_points_to_autotrade_phase3_closed": all(token in status_text for token in ("autotrade_phase3_closed_pre_live_locked_handoff_prep", "Phase 3 Shadow Mode is closed", "spot-as-signal / FX-as-execution", "No FX product/account confirmation, no live mode")),
        "focus_json_points_to_next_thread_first_reads": focus_data.get("current_focus") == "autotrade_phase3_closed_pre_live_locked_handoff_prep" and focus_data.get("pre_live_decision_lock", {}).get("core_rule") == "spot-as-signal / FX-as-execution" and "gpt_room/memory/handoffs/2026-06-13_autotrade_phase3_closed_pre_live_locked_thread_handoff.md" in tuple(focus_data.get("must_read_first") or []),
        "state_json_carries_progress_and_remaining_before_live": state_data.get("state_kind") == "compact_current_state_after_autotrade_phase3_closed_pre_live_locked" and state_data.get("progress_estimate", {}).get("phase3_shadow_mode") == "closed" and "FX market identity/product/account path confirmation" in tuple(state_data.get("remaining_before_live_min_size") or state_data.get("remaining_before_live") or []),
        "decisions_current_override_is_autotrade_not_old_dashboard": "2026-06-13 CURRENT OVERRIDE: AutoTrade Phase 3 closed" in decisions_text and "spot-as-signal / FX-as-execution" in decisions_text and decisions_text.index("2026-06-13 CURRENT OVERRIDE") < decisions_text.index("2026-06-12 CURRENT OVERRIDE"),
        "handoff_exists_and_contains_next_phase_guardrails": all(token in handoff_text for token in ("Phase 3 Shadow Mode is closed", "spot-as-signal / FX-as-execution", "Real trading is bitFlyer FX only", "FX market identity / product config model", "Do not silently map spot BTC_JPY to FX execution")),
        "dn_decision_and_boundary_docs_still_exist": DN_DECISION.exists() and DN_BOUNDARY.exists() and "Real trading is bitFlyer FX only" in dn_decision_text and "execution_market_type = FX" in dn_boundary_text,
        "closure_doc_exists_and_points_to_phase4_next": CLOSURE_DOC.exists() and "Phase 4: Paper/Replay order lifecycle" in closure_doc_text and "FX market identity / product config skeleton" in closure_doc_text,
        "dm_dn_guards_exist": DM_GUARD.exists() and DN_GUARD.exists(),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DO: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_do_room_docs_handoff_refresh_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "canonical_status_points_to_autotrade_phase3_closed": checks["canonical_status_points_to_autotrade_phase3_closed"],
            "focus_json_points_to_next_thread_first_reads": checks["focus_json_points_to_next_thread_first_reads"],
            "state_json_carries_progress_and_remaining_before_live": checks["state_json_carries_progress_and_remaining_before_live"],
            "decisions_current_override_is_autotrade_not_old_dashboard": checks["decisions_current_override_is_autotrade_not_old_dashboard"],
            "handoff_exists_and_contains_next_phase_guardrails": checks["handoff_exists_and_contains_next_phase_guardrails"],
            "dn_decision_and_boundary_docs_still_exist": checks["dn_decision_and_boundary_docs_still_exist"],
            "closure_doc_exists_and_points_to_phase4_next": checks["closure_doc_exists_and_points_to_phase4_next"],
            "dm_dn_guards_exist": checks["dm_dn_guards_exist"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
