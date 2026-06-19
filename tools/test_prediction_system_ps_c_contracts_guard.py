# path: ./tools/test_prediction_system_ps_c_contracts_guard.py
# desc: Focused guard for PS-C standalone Prediction System contracts.

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SYSTEM_CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"


def test_system_contract_static_boundaries() -> None:
    text = SYSTEM_CONTRACT.read_text(encoding="utf-8")
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "private_api",
        "send_order",
        "place_order",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    assert "# path: ./btcts_next/src/btcts/prediction/system_contract.py" in text
    assert "PredictionSystemInput" in text
    assert "PredictionSystemResult" in text
    assert "ScenarioCoreOutput" in text
    assert "HorizonGroupSummary" in text
    assert "would_write_collector_state" in text


def test_system_contract_exports_and_serialization() -> None:
    from btcts.prediction import (
        HorizonGroup,
        HorizonGroupSummary,
        PredictionLifetime,
        PredictionRunIdentity,
        PredictionSystemInput,
        PredictionSystemResult,
        PredictionTriggerEligibility,
        ScenarioCoreOutput,
        build_default_horizon_group_summaries,
    )

    assert HorizonGroup.NOWCAST.value == "nowcast"
    summaries = build_default_horizon_group_summaries()
    assert [item.horizon_group.value for item in summaries] == ["nowcast", "short_horizon", "mid_horizon", "long_horizon"]
    assert summaries[0].display_label_ja == "現在"
    assert 600 in summaries[1].horizons_sec

    lifetime = PredictionLifetime(
        valid_from="2026-06-19T00:00:00Z",
        valid_until="2026-06-19T00:05:00Z",
        stale_after_sec=300,
        refresh_required=False,
    )
    trigger = PredictionTriggerEligibility(trigger_eligibility_state="blocked", blockers=("standalone_not_activated",))
    horizon_summary = HorizonGroupSummary(
        horizon_group=HorizonGroup.SHORT_HORIZON,
        display_label_ja="短期",
        horizons_sec=(300, 600, 900),
        primary_label="no_edge",
        trend_bias="flat",
        lifetime=lifetime,
        trigger_eligibility=trigger,
        human_narrative_ja="短期は明確な優位がなく様子見です。",
        gpt_review_digest={"state": "no_edge"},
    )
    scenario = ScenarioCoreOutput(
        scenario_id="scenario-test",
        generated_at="2026-06-19T00:00:00Z",
        outlooks=(horizon_summary,),
        current_regime_state="range",
        trigger_eligibility_state="blocked",
    )
    result = PredictionSystemResult(
        run_identity=PredictionRunIdentity(prediction_run_id="run-test", generated_at="2026-06-19T00:00:00Z"),
        system_input=PredictionSystemInput(input_id="input-test", generated_at="2026-06-19T00:00:00Z"),
        scenario_core=scenario,
        human_narrative_ja="現在の予測シナリオです。",
        gpt_review_digest={"weak_family": []},
    )
    data = result.to_dict()
    assert data["run_identity"]["prediction_run_id"] == "run-test"
    assert data["scenario_core"]["outlooks"][0]["horizon_group"] == "short_horizon"
    assert data["scenario_core"]["outlooks"][0]["lifetime"]["stale_after_sec"] == 300
    assert data["scenario_core"]["outlooks"][0]["trigger_eligibility"]["trigger_eligibility_state"] == "blocked"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_collector_state"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["approval_append_requested"] is False


def main() -> int:
    test_system_contract_static_boundaries()
    test_system_contract_exports_and_serialization()
    print("[OK] Prediction System PS-C standalone contracts guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
