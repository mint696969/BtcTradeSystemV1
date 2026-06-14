# path: ./btcts_next/src/btcts/autotrade/execution/paper_ledger.py
# desc: SR-FX paper order ledger persistence under AutoTrade hot runtime. No broker calls.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.intents import OrderSide, OrderType, build_order_intent_from_decision
from btcts.autotrade.execution.order_state import PaperOrder, PaperOrderStatus
from btcts.autotrade.execution.paper_intent import PaperOrderIntentBuildResult
from btcts.autotrade.runtime_paths import decision_ledger_path


@dataclass(frozen=True)
class PaperOrderLedgerRecord:
    record_id: str
    recorded_at: str
    accepted: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    order: PaperOrder | None
    intent_build: PaperOrderIntentBuildResult
    ledger_event: str = "autotrade.paper_order_recorded"
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_event": self.ledger_event,
            "record_id": self.record_id,
            "recorded_at": self.recorded_at,
            "accepted": self.accepted,
            "blocked_by": list(self.blocked_by),
            "warnings": list(self.warnings),
            "order": self.order.to_dict() if self.order is not None else None,
            "intent_build": self.intent_build.to_dict(),
            "read_only": self.read_only,
            "would_send_to_broker": self.would_send_to_broker,
        }


def default_paper_order_ledger_path(*, ensure: bool = True) -> Path:
    return decision_ledger_path("paper_orders", ensure=ensure)


def build_paper_order_ledger_record(
    *,
    intent_build: PaperOrderIntentBuildResult,
    order: PaperOrder | None,
    recorded_at: str,
    record_id: str | None = None,
) -> PaperOrderLedgerRecord:
    decision_id = "unknown"
    if order is not None:
        decision_id = order.intent.decision_id
    elif intent_build.intent is not None:
        decision_id = intent_build.intent.decision_id
    rid = record_id or f"paper_order_record_{decision_id}_{str(recorded_at).replace(':', '').replace('-', '').replace('.', '')}"

    blocked = list(intent_build.blocked_by)
    warnings = list(intent_build.warnings)
    accepted = bool(intent_build.ok and order is not None and order.status != PaperOrderStatus.REJECTED)
    if order is None:
        blocked.append("paper_order_missing")
    elif order.status == PaperOrderStatus.REJECTED:
        blocked.append("paper_order_rejected")
        if order.reject_reason:
            blocked.extend(str(part) for part in order.reject_reason.split(";") if part)

    return PaperOrderLedgerRecord(
        record_id=rid,
        recorded_at=recorded_at,
        accepted=accepted,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        order=order,
        intent_build=intent_build,
        read_only=True,
        would_send_to_broker=False,
    )


def append_paper_order_ledger_record(path: Path, record: PaperOrderLedgerRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, default=str) + "\n")


def record_paper_order(
    *,
    intent_build: PaperOrderIntentBuildResult,
    order: PaperOrder | None,
    recorded_at: str,
    path: Path | None = None,
) -> PaperOrderLedgerRecord:
    target = path or default_paper_order_ledger_path(ensure=True)
    record = build_paper_order_ledger_record(intent_build=intent_build, order=order, recorded_at=recorded_at)
    append_paper_order_ledger_record(target, record)
    return record


def _intent_from_dict(data: Dict[str, Any]):
    return build_order_intent_from_decision(
        decision_id=str(data.get("decision_id") or ""),
        snapshot_id=str(data.get("snapshot_id") or ""),
        forecast_id=data.get("forecast_id"),
        parameter_set_id=str(data.get("parameter_set_id") or ""),
        logic_version=str(data.get("logic_version") or ""),
        side=str(data.get("side") or "buy"),
        size=float(data.get("size") or 0.0),
        price=data.get("price"),
        reason_codes=tuple(data.get("reason_codes") or ()),
        risk_gate_allowed=bool(data.get("risk_gate_allowed")),
        mode=str(data.get("mode") or ""),
        order_type=OrderType(str(data.get("order_type") or "limit")),
        exchange=data.get("exchange"),
        product_code=data.get("product_code"),
        market_type=data.get("market_type"),
        market_uid=data.get("market_uid"),
        market_role=data.get("market_role"),
    )


def _order_from_dict(data: Dict[str, Any] | None) -> PaperOrder | None:
    if not isinstance(data, dict):
        return None
    intent_data = data.get("intent") if isinstance(data.get("intent"), dict) else {}
    intent = _intent_from_dict(dict(intent_data))
    return PaperOrder(
        order_id=str(data.get("order_id") or ""),
        intent=intent,
        status=PaperOrderStatus(str(data.get("status") or "new")),
        created_at=str(data.get("created_at") or ""),
        updated_at=str(data.get("updated_at") or ""),
        filled_size=float(data.get("filled_size") or 0.0),
        fill_price=data.get("fill_price"),
        cancel_reason=data.get("cancel_reason"),
        reject_reason=data.get("reject_reason"),
    )


def read_paper_order_ledger(path: Path | None = None) -> Tuple[dict[str, Any], ...]:
    target = path or default_paper_order_ledger_path(ensure=False)
    if not target.exists():
        return ()
    rows: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return tuple(rows)


def read_paper_orders(path: Path | None = None) -> Tuple[PaperOrder, ...]:
    orders: list[PaperOrder] = []
    for row in read_paper_order_ledger(path):
        order = _order_from_dict(row.get("order") if isinstance(row, dict) else None)
        if order is not None:
            orders.append(order)
    return tuple(orders)
