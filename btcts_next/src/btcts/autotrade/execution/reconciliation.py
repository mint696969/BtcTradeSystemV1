# path: ./btcts_next/src/btcts/autotrade/execution/reconciliation.py
# desc: SR-FX read-only private-state reconciliation. No broker calls and no order send.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple

from btcts.autotrade.execution.order_state import PaperOrder, PaperOrderStatus
from btcts.autotrade.execution.paper_ledger import PaperOrderLedgerSummary, summarize_paper_order_ledger


@dataclass(frozen=True)
class FxReconciliationResult:
    ok: bool
    product_code: str
    market_uid: str
    private_state_known_and_fresh: bool
    account_clear_for_new_auto_entry: bool
    position_item_count: int
    open_order_item_count: int
    own_execution_item_count: int
    active_paper_order_count: int
    terminal_paper_order_count: int
    paper_order_ledger_path: str | None = None
    paper_order_ledger_skipped_rows: int = 0
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _int_at(mapping: Mapping[str, Any], key: str, default: int = 0) -> int:
    try:
        return max(int(mapping.get(key, default) or 0), 0)
    except Exception:
        return default


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def private_readiness_counts(private_readiness: Mapping[str, Any]) -> Dict[str, int]:
    summary = private_readiness.get("account_state_summary")
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "position_item_count": _int_at(summary, "position_item_count"),
        "open_order_item_count": _int_at(summary, "open_order_item_count"),
        "own_execution_item_count": _int_at(summary, "own_execution_item_count"),
    }


def paper_order_counts(paper_orders: Iterable[PaperOrder]) -> Dict[str, int]:
    active = 0
    terminal = 0
    for order in paper_orders:
        if order.status in {
            PaperOrderStatus.FILLED,
            PaperOrderStatus.CANCELED,
            PaperOrderStatus.EXPIRED,
            PaperOrderStatus.REJECTED,
        }:
            terminal += 1
        else:
            active += 1
    return {"active_paper_order_count": active, "terminal_paper_order_count": terminal}


def reconcile_fx_private_state_with_paper(
    *,
    private_readiness: Mapping[str, Any],
    paper_orders: Iterable[PaperOrder] = (),
    require_account_clear_for_new_auto_entry: bool = True,
) -> FxReconciliationResult:
    blocked: list[str] = []
    warnings: list[str] = []

    product_code = str(private_readiness.get("product_code") or "")
    market_uid = str(private_readiness.get("market_uid") or "")
    private_fresh = _bool_at(private_readiness, "private_state_known_and_fresh")
    account_clear = _bool_at(private_readiness, "account_clear_for_new_auto_entry")

    if product_code != "FX_BTC_JPY":
        blocked.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        blocked.append("execution_market_uid_mismatch")
    if not private_fresh:
        blocked.append("private_state_not_fresh")
    if require_account_clear_for_new_auto_entry and not account_clear:
        blocked.append("account_not_clear_for_new_auto_entry")

    counts = private_readiness_counts(private_readiness)
    if counts["position_item_count"] > 0:
        warnings.append("exchange_positions_detected")
    if counts["open_order_item_count"] > 0:
        warnings.append("exchange_open_orders_detected")

    paper_counts = paper_order_counts(tuple(paper_orders))
    if paper_counts["active_paper_order_count"] > 0 and counts["open_order_item_count"] == 0:
        warnings.append("active_paper_orders_without_exchange_open_orders")
    if paper_counts["active_paper_order_count"] == 0 and counts["open_order_item_count"] > 0:
        warnings.append("exchange_open_orders_without_active_paper_orders")

    return FxReconciliationResult(
        ok=not blocked,
        product_code=product_code,
        market_uid=market_uid,
        private_state_known_and_fresh=private_fresh,
        account_clear_for_new_auto_entry=account_clear,
        position_item_count=counts["position_item_count"],
        open_order_item_count=counts["open_order_item_count"],
        own_execution_item_count=counts["own_execution_item_count"],
        active_paper_order_count=paper_counts["active_paper_order_count"],
        terminal_paper_order_count=paper_counts["terminal_paper_order_count"],
        paper_order_ledger_path=None,
        paper_order_ledger_skipped_rows=0,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        would_send_to_broker=False,
        read_only=True,
    )



def reconcile_fx_private_state_with_paper_ledger(
    *,
    private_readiness: Mapping[str, Any],
    paper_order_ledger_path: Path | None = None,
    max_lines: int | None = 1000,
    require_account_clear_for_new_auto_entry: bool = True,
) -> FxReconciliationResult:
    """Reconcile private state using the persisted paper-order ledger summary.

    This is read-only and fail-soft: malformed ledger rows are counted in
    paper_order_ledger_skipped_rows and reported as warnings, but do not crash
    readiness surfaces.
    """
    summary: PaperOrderLedgerSummary = summarize_paper_order_ledger(paper_order_ledger_path, max_lines=max_lines)
    blocked: list[str] = []
    warnings: list[str] = []

    product_code = str(private_readiness.get("product_code") or "")
    market_uid = str(private_readiness.get("market_uid") or "")
    private_fresh = _bool_at(private_readiness, "private_state_known_and_fresh")
    account_clear = _bool_at(private_readiness, "account_clear_for_new_auto_entry")

    if product_code != "FX_BTC_JPY":
        blocked.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        blocked.append("execution_market_uid_mismatch")
    if not private_fresh:
        blocked.append("private_state_not_fresh")
    if require_account_clear_for_new_auto_entry and not account_clear:
        blocked.append("account_not_clear_for_new_auto_entry")

    counts = private_readiness_counts(private_readiness)
    if counts["position_item_count"] > 0:
        warnings.append("exchange_positions_detected")
    if counts["open_order_item_count"] > 0:
        warnings.append("exchange_open_orders_detected")

    active_paper = int(summary.active_paper_order_count or 0)
    terminal_paper = int(summary.terminal_paper_order_count or 0)
    if active_paper > 0 and counts["open_order_item_count"] == 0:
        warnings.append("active_paper_orders_without_exchange_open_orders")
    if active_paper == 0 and counts["open_order_item_count"] > 0:
        warnings.append("exchange_open_orders_without_active_paper_orders")
    if summary.skipped_rows > 0:
        warnings.append("paper_order_ledger_has_skipped_rows")

    return FxReconciliationResult(
        ok=not blocked,
        product_code=product_code,
        market_uid=market_uid,
        private_state_known_and_fresh=private_fresh,
        account_clear_for_new_auto_entry=account_clear,
        position_item_count=counts["position_item_count"],
        open_order_item_count=counts["open_order_item_count"],
        own_execution_item_count=counts["own_execution_item_count"],
        active_paper_order_count=active_paper,
        terminal_paper_order_count=terminal_paper,
        paper_order_ledger_path=str(summary.path),
        paper_order_ledger_skipped_rows=int(summary.skipped_rows or 0),
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        would_send_to_broker=False,
        read_only=True,
    )
