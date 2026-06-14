# path: ./btcts_next/src/btcts/autotrade/execution/paper_position.py
# desc: Read-only SR-FX paper position and realized PnL summary from paper lifecycle ledger. No broker calls.

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.paper_ledger import default_paper_order_ledger_path, read_paper_order_ledger_rows


@dataclass(frozen=True)
class PaperFillEvent:
    record_id: str
    recorded_at: str
    order_id: str
    decision_id: str
    side: str
    size: float
    price: float
    product_code: str | None
    market_uid: str | None
    transition_event: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PaperPositionSummary:
    path: Path
    exists: bool
    total_rows: int
    fill_event_count: int
    buy_fill_size: float
    sell_fill_size: float
    gross_fill_size: float
    net_position_size: float
    position_side: str
    average_entry_price: float | None
    realized_pnl: float
    realized_pnl_currency: str
    latest_record_id: str | None = None
    latest_recorded_at: str | None = None
    latest_order_id: str | None = None
    latest_decision_id: str | None = None
    latest_fill_side: str | None = None
    latest_fill_size: float | None = None
    latest_fill_price: float | None = None
    product_code: str | None = None
    market_uid: str | None = None
    skipped_rows: int = 0
    error_samples: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _transition_of(row: Dict[str, Any]) -> Dict[str, Any]:
    transition = row.get("transition")
    return dict(transition) if isinstance(transition, dict) else {}


def _order_of(row: Dict[str, Any]) -> Dict[str, Any]:
    order = row.get("order")
    return dict(order) if isinstance(order, dict) else {}


def _intent_of(order: Dict[str, Any]) -> Dict[str, Any]:
    intent = order.get("intent")
    return dict(intent) if isinstance(intent, dict) else {}


def _fill_event_from_row(row: Dict[str, Any]) -> PaperFillEvent | None:
    transition = _transition_of(row)
    fill_size = _float_or_none(transition.get("fill_size"))
    fill_price = _float_or_none(transition.get("fill_price"))
    if fill_size is None or fill_size <= 0.0 or fill_price is None:
        return None

    order = _order_of(row)
    intent = _intent_of(order)
    side = str(intent.get("side") or "").lower().strip()
    if side not in {"buy", "sell"}:
        return None

    return PaperFillEvent(
        record_id=str(row.get("record_id") or ""),
        recorded_at=str(row.get("recorded_at") or ""),
        order_id=str(order.get("order_id") or row.get("order_id") or ""),
        decision_id=str(intent.get("decision_id") or row.get("decision_id") or ""),
        side=side,
        size=float(fill_size),
        price=float(fill_price),
        product_code=str(intent.get("product_code")) if intent.get("product_code") is not None else None,
        market_uid=str(intent.get("market_uid")) if intent.get("market_uid") is not None else None,
        transition_event=str(transition.get("event") or row.get("transition_event") or "") or None,
    )


def _apply_fill(*, position_size: float, average_price: float | None, realized_pnl: float, fill: PaperFillEvent) -> tuple[float, float | None, float]:
    signed_fill = fill.size if fill.side == "buy" else -fill.size
    if position_size == 0.0 or (position_size > 0.0 and signed_fill > 0.0) or (position_size < 0.0 and signed_fill < 0.0):
        new_abs = abs(position_size) + abs(signed_fill)
        current_notional = (average_price or 0.0) * abs(position_size)
        fill_notional = fill.price * abs(signed_fill)
        new_avg = (current_notional + fill_notional) / new_abs if new_abs > 0.0 else None
        return position_size + signed_fill, new_avg, realized_pnl

    close_qty = min(abs(position_size), abs(signed_fill))
    avg = float(average_price or 0.0)
    if position_size > 0.0:
        realized_pnl += (fill.price - avg) * close_qty
    else:
        realized_pnl += (avg - fill.price) * close_qty

    new_position = position_size + signed_fill
    if new_position == 0.0:
        return 0.0, None, realized_pnl
    if (position_size > 0.0 and new_position > 0.0) or (position_size < 0.0 and new_position < 0.0):
        return new_position, average_price, realized_pnl
    return new_position, fill.price, realized_pnl


def summarize_paper_position_from_lifecycle(path: Path | None = None, *, max_lines: int | None = 1000) -> PaperPositionSummary:
    target = path or default_paper_order_ledger_path(ensure=False)
    read = read_paper_order_ledger_rows(target, max_lines=max_lines)
    fills: list[PaperFillEvent] = []
    warnings: list[str] = []
    for row in read.rows:
        fill = _fill_event_from_row(row)
        if fill is not None:
            fills.append(fill)

    position_size = 0.0
    average_price: float | None = None
    realized_pnl = 0.0
    buy_fill_size = 0.0
    sell_fill_size = 0.0
    product_code: str | None = None
    market_uid: str | None = None
    for fill in fills:
        if fill.side == "buy":
            buy_fill_size += fill.size
        else:
            sell_fill_size += fill.size
        product_code = fill.product_code or product_code
        market_uid = fill.market_uid or market_uid
        position_size, average_price, realized_pnl = _apply_fill(
            position_size=position_size,
            average_price=average_price,
            realized_pnl=realized_pnl,
            fill=fill,
        )

    if read.skipped_count > 0:
        warnings.append("paper_position_summary_skipped_malformed_rows")
    latest = fills[-1] if fills else None
    side = "flat"
    if position_size > 0.0:
        side = "long"
    elif position_size < 0.0:
        side = "short"

    return PaperPositionSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(read.rows),
        fill_event_count=len(fills),
        buy_fill_size=buy_fill_size,
        sell_fill_size=sell_fill_size,
        gross_fill_size=buy_fill_size + sell_fill_size,
        net_position_size=position_size,
        position_side=side,
        average_entry_price=average_price,
        realized_pnl=realized_pnl,
        realized_pnl_currency="JPY",
        latest_record_id=latest.record_id if latest is not None else None,
        latest_recorded_at=latest.recorded_at if latest is not None else None,
        latest_order_id=latest.order_id if latest is not None else None,
        latest_decision_id=latest.decision_id if latest is not None else None,
        latest_fill_side=latest.side if latest is not None else None,
        latest_fill_size=latest.size if latest is not None else None,
        latest_fill_price=latest.price if latest is not None else None,
        product_code=product_code,
        market_uid=market_uid,
        skipped_rows=read.skipped_count,
        error_samples=read.error_samples,
        warnings=tuple(dict.fromkeys(warnings)),
        read_only=True,
        would_send_to_broker=False,
    )
