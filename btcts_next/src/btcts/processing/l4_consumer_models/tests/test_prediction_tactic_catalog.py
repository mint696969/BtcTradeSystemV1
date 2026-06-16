# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_catalog.py
# desc: Verify Phase 4-A tactic catalog metadata stays shared, stable, and builder-independent.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared.prediction_tactic_catalog import (  # noqa: E402
    TACTIC_CATALOG,
    get_tactic_shape,
)


def main() -> int:
    assert "observe_only" in TACTIC_CATALOG
    assert "continuation_follow" in TACTIC_CATALOG
    assert "reversal_prepare" in TACTIC_CATALOG

    assert get_tactic_shape("observe_only") == (
        "observe_only",
        "no_trade_watch",
        "hold",
    )
    assert get_tactic_shape("continuation_follow") == (
        "continuation_follow",
        "continuation_bias",
        "ready",
    )
    assert get_tactic_shape("maintain_no_trade") == (
        "maintain_no_trade",
        "no_trade_bias",
        "avoid",
    )
    assert get_tactic_shape("unknown_tactic") == (
        "unknown_tactic",
        "unknown",
        "hold",
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())