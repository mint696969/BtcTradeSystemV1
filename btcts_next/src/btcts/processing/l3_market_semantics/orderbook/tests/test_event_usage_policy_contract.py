# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_usage_policy_contract.py
# desc: Minimal contract test for L3 event family and usage grade policy.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[5]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics import (
    build_event_contract_row,
    build_event_usage_contract_rows,
    build_event_usage_summary,
    resolve_event_family,
    resolve_usage_grade,
)


def main() -> int:
    assert resolve_event_family("pressure_shift") == "pressure"
    assert resolve_event_family("near_wall_continued") == "wall"
    assert resolve_event_family("support_continued") == "support_resistance"
    assert resolve_event_family("sweep_candidate") == "sweep"
    assert resolve_event_family("absorption_candidate") == "absorption"
    assert resolve_event_family("unknown_event_name") == "unknown"

    assert resolve_usage_grade("allow_structural_use", "pressure") == "strong"
    assert resolve_usage_grade("allow_structural_use", "sweep") == "strong"

    assert resolve_usage_grade("observe_only", "pressure") == "watch_weak"
    assert resolve_usage_grade("observe_only", "wall") == "watch"
    assert resolve_usage_grade("observe_only", "support_resistance") == "watch"
    assert resolve_usage_grade("observe_only", "sweep") == "tentative"
    assert resolve_usage_grade("observe_only", "absorption") == "tentative"

    assert resolve_usage_grade("reanchor_required", "pressure") == "invalid"
    assert resolve_usage_grade("reanchor_required", "wall") == "invalid"

    assert resolve_usage_grade("unknown_bucket", "pressure") == "unknown"
    assert resolve_usage_grade("observe_only", "unknown_family") == "watch"

    contract_row = build_event_contract_row(
        "support_candidate",
        "observe_only",
        trust_state="provisional",
        side="bid",
    )
    assert contract_row["event_name"] == "support_candidate"
    assert contract_row["event_family"] == "support_resistance"
    assert contract_row["usage_grade"] == "watch"
    assert contract_row["interpretation_bucket"] == "observe_only"
    assert contract_row["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert contract_row["confidence"] == 0.55
    assert contract_row["trust_bucket"] == "degraded"
    assert contract_row["consumer_allowed"] == ["ui", "alert", "ai"]
    assert contract_row["actionability"] == "review"
    assert contract_row["forecast_horizon_hint"] == "short"
    assert contract_row["half_life_sec"] == 30
    assert contract_row["invalidates_on"] == [
        "series_boundary",
        "reanchor_required",
    ]
    assert contract_row["evidence_refs"] == []
    assert contract_row["side"] == "bid"

    family_rows = build_event_usage_contract_rows("observe_only")
    assert family_rows[0]["contract_source"] == "l3_event_usage_policy"
    assert family_rows[0]["interpretation_bucket"] == "observe_only"
    assert family_rows[0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"

    summary = build_event_usage_summary(
        "observe_only",
        event_names=[
            "support_candidate",
            "unknown_event_name",
        ],
        active_event_contracts=[
            {
                "event_name": "support_candidate",
                "trust_bucket": "degraded",
                "interpretation_bucket": "observe_only",
                "consumer_allowed": ["ui", "alert", "ai"],
            },
            {
                "event_name": "unknown_event_name",
                "trust_bucket": "blocked",
                "interpretation_bucket": "reanchor_required",
                "consumer_allowed": ["ui", "alert"],
            },
        ],
    )
    assert summary["contract_source"] == "l3_event_usage_policy"
    assert summary["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary["observer_status"] == "caution"
    assert summary["active_event_count"] == 2
    assert summary["mapped_event_count"] == 1
    assert summary["unknown_event_count"] == 1
    assert summary["event_family_distribution"] == {
        "support_resistance": 1,
        "unknown": 1,
    }
    assert summary["trust_bucket_distribution"] == {
        "blocked": 1,
        "degraded": 1,
    }
    assert summary["interpretation_bucket_distribution"] == {
        "observe_only": 1,
        "reanchor_required": 1,
    }
    assert summary["consumer_distribution"] == {
        "ai": 1,
        "alert": 2,
        "ui": 2,
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())