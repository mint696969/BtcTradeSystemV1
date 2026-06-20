# path: ./tools/test_prediction_system_inference_formal_spec_guard.py
# desc: Guard the canonical Prediction System inference formal spec and ensure future GPT entrypoints cannot compress the final goal.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md"
INDEX = REPO_ROOT / "docs/_INDEX.md"
ROOM_START = REPO_ROOT / "tmp/gpt_room/NEXT_THREAD_PREDICTION_SYSTEM_PS_Q2_SOURCE_ARTIFACT_INPUT_COVERAGE_START_HERE.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for path in (SPEC, INDEX, ROOM_START):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(REPO_ROOT)}")

    if not failures:
        spec = _read(SPEC)
        index = _read(INDEX)
        room_start = _read(ROOM_START)
        required_spec_tokens = (
            "Complete a standalone inference system",
            "WarRoom",
            "future AutoTrade trigger candidates",
            "Machine-readable trigger-candidate output",
            "Human-readable WarRoom prediction review",
            "inference, not prophecy",
            "100% accuracy",
            "proprietary reference indicator",
            "estimated_signal_strength_percent",
            "estimated_reference_hit_rate_percent",
            "0% = prediction unavailable",
            "99% = maximum display value",
            "100% = forbidden",
            "Do not force most predictions into very low percentages",
            "Prediction System does not trade",
            "Prediction System does not call broker/private APIs",
            "Prediction System must support 11 families",
            "trigger_eligibility_state remains blocked by default",
            "PS-Q2: source / artifact input coverage start",
            "PS-Q9: explicit AutoTrade return gate / trigger integration design",
            "Input coverage matrix",
            "Source contribution ledger",
            "TriggerEligibility state machine",
            "WarRoom packet schema",
            "Probability-improvement principle",
            "improve decision odds compared with blind or random direction selection",
            "blindly choosing red/black",
            "adjustable mechanisms for improving correct-reference probability",
            "raise the probability of making a better-informed real-money trading decision",
            "Implementation workflow mandate",
            "one-shot patch runner workflow",
            "Evidence hierarchy and conflict resolution",
            "Prediction System must not treat all information sources as equal",
            "Tier 0: source quality / freshness / integrity gate",
            "Tier 1: local executable-market truth",
            "Tier 2: multi-timeframe price/technical structure",
            "Tier 3: cross-venue spot confirmation",
            "Tier 4: derivatives and leverage context",
            "Tier 5: macro / session / calendar / incident / news context",
            "Tier 6: AI/pro participant behavior hypothesis",
            "Tier 7: replay / outcome / calibration prior",
            "If all required fresh/trusted tiers align and replay/calibration does not object",
            "evidence_hierarchy_version",
            "dominant_evidence_tier",
            "source_contribution_ledger",
            "signal_strength_cap_reason",
            "Extensible reference-source registry",
            "New sources may be added only through an explicit source registry / input contract",
            "direction_ownership: none / supporting / primary_candidate",
            "allowed_effects: confirm / warn / cap / veto / strengthen / weaken / context_only",
            "New sources must start conservative until evaluated",
            "source_registry_version",
            "reference_source_registry_ids",
            "Context-specific evidence profiles",
            "Source reliability, evidence priority, and useful weighting must not be treated as one global value",
            "Evidence hierarchy defines the global default order",
            "Context-specific evidence profiles define how that hierarchy is applied",
            "evidence_profile_id",
            "evidence_profile_version",
            "primary_evidence_tiers",
            "secondary_evidence_tiers",
            "caution_only_tiers",
            "cap_only_tiers",
            "veto_tiers",
            "context_weight_overrides",
            "signal_strength_floor",
            "signal_strength_ceiling",
            "Context-specific evidence profile contract",
            "Signal-strength percentage contract",
        )
        for token in required_spec_tokens:
            if token not in spec:
                failures.append(f"spec missing token: {token}")
        if "PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md" not in index:
            failures.append("docs/_INDEX.md does not reference inference formal spec")
        if "PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md" not in room_start:
            failures.append("PS-Q2 start-here does not reference inference formal spec")
        forbidden = (
            "AutoTrade trigger enabled",
            "broker execution enabled",
            "command ledger append enabled",
        )
        for token in forbidden:
            if token in spec:
                failures.append(f"forbidden enablement token present: {token}")
        if spec.count("```") % 2 != 0:
            failures.append("spec has unbalanced markdown code fences")
    if failures:
        print("[FAIL] Prediction System inference formal spec guard")
        for item in failures:
            print(f"- {item}")
        return 1
    print("[OK] Prediction System inference formal spec guard")
    return 0


def test_prediction_system_inference_formal_spec_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
