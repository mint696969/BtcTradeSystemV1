# path: ./tools/test_prediction_system_thread_close_handoff_guard.py
# desc: Guard for Prediction System thread-close handoff and PS-Q8F roadmap status docs.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md"
STATUS_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_ROADMAP_STATUS_PS_Q8F_HANDOFF_2026-06-21.md"
HANDOFF = REPO_ROOT / "tmp/gpt_room/memory/handoffs/2026-06-21_prediction_system_ps_q8f_thread_close_handoff.md"
START = REPO_ROOT / "tmp/gpt_room/NEXT_THREAD_PREDICTION_SYSTEM_PS_Q2_SOURCE_ARTIFACT_INPUT_COVERAGE_START_HERE.md"

REQUIRED_MARKERS = {
    SPEC: (
        "## 19. PS-Q8F implementation checkpoint and next-thread boundary",
        "Checkpoint commit: `a601442b`",
        "PS-Q8F human_observation_passed",
        "Actual latest payload read is not implemented.",
        "PS-Q9A: latest payload actual-read preflight final contract.",
        "Do not begin PS-Q9B actual read until PS-Q9A is committed and guarded.",
    ),
    STATUS_DOC: (
        "Prediction System Roadmap Status at PS-Q8F Thread Handoff",
        "Checkpoint commit: `a601442b`",
        "Overall final-goal progress: about 60-65%.",
        "PS-Q8F: human UI observation passed.",
        "PS-Q9A: latest payload actual-read preflight final contract.",
        "No actual hot/latest file read before PS-Q9B.",
    ),
    HANDOFF: (
        "Prediction System PS-Q8F Thread-Close Handoff",
        "Checkpoint commit: `a601442b`",
        "WarRoom UI entrance is implemented and human-observed.",
        "PS-Q9A must be contract/preflight only and must not read files.",
        "Do not implement actual file read.",
    ),
    START: (
        "PS-Q8F manual UI observation result recorded",
        "Observation state: human_observation_passed",
        "Runtime remains disconnected",
    ),
}

FORBIDDEN_MISLEADING_PHRASES = (
    "Actual latest payload read is implemented.",
    "Actual payload decode is implemented.",
    "AutoTrade trigger execution is implemented.",
    "broker/private API control is exposed without negation",
    "PS-Q9B actual read completed",
    "authorization grant enabled",
    "approval write enabled",
)


def _read(path: Path) -> str:
    assert path.exists(), f"missing file: {path.relative_to(REPO_ROOT)}"
    return path.read_text(encoding="utf-8")


def test_thread_close_docs_have_required_markers() -> None:
    for path, markers in REQUIRED_MARKERS.items():
        text = _read(path)
        for marker in markers:
            assert marker in text, f"missing marker in {path.relative_to(REPO_ROOT)}: {marker}"


def test_thread_close_docs_do_not_claim_unsafe_completion() -> None:
    combined = "\n".join(_read(path) for path in REQUIRED_MARKERS)
    for phrase in FORBIDDEN_MISLEADING_PHRASES:
        assert phrase not in combined, phrase


def test_next_slice_is_q9a_not_actual_read() -> None:
    text = _read(HANDOFF) + "\n" + _read(STATUS_DOC) + "\n" + _read(SPEC)
    assert text.count("PS-Q9A: latest payload actual-read preflight final contract.") >= 3
    assert "PS-Q9A must be contract/preflight only and must not read files." in text
    assert "Do not begin PS-Q9B actual read until PS-Q9A is committed and guarded." in text


def main() -> int:
    test_thread_close_docs_have_required_markers()
    test_thread_close_docs_do_not_claim_unsafe_completion()
    test_next_slice_is_q9a_not_actual_read()
    print("[OK] Prediction System thread-close handoff guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
