# path: ./tools/test_prediction_system_ps_f_complete_review_guard.py
# desc: Guard for PS-F complete 11-family review document and current family coverage.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_F_COMPLETE_11_FAMILY_REVIEW_BTC_BITFLYER_2026-06-19.md"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"

REQUIRED_FAMILIES = [
    "market_regime",
    "trend_bias",
    "reversal_zone",
    "volatility_risk",
    "liquidity_execution_quality",
    "breakout_false_break",
    "opportunity_participation",
    "cross_venue_confirmation",
    "macro_risk_context",
    "algorithmic_participant_footprint",
    "human_technical_structure",
]


def _rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": 10_000_000 + idx * 700,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_020_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_021_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "binance", "venue": "Binance", "symbol": "BTC_JPY_REF", "price": 10_022_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_review_document_required_sections() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "Prediction System PS-F Complete 11-Family Review",
        "PS-F is functionally complete at the rule-output coverage level",
        "Hard boundaries preserved",
        "Current 11-family coverage",
        "Weak/proxy-only family index",
        "Recommended next work: PS-H before PS-E",
        "PS-H1: Scenario Core lite integration",
        "Scenario integration remains the next bottleneck",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    for family in REQUIRED_FAMILIES:
        assert family in text


def test_static_boundaries() -> None:
    text = RULE.read_text(encoding="utf-8") + "\n" + SYSTEM.read_text(encoding="utf-8")
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


def test_runtime_family_coverage_after_ps_f() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result
    from btcts.prediction.rule_based_v0 import INITIAL_FAMILIES

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    families = [family.value for family in INITIAL_FAMILIES]
    assert families == REQUIRED_FAMILIES
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert data["gpt_review_digest"]["family_count"] == 11
    assert sorted(data["inference_bundle"]["families_present"]) == sorted(REQUIRED_FAMILIES)
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_review_document_required_sections()
    test_static_boundaries()
    test_runtime_family_coverage_after_ps_f()
    print("[OK] Prediction System PS-F complete review guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
