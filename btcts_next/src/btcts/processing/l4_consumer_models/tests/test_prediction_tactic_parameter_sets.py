# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_parameter_sets.py
# desc: Verify Phase 4-A tactic parameter-set resolution stays profile-aware, comparison-safe, and rollback-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionScenarioOutput,
    TacticParameterSetRef,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_parameter_sets import (  # noqa: E402
    resolve_tactic_parameter_set_bundle,
)


def main() -> int:
    scenario_output = PredictionScenarioOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-19T14:00:00Z",
    )

    candidate_ref = TacticParameterSetRef(
        set_id="candidate-reversal-watch",
        set_version="v2",
        profile_kind="candidate",
        baseline_ref="baseline-default",
        overlay_refs=("reversal_watch_overlay", "risk_guard_overlay"),
        rollback_parent_set_id="baseline-default",
        comparison_group="phase4a-entry",
        is_active_candidate=True,
    )

    bundle = resolve_tactic_parameter_set_bundle(
        scenario_output=scenario_output,
        active_parameter_set_ref=candidate_ref,
        comparison_set_refs=None,
    )

    assert bundle.active_parameter_set_ref.set_id == "candidate-reversal-watch"
    assert len(bundle.comparison_set_refs) == 2
    assert bundle.comparison_set_refs[0].set_id == "baseline-default"
    assert bundle.comparison_set_refs[1].set_id == "candidate-reversal-watch"
    assert bundle.rollback_ready is True
    assert bundle.parameter_trace == {
        "active_set_id": "candidate-reversal-watch",
        "active_set_version": "v2",
        "profile_kind": "candidate",
        "baseline_ref": "baseline-default",
        "overlay_refs": ("reversal_watch_overlay", "risk_guard_overlay"),
        "comparison_group": "phase4a-entry",
        "rollback_parent_set_id": "baseline-default",
        "comparison_set_ids": ("baseline-default", "candidate-reversal-watch"),
        "comparison_count": 2,
    }

    default_bundle = resolve_tactic_parameter_set_bundle(
        scenario_output=scenario_output,
        active_parameter_set_ref=None,
        comparison_set_refs=None,
    )

    assert default_bundle.active_parameter_set_ref.set_id == (
        "bitflyer_spot_BTC_JPY_phase4a_default"
    )
    assert default_bundle.active_parameter_set_ref.profile_kind == "baseline"
    assert default_bundle.comparison_set_refs == (
        default_bundle.active_parameter_set_ref,
    )
    assert default_bundle.rollback_ready is False
    assert default_bundle.parameter_trace["comparison_count"] == 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())