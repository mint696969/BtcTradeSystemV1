# path: ./tools/test_prediction_system_ps_d1_provider_reliability_guard.py
# desc: Focused guard for PS-D1 provider reliability registry skeleton.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SOURCE_QUALITY = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "source_quality.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"


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


def _snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_010_000, "event_ts": ts, "market_role": "bitflyer_fx"},
        {"source_id": "mystery_provider", "venue": "Unknown", "symbol": "BTC_JPY_REF", "price": 10_012_000, "event_ts": ts, "market_role": "reference"},
    ]


def test_static_boundaries_and_provider_markers() -> None:
    text = SOURCE_QUALITY.read_text(encoding="utf-8") + "\n" + SYSTEM.read_text(encoding="utf-8")
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
    assert "ProviderReliabilityStatus" in text
    assert "ProviderReliabilityRegistry" in text
    assert "build_provider_reliability_registry" in text
    assert "primary_direction_owner_allowed" in text


def test_provider_reliability_registry_is_context_only() -> None:
    from btcts.prediction import SourceTrustState, assess_source_quality, build_provider_reliability_registry

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    q = {
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="bitflyer_spot", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="bitflyer_fx", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    registry = build_provider_reliability_registry(source_quality_by_id=q, observed_source_ids=("bf_spot", "bf_fx", "unknown_macro"), now=now)
    data = registry.to_dict()
    assert data["provider_count"] >= 2
    assert data["usable_provider_count"] >= 1
    assert data["context_only"] is True
    assert data["primary_direction_owner_allowed"] is False
    assert "unknown_macro" in data["unknown_source_ids"]
    assert any(provider["provider_family"] == "unknown_provider" for provider in data["providers"])
    assert all(provider["primary_direction_owner"] is False for provider in data["providers"])
    assert all(provider["usable_for_primary_short_horizon"] is False for provider in data["providers"])
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_send_to_broker"] is False


def test_prediction_system_surfaces_provider_registry_summary() -> None:
    from btcts.prediction import HorizonGroup, SourceTrustState, assess_source_quality, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    q = {
        "bf_spot": assess_source_quality(source_id="bf_spot", source_family="bitflyer_spot", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx": assess_source_quality(source_id="bf_fx", source_family="bitflyer_fx", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_snapshots(now),
        source_quality_by_id=q,
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    provider_summary = data["system_input"]["provider_quality_summary"]["provider_reliability_registry"]
    source_summary = data["inference_bundle"]["source_quality_summary"]["provider_reliability_registry"]
    assert provider_summary["context_only"] is True
    assert provider_summary["primary_direction_owner_allowed"] is False
    assert "mystery_provider" in provider_summary["unknown_source_ids"]
    assert source_summary["provider_count"] == provider_summary["provider_count"]
    assert data["gpt_review_digest"]["provider_reliability_version"] == "ps_d1.v1"
    assert data["gpt_review_digest"]["provider_reliability_context_only"] is True
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_send_to_broker"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_provider_markers()
    test_provider_reliability_registry_is_context_only()
    test_prediction_system_surfaces_provider_registry_summary()
    print("[OK] Prediction System PS-D1 provider reliability guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
