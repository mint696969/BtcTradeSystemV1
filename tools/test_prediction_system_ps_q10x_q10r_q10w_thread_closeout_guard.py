# path: ./tools/test_prediction_system_ps_q10x_q10r_q10w_thread_closeout_guard.py
# desc: Guard for final Q10R-Q10W thread closeout spec and gpt_room next-thread handoff entry.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_Q10R_Q10W_THREAD_CLOSEOUT_2026-06-21.md"
INDEX = REPO_ROOT / "docs/_INDEX.md"
REENTRY = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_REENTRY_GATE_2026-06-19.md"
START = REPO_ROOT / "tmp/gpt_room/02_START_HERE.md"
STATUS = REPO_ROOT / "tmp/gpt_room/08_STATUS.md"
NEXT = REPO_ROOT / "tmp/gpt_room/NEXT_THREAD_PREDICTION_SYSTEM_PS_Q11_SCENARIO_CORE_START_HERE.md"
HANDOFF = REPO_ROOT / "tmp/gpt_room/memory/handoffs/2026-06-21_prediction_system_q10r_q10w_next_thread_handoff.md"

REQUIRED_DOC_TOKENS = (
    "Head at closeout: 47860a81",
    "WarRoom actual review-packet mounted observation lane is ready for operator review handoff.",
    "This is not an execution path.",
    "AutoTrade remains paused.",
    "Prediction-to-trigger-candidate bridge was not added.",
    "AutoTrade trigger is not enabled.",
    "Broker/private API call is not enabled.",
    "Start with PS-Q11-style Scenario Prediction Core strengthening.",
    "richer evidence weighting",
    "richer invalidation / rewrite state",
    "richer scenario switch trace",
    "trace_focus_material",
    "47860a81 fix: include readiness exit commit in branch summary",
)
REQUIRED_ROOM_TOKENS = (
    "PREDICTION SYSTEM Q10R-Q10W THREAD CLOSEOUT",
    "Head: 47860a81",
    "Next: PS-Q11 Scenario Prediction Core strengthening",
    "not execution",
    "Do not resume AutoTrade automatically",
)
FORBIDDEN_DOC_TOKENS = (
    "AutoTrade trigger is enabled",
    "broker/private API call is enabled",
    "production UI actual-read trigger was added",
    "approval/authorization grant is enabled",
    "decision or command ledger append is enabled",
)


def _read(path: Path) -> str:
    assert path.exists(), f"missing: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")



def test_docs_index_references_closeout_spec() -> None:
    text = _read(INDEX)
    assert "Prediction System Q10R-Q10W Thread Closeout" in text
    assert "docs/strategy/PREDICTION_SYSTEM_Q10R_Q10W_THREAD_CLOSEOUT_2026-06-21.md" in text

def test_closeout_spec_contains_current_head_scope_and_next_task() -> None:
    text = _read(DOC)
    for token in REQUIRED_DOC_TOKENS:
        assert token in text, token
    for token in FORBIDDEN_DOC_TOKENS:
        assert token not in text, token


def test_reentry_gate_points_to_q10x_closeout() -> None:
    text = _read(REENTRY)
    assert "2026-06-21 Q10R-Q10W WarRoom observation lane closeout" in text
    assert "docs/strategy/PREDICTION_SYSTEM_Q10R_Q10W_THREAD_CLOSEOUT_2026-06-21.md" in text
    assert "Next: PS-Q11 Scenario Prediction Core strengthening." in text
    assert "AutoTrade trigger" in text
    assert "broker/private API path" in text


def test_gpt_room_next_thread_entry_is_current() -> None:
    combined = "\n".join(_read(path) for path in (START, STATUS, NEXT, HANDOFF))
    for token in REQUIRED_ROOM_TOKENS:
        assert token in combined, token
    assert "S161 Operator/UI read-only visibility completion status index packet" not in _read(STATUS)
    assert "s161_operator_ui_decision_policy_gate_read_only_visibility_completion_status_index_packet" not in _read(STATUS)


def test_prediction_system_next_task_does_not_resume_execution() -> None:
    text = _read(NEXT)
    for token in (
        "Do not start with AutoTrade execution.",
        "Do not start with broker/mode/order work.",
        "Do not add WarRoom UI actual-read controls.",
        "Do not append approval, decision, or command ledger records.",
        "Do not create a broker/private API path.",
    ):
        assert token in text, token


def main() -> int:
    test_docs_index_references_closeout_spec()
    test_closeout_spec_contains_current_head_scope_and_next_task()
    test_reentry_gate_points_to_q10x_closeout()
    test_gpt_room_next_thread_entry_is_current()
    test_prediction_system_next_task_does_not_resume_execution()
    print("[OK] Prediction System PS-Q10X Q10R-Q10W thread closeout guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
