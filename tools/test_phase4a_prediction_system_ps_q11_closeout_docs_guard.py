# path: ./tools/test_phase4a_prediction_system_ps_q11_closeout_docs_guard.py
# desc: Guard for PS-Q11 Scenario Core closeout documentation refresh.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PS_Q11_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_CLOSEOUT_2026-06-22.md"
Q10_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_Q10R_Q10W_THREAD_CLOSEOUT_2026-06-21.md"
REENTRY_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_CLOSEOUT_2026-06-22.md",
    "docs/strategy/PREDICTION_SYSTEM_Q10R_Q10W_THREAD_CLOSEOUT_2026-06-21.md",
    "docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md",
    "tools/test_phase4a_prediction_system_ps_q11_closeout_docs_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _require_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"missing {label} marker: {marker}")


def main() -> int:
    failures: list[str] = []

    for path in (PS_Q11_DOC, Q10_DOC, REENTRY_DOC):
        if not path.exists():
            failures.append(f"missing doc: {path.relative_to(REPO_ROOT)}")

    if PS_Q11_DOC.exists():
        ps_text = _read(PS_Q11_DOC)
        _require_markers(
            ps_text,
            (
                "Head at closeout candidate: f5ba61a4",
                "PS-Q11A through PS-Q11H completed through f5ba61a4",
                "480517e1 PS-Q11A Scenario Core evidence weighting trace",
                "f5ba61a4 PS-Q11H Scenario Core summary contract consolidation / closeout candidate",
                "evidence_weighting_trace",
                "invalidation_rewrite_trace",
                "scenario_switch_trace",
                "trace_contract_summary",
                "advisory_output_packet_candidate",
                "operator_review_handoff_shape",
                "advisory_packet_summary",
                "scenario_core_closeout_candidate",
                "closeout_status: ready_for_thread_closeout",
                "summary_contract_status: complete",
                "consolidated_trace_count: 7",
                "manual_review_only: true",
                "advisory_read_only: true",
                "non_executing: true",
                "would_send_to_broker: false",
                "would_append_ledger: false",
                "would_write_runtime_artifact: false",
                "no_auto_trade",
                "no_broker_send",
                "no_mode_apply",
                "no_order_place",
                "no_ledger_append",
                "no_runtime_write",
                "Do not start AutoTrade",
            ),
            "ps_q11_closeout_doc",
            failures,
        )

    if Q10_DOC.exists():
        q10_text = _read(Q10_DOC)
        _require_markers(
            q10_text,
            (
                "2026-06-22 PS-Q11 Scenario Core closeout update",
                "Head: f5ba61a4",
                "PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_CLOSEOUT_2026-06-22.md",
                "Completed: PS-Q11A-PS-Q11H Scenario Prediction Core strengthening.",
                "State: ready_for_thread_closeout_read_only_non_executing.",
                "AutoTrade execution",
                "runtime artifact write",
            ),
            "q10_appendix",
            failures,
        )

    if REENTRY_DOC.exists():
        reentry_text = _read(REENTRY_DOC)
        _require_markers(
            reentry_text,
            (
                "2026-06-22 PS-Q11 Scenario Core closeout",
                "Head: f5ba61a4",
                "PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_CLOSEOUT_2026-06-22.md",
                "State: ready_for_thread_closeout_read_only_non_executing.",
                "Do not treat this closeout as approval to resume AutoTrade.",
                "must not add broker/mode/order, approval/ledger, WarRoom actual-read, payload decode, or runtime artifact write paths",
            ),
            "reentry_appendix",
            failures,
        )

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q11_closeout_docs",
        "phase": "phase3_prediction_system_reentry_scenario_prediction_core_strengthening",
        "contract": {
            "docs_only": not failures,
            "ps_q11_closeout_present": PS_Q11_DOC.exists() and not failures,
            "q10_doc_updated": Q10_DOC.exists() and not failures,
            "reentry_gate_updated": REENTRY_DOC.exists() and not failures,
            "no_execution_enablement_text_removed": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q11_closeout_docs_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
