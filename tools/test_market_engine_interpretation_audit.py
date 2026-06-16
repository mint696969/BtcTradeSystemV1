# path: ./tools/test_market_engine_interpretation_audit.py
# desc: Audit current runtime interpretation decisions for representative trust/boundary/continuity cases.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json

from btcts.processing.l3_market_semantics.continuity import InterpretationEngine
from btcts.market_engine.profiles import BitflyerProfile
from btcts.market_engine.types import BoundaryReason, TrustState


def _case(
    *,
    name: str,
    trust_state: TrustState,
    boundary_reason: BoundaryReason,
    continuity_state: str | None,
) -> dict:
    return {
        "name": name,
        "trust_state": trust_state,
        "boundary_reason": boundary_reason,
        "continuity_state": continuity_state,
    }


def main() -> int:
    engine = InterpretationEngine()
    profile = BitflyerProfile()
    review_policy = profile.review_policy()

    cases = [
        _case(
            name="trusted_continuous_none",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.NONE,
            continuity_state="continuous",
        ),
        _case(
            name="trusted_resynced_none",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.NONE,
            continuity_state="resynced",
        ),
        _case(
            name="trusted_gap_detected_boundary",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.GAP_DETECTED,
            continuity_state="continuous",
        ),
        _case(
            name="trusted_resync_started_boundary",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.RESYNC_STARTED,
            continuity_state="continuous",
        ),
        _case(
            name="trusted_invalid_diff_attach_boundary",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.INVALID_DIFF_ATTACH,
            continuity_state="continuous",
        ),
        _case(
            name="provisional_continuous_none",
            trust_state=TrustState.PROVISIONAL,
            boundary_reason=BoundaryReason.NONE,
            continuity_state="continuous",
        ),
        _case(
            name="broken_gap_detected",
            trust_state=TrustState.BROKEN,
            boundary_reason=BoundaryReason.GAP_DETECTED,
            continuity_state="gap_detected",
        ),
        _case(
            name="quarantined_profile_rule",
            trust_state=TrustState.QUARANTINED,
            boundary_reason=BoundaryReason.PROFILE_RULE,
            continuity_state="continuous",
        ),
        _case(
            name="trusted_none_none",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.NONE,
            continuity_state=None,
        ),
        _case(
            name="trusted_empty_none",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.NONE,
            continuity_state="",
        ),
        _case(
            name="trusted_resync_completed_boundary",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.RESYNC_COMPLETED,
            continuity_state="continuous",
        ),
        _case(
            name="provisional_resynced_none",
            trust_state=TrustState.PROVISIONAL,
            boundary_reason=BoundaryReason.NONE,
            continuity_state="resynced",
        ),
        _case(
            name="provisional_continuous_new_stream_session",
            trust_state=TrustState.PROVISIONAL,
            boundary_reason=BoundaryReason.NEW_STREAM_SESSION,
            continuity_state="continuous",
        ),
    ]

    rows: list[dict[str, object]] = []
    for case in cases:
        decision = engine.evaluate(
            trust_state=case["trust_state"],
            boundary_reason=case["boundary_reason"],
            continuity_state=case["continuity_state"],
            review_policy=review_policy,
        )
        rows.append(
            {
                "case": case["name"],
                "trust_state": case["trust_state"].value,
                "boundary_reason": case["boundary_reason"].value,
                "continuity_state": case["continuity_state"],
                "bucket": decision.bucket,
                "reason": decision.reason,
            }
        )

    report = {
        "profile_name": profile.profile_name,
        "runtime_interpretation_cases": rows,
        "review_policy_buckets": sorted(list(review_policy.keys())),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())