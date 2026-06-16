# path: ./btcts_next/src/btcts/autotrade/README.md
# desc: AutoTrade package overview and boundaries.

# AutoTrade package

This package contains the logic-driven AutoTrade system.

## Role

```text
L1-L4 provide read-only market truth and shared read models.
AutoTrade reads those outputs through explicit read-model adapters.
AutoTrade creates deterministic candidates, applies risk gates, records ledgers, and later owns execution runtime boundaries.
GPT/human review logs and parameter results after the fact.
```

## Non-goals

```text
- GPT/AI is not the live order decision maker.
- Operator UI is not the execution source of truth.
- L3/L4 must not import AutoTrade.
- AutoTrade must not mutate L1-L4 market truth.
```

## Responsibility folders

```text
config/      parameter sets, defaults, limits
read_model/  non-UI L1-L4 AutoTrade snapshot and freshness/forecast inputs
strategy/    deterministic strategy/profile/candidate generation
risk/        risk gates, exposure, kill switch, fail-closed decisions
execution/   order intents, broker adapter boundary, reconciliation, order state
ledger/      decision/order/fill/position/performance/review ledgers
replay/      shadow/paper/replay runners and scenario validation
```

## Import direction

```text
L1-L4 -> autotrade.read_model -> autotrade.strategy -> autotrade.risk -> autotrade.execution -> autotrade.ledger
operator_ui -> autotrade read/status/command APIs only
GPT review -> ledger exports only
```

## Hard boundary

```text
If state is unknown, do not add exposure.
If safety and edge conflict, safety wins.
If it is not logged, it did not happen.
```
