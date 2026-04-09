# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_usage_policy_contract.py
# desc: Minimal contract test for L3 event family and usage grade policy.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[5]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics import (
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

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())