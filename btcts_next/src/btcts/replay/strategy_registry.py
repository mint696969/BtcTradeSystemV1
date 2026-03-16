# path: ./btcts_next/src/btcts/replay/strategy_registry.py
# desc: Strategy registry for replay strategy comparison.

from __future__ import annotations

from .strategy_rules import (
    microstructure_strategy,
    regime_aware_microstructure_strategy,
)


def empty_strategy(row, position):
    return None


STRATEGY_REGISTRY = {
    "microstructure_v1": microstructure_strategy,
    "regime_aware_microstructure_v1": regime_aware_microstructure_strategy,
    "baseline_none": empty_strategy,
}