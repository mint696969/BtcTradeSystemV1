# path: ./btcts_next/src/btcts/autotrade/boundary.py
# desc: Declarative responsibility boundaries for AutoTrade package.

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Tuple


@dataclass(frozen=True)
class AutoTradeLayerBoundary:
    name: str
    purpose: str
    may_do: Tuple[str, ...]
    must_not_do: Tuple[str, ...]


AUTOTRADE_PACKAGE: Final[str] = "btcts.autotrade"

RESPONSIBILITY_BOUNDARIES: Final[Tuple[AutoTradeLayerBoundary, ...]] = (
    AutoTradeLayerBoundary(
        name="read_model",
        purpose="Build a non-UI AutoTrade snapshot from L1-L4 read-only outputs.",
        may_do=(
            "read explicit L1-L4 adapter outputs",
            "normalize timestamps and freshness",
            "produce AutoTrade snapshot and forecast inputs",
        ),
        must_not_do=(
            "create new L3 market meaning",
            "import Operator UI components",
            "place or cancel orders",
            "mutate L1-L4 state",
        ),
    ),
    AutoTradeLayerBoundary(
        name="strategy",
        purpose="Create deterministic action candidates from snapshot, forecast, and parameter set.",
        may_do=(
            "select strategy/profile",
            "build entry/hold/exit/cancel/reprice candidates",
            "attach reason codes",
        ),
        must_not_do=(
            "call broker APIs",
            "mutate order state",
            "override risk gates",
        ),
    ),
    AutoTradeLayerBoundary(
        name="risk",
        purpose="Allow, block, shrink, or halt candidates using fail-closed risk rules.",
        may_do=(
            "apply safety gates",
            "apply exposure and margin limits",
            "convert approved candidate into executable intent boundary",
        ),
        must_not_do=(
            "send broker orders directly",
            "ignore kill switch",
            "allow new exposure when state is unknown",
        ),
    ),
    AutoTradeLayerBoundary(
        name="execution",
        purpose="Own order intent execution boundary, broker adapter, idempotency, and reconciliation.",
        may_do=(
            "manage order ids and order state",
            "talk to broker adapter after risk approval",
            "reconcile fills, positions, margin, and open orders",
        ),
        must_not_do=(
            "compute market meaning",
            "select strategy",
            "execute without risk-approved intent",
        ),
    ),
    AutoTradeLayerBoundary(
        name="ledger",
        purpose="Persist all decisions, commands, outcomes, performance, and review exports.",
        may_do=(
            "log allowed and blocked decisions",
            "link decision/order/fill/position/performance records",
            "export review bundles",
        ),
        must_not_do=(
            "send orders",
            "change live parameters silently",
        ),
    ),
)

FORBIDDEN_UPSTREAM_IMPORTERS: Final[Tuple[str, ...]] = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)

FORBIDDEN_AUTOTRADE_IMPORTS: Final[Tuple[str, str]] = (
    ("read_model", "btcts.apps.operator_ui"),
    ("read_model", "btcts.autotrade.execution"),
    ("strategy", "btcts.autotrade.execution"),
    ("strategy", "btcts.apps.operator_ui"),
    ("risk", "btcts.apps.operator_ui"),
)


def boundary_names() -> Tuple[str, ...]:
    return tuple(boundary.name for boundary in RESPONSIBILITY_BOUNDARIES)
