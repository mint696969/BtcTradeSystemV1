# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/execution_market_service_input.py
# desc: Shared L4 service input contract for execution-market consumers such as WorkRoom, UI, and AutoTrade.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary


@dataclass(frozen=True)
class ExecutionMarketServiceInput:
    contract_type: str
    service_input_role: str
    exchange: str | None
    symbol_raw: str | None
    market_uid: str | None
    source_kind: str
    source_series_id: str | None
    event_ts: str | None
    freshness: str
    is_stale: bool | None
    trust_state: str | None
    continuity_state: str | None
    interpretation_bucket: str | None
    semantic_runtime_wiring_status: str
    orderbook_wiring_status: str
    consumer_allowed: tuple[str, ...]
    capabilities: tuple[str, ...]
    blocked_by: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["consumer_allowed"] = list(self.consumer_allowed)
        data["capabilities"] = list(self.capabilities)
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        data["diagnostics"] = dict(self.diagnostics)
        return data


def _capabilities(summary: MarketSummary) -> tuple[str, ...]:
    out: list[str] = ["market_summary_anchor"]
    if summary.freshness in {"LIVE", "QUIET"}:
        out.append("freshness_usable")
    if summary.trust_state == "trusted":
        out.append("trusted_market_state")
    if summary.interpretation_bucket == "allow_structural_use":
        out.append("structural_use_allowed")
    if summary.semantic_runtime_wiring_status in {"wired", "partial"}:
        out.append("semantic_context_available")
    if summary.orderbook_wiring_status in {"wired", "partial"}:
        out.append("orderbook_context_available")
    return tuple(dict.fromkeys(out))


def _blocked_by(summary: MarketSummary) -> tuple[str, ...]:
    blocked: list[str] = []
    if not summary.market_uid:
        blocked.append("market_uid_missing")
    if not summary.symbol_raw:
        blocked.append("symbol_raw_missing")
    if summary.is_stale is True or summary.freshness == "STALE":
        blocked.append("market_summary_stale")
    if summary.trust_state not in {None, "trusted"}:
        blocked.append("market_summary_not_trusted")
    if summary.interpretation_bucket not in {None, "allow_structural_use"}:
        blocked.append("market_summary_not_structural_use")
    return tuple(dict.fromkeys(blocked))


def _warnings(summary: MarketSummary) -> tuple[str, ...]:
    warnings: list[str] = []
    if summary.continuity_state == "rest_baseline_snapshot":
        warnings.append("execution_market_rest_baseline_not_continuous_ws_series")
    if summary.semantic_runtime_wiring_status == "missing":
        warnings.append("semantic_context_missing")
    if summary.orderbook_wiring_status == "missing":
        warnings.append("orderbook_context_missing")
    return tuple(dict.fromkeys(warnings))


def build_execution_market_service_input(
    summary: MarketSummary,
    *,
    consumer_allowed: tuple[str, ...] | list[str] = ("workroom", "operator_ui", "autotrade", "l4_consumer"),
    diagnostics: dict[str, Any] | None = None,
) -> ExecutionMarketServiceInput:
    """Build a read-only shared service input for execution-market consumers.

    This is intentionally a consumer-facing contract, not a broker/order contract.
    It must remain read-only and must never imply order-send capability.
    """

    consumer_tuple = tuple(str(item) for item in consumer_allowed if str(item).strip())
    contract_diag = {
        "builder_type": "execution_market_service_input",
        "summary_type": summary.summary_type,
        "source_kind": summary.source_kind,
        "summary_freshness": summary.freshness,
        **dict(diagnostics or {}),
    }
    return ExecutionMarketServiceInput(
        contract_type="execution_market_service_input",
        service_input_role="execution_market",
        exchange=summary.exchange,
        symbol_raw=summary.symbol_raw,
        market_uid=summary.market_uid,
        source_kind=summary.source_kind,
        source_series_id=summary.source_series_id,
        event_ts=summary.event_ts,
        freshness=summary.freshness,
        is_stale=summary.is_stale,
        trust_state=summary.trust_state,
        continuity_state=summary.continuity_state,
        interpretation_bucket=summary.interpretation_bucket,
        semantic_runtime_wiring_status=summary.semantic_runtime_wiring_status,
        orderbook_wiring_status=summary.orderbook_wiring_status,
        consumer_allowed=consumer_tuple,
        capabilities=_capabilities(summary),
        blocked_by=_blocked_by(summary),
        warnings=_warnings(summary),
        diagnostics=contract_diag,
        read_only=True,
        would_send_to_broker=False,
    )
