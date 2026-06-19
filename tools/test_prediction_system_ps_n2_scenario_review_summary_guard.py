# path: ./tools/test_prediction_system_ps_n2_scenario_review_summary_guard.py
# desc: Guard for PS-N2 top-level scenario_review_summary digest. Review-only; no execution behavior.

from __future__ import annotations

import py_compile
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
F14 = ROOT / "tools" / "test_prediction_system_ps_f14_cc_pass_guard.py"
F15 = ROOT / "tools" / "test_prediction_system_ps_f15_next_slice_checkpoint_guard.py"
N1 = ROOT / "tools" / "test_prediction_system_ps_n1_scenario_narrative_plan_guard.py"


def _rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": 10_000_000 + idx * 1000,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _venue_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_004_000, "event_ts": ts, "market_role": "bitflyer_fx"},
    ]


def _feature_depth(now: datetime):
    from btcts.prediction import SourceTrustState, assess_source_quality, build_feature_depth_snapshot, build_provider_reliability_registry

    q = {
        "bf_fx_board": assess_source_quality(source_id="bf_fx_board", source_family="bitflyer_fx_public_board", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx_trades": assess_source_quality(source_id="bf_fx_trades", source_family="bitflyer_fx_public_trades", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    registry = build_provider_reliability_registry(source_quality_by_id=q, observed_source_ids=("bf_fx_board", "bf_fx_trades"), now=now)
    return build_feature_depth_snapshot(
        orderbook_snapshots=(
            {"source_id": "bf_fx_board", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "bid_price": 10_000_000, "ask_price": 10_001_200, "bid_depth": 5.0, "ask_depth": 4.2, "imbalance_ratio": 0.16},
        ),
        tradeflow_windows=(
            {"source_id": "bf_fx_trades", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "buy_volume": 5.4, "sell_volume": 2.4, "aggressive_buy_volume": 2.1, "aggressive_sell_volume": 0.7, "trade_count": 240},
        ),
        provider_reliability_registry=registry,
        now=now,
    )


def test_ps_n2_static_markers_and_boundaries() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, RULE, CONTRACT))
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in production_text]
    assert not hits, hits
    required = [
        "def _scenario_review_summary",
        '"scenario_review_summary": _scenario_review_summary(',
        '"version": "ps_n1.v1"',
        '"review_only": True',
        '"evidence_support"',
        '"evidence_conflicts"',
        '"refresh_or_rewrite"',
        '"context_versions"',
        '"boundaries"',
    ]
    missing = [item for item in required if item not in production_text]
    assert not missing, missing


def test_ps_n2_scenario_review_summary_shape_with_feature_depth() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_venue_snapshots(now),
        feature_depth_snapshot=_feature_depth(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    digest = data["gpt_review_digest"]
    summary = digest["scenario_review_summary"]
    assert summary["version"] == "ps_n1.v1"
    assert summary["review_only"] is True
    assert summary["primary_story"]["current_regime_state"] == data["scenario_core"]["current_regime_state"]
    assert summary["scenario_health"]["trigger_eligibility_state"] == "blocked"
    assert summary["watch_next"]
    assert isinstance(summary["evidence_support"], list)
    assert isinstance(summary["evidence_conflicts"], list)
    assert summary["refresh_or_rewrite"]["invalidation_state"] == data["scenario_core"]["invalidation_state"]
    assert summary["context_versions"]["liquidity_feature_depth_context_version"] == "ps_e2.v1"
    assert summary["context_versions"]["orderbook_breakout_algo_context_version"] == "ps_e3.v1"
    assert summary["context_versions"]["opportunity_tradeflow_context_version"] == "ps_e4.v1"
    assert summary["output_counts"]["output_count"] == len(data["outputs"])
    assert summary["output_counts"]["forecast_record_count"] == data["forecast_batch"]["record_count"]
    assert summary["boundaries"]["read_only"] is True
    assert summary["boundaries"]["non_executing"] is True
    assert summary["boundaries"]["would_collect_public_source"] is False
    assert summary["boundaries"]["would_send_to_broker"] is False
    assert summary["boundaries"]["broker_execution_requested"] is False
    assert summary["boundaries"]["mode_apply_requested"] is False
    assert summary["boundaries"]["command_ledger_append_requested"] is False
    assert summary["boundaries"]["trigger_eligibility_state"] == "blocked"
    assert summary["boundaries"]["feature_depth_context_only"] is True
    assert summary["boundaries"]["feature_depth_primary_direction_owner"] is False
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False


def test_ps_n2_scenario_review_summary_missing_inputs() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    summary = data["gpt_review_digest"]["scenario_review_summary"]
    assert summary["version"] == "ps_n1.v1"
    assert summary["review_only"] is True
    assert summary["watch_next"]
    assert summary["context_versions"]["liquidity_feature_depth_context_version"] is None
    assert summary["boundaries"]["trigger_eligibility_state"] == "blocked"
    assert summary["boundaries"]["would_send_to_broker"] is False
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33


def test_ps_n2_existing_guard_anchors_and_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, PS_G, F12, F14, F15, N1, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_f14_production_static_boundaries_and_version_markers" in F14.read_text(encoding="utf-8")
    assert "test_ps_f15_checkpoint_doc_records_next_direction" in F15.read_text(encoding="utf-8")
    assert "test_ps_n1_plan_doc_records_target_and_boundaries" in N1.read_text(encoding="utf-8")


def main() -> int:
    test_ps_n2_static_markers_and_boundaries()
    test_ps_n2_scenario_review_summary_shape_with_feature_depth()
    test_ps_n2_scenario_review_summary_missing_inputs()
    test_ps_n2_existing_guard_anchors_and_compile()
    print("[OK] Prediction System PS-N2 scenario_review_summary guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
