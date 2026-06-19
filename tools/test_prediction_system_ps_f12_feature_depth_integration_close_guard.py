# path: ./tools/test_prediction_system_ps_f12_feature_depth_integration_close_guard.py
# desc: Integration close guard for PS-E2/E3/E4 feature-depth context wiring. Review-only; no new feature behavior.

from __future__ import annotations

import py_compile
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
FEATURE_DEPTH = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py"
FILES = [
    RULE,
    SYSTEM,
    FEATURE_DEPTH,
    ROOT / "tools" / "test_prediction_system_ps_e2_liquidity_feature_context_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_e3_orderbook_breakout_algo_context_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_e4_tradeflow_opportunity_context_guard.py",
    ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py",
]


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


def test_ps_f12_files_compile() -> None:
    for path in FILES:
        if not path.exists():
            raise AssertionError(f"missing file: {path}")
        py_compile.compile(str(path), doraise=True)


def test_ps_f12_static_boundaries_and_markers() -> None:
    rule = RULE.read_text(encoding="utf-8")
    system = SYSTEM.read_text(encoding="utf-8")
    feature_depth = FEATURE_DEPTH.read_text(encoding="utf-8")
    text = "\n".join((rule, system, feature_depth))
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
    hits = [item for item in forbidden if item in text]
    assert not hits, hits

    liquidity_section = rule.split("def _apply_liquidity_feature_depth_context", 1)[1].split("def _liquidity_execution_quality", 1)[0]
    generic_section = rule.split("def _apply_feature_depth_context_for_family", 1)[1].split("def _breakout_false_break", 1)[0]
    assert "context_version" not in liquidity_section
    assert 'context_version: str = "ps_e3.v1"' in generic_section
    assert '"version": context_version' in generic_section

    for marker in (
        "liquidity_feature_depth_context_supplied",
        "breakout_false_break_feature_depth_context_supplied",
        "algorithmic_participant_footprint_feature_depth_context_supplied",
        "opportunity_participation_feature_depth_context_supplied",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
        "ps_e2.v1",
        "ps_e3.v1",
        "ps_e4.v1",
    ):
        assert marker in text, marker


def test_ps_f12_rule_based_feature_depth_context_versions() -> None:
    from btcts.prediction import PredictionFamily, build_rule_based_v0_outputs

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    outputs = build_rule_based_v0_outputs(feature_depth_snapshot=_feature_depth(now), horizon_sec=300, now=now)
    by_family = {item.family: item.to_dict() for item in outputs}

    expected = {
        PredictionFamily.LIQUIDITY_EXECUTION_QUALITY: ("ps_e2.v1", None, "liquidity_feature_depth_context_supplied"),
        PredictionFamily.BREAKOUT_FALSE_BREAK: ("ps_e3.v1", "breakout_false_break", "breakout_false_break_feature_depth_context_supplied"),
        PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT: ("ps_e3.v1", "algorithmic_participant_footprint", "algorithmic_participant_footprint_feature_depth_context_supplied"),
        PredictionFamily.OPPORTUNITY_PARTICIPATION: ("ps_e4.v1", "opportunity_participation", "opportunity_participation_feature_depth_context_supplied"),
    }
    for family, (version, target_family, driver) in expected.items():
        data = by_family[family]
        context = data["values"]["feature_depth_context"]
        assert context["version"] == version
        if target_family is not None:
            assert context["target_family"] == target_family
        assert context["context_only"] is True
        assert context["primary_direction_owner"] is False
        assert context["usable_for_primary_short_horizon"] is False
        assert driver in data["drivers"]
        assert data["read_only"] is True
        assert data["non_executing"] is True
        assert data["would_send_to_broker"] is False
        assert data["broker_execution_requested"] is False
        assert data["mode_apply_requested"] is False
        assert data["command_ledger_append_requested"] is False


def test_ps_f12_prediction_system_digest_and_boundaries() -> None:
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
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert digest["liquidity_feature_depth_context_version"] == "ps_e2.v1"
    assert digest["orderbook_breakout_algo_context_version"] == "ps_e3.v1"
    assert digest["opportunity_tradeflow_context_version"] == "ps_e4.v1"
    assert digest["feature_depth_context_only"] is True
    assert digest["feature_depth_primary_direction_owner"] is False
    assert data["system_input"]["feature_snapshot"]["feature_depth_snapshot_supplied"] is True
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert all(outlook["trigger_eligibility"]["trigger_eligibility_state"] == "blocked" for outlook in data["scenario_core"]["outlooks"])


def test_ps_f12_missing_inputs_still_do_not_raise() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,), now=now)
    data = result.to_dict()
    assert len(data["outputs"]) == 33
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_ps_f12_files_compile()
    test_ps_f12_static_boundaries_and_markers()
    test_ps_f12_rule_based_feature_depth_context_versions()
    test_ps_f12_prediction_system_digest_and_boundaries()
    test_ps_f12_missing_inputs_still_do_not_raise()
    print("[OK] Prediction System PS-F12 feature-depth integration close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
