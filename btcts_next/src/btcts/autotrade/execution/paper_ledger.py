# path: ./btcts_next/src/btcts/autotrade/execution/paper_ledger.py
# desc: SR-FX paper order ledger persistence under AutoTrade hot runtime. No broker calls.

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.intents import OrderSide, OrderType, build_order_intent_from_decision
from btcts.autotrade.execution.order_state import PaperOrder, PaperOrderStatus, TERMINAL_PAPER_ORDER_STATUSES
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


@dataclass(frozen=True)
class PaperOrderLedgerReadResult:
    path: Path
    rows: Tuple[dict[str, Any], ...]
    skipped_count: int = 0
    error_samples: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "rows": list(self.rows),
            "skipped_count": self.skipped_count,
            "error_samples": list(self.error_samples),
            "read_only": True,
            "would_send_to_broker": False,
        }


@dataclass(frozen=True)
class PaperOrderLedgerSummary:
    path: Path
    exists: bool
    total_rows: int
    accepted_count: int
    rejected_count: int
    active_paper_order_count: int
    terminal_paper_order_count: int
    skipped_rows: int
    latest_record_id: str | None = None
    latest_recorded_at: str | None = None
    latest_order_id: str | None = None
    latest_decision_id: str | None = None
    latest_status: str | None = None
    latest_product_code: str | None = None
    latest_market_uid: str | None = None
    latest_accepted: bool | None = None
    latest_blocked_by: Tuple[str, ...] = ()
    latest_warnings: Tuple[str, ...] = ()
    status_counts: Dict[str, int] | None = None
    blocked_by_counts: Dict[str, int] | None = None
    warning_counts: Dict[str, int] | None = None
    error_samples: Tuple[str, ...] = ()
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        data["status_counts"] = dict(self.status_counts or {})
        data["blocked_by_counts"] = dict(self.blocked_by_counts or {})
        data["warning_counts"] = dict(self.warning_counts or {})
        return data


def _iter_recent_lines(path: Path, *, max_lines: int | None = None) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    if max_lines is not None and max_lines >= 0:
        return lines[-max_lines:]
    return lines


def read_paper_order_ledger_rows(path: Path | None = None, *, max_lines: int | None = 1000) -> PaperOrderLedgerReadResult:
    target = path or default_paper_order_ledger_path(ensure=False)
    rows: list[dict[str, Any]] = []
    skipped = 0
    errors: list[str] = []
    for index, line in enumerate(_iter_recent_lines(target, max_lines=max_lines), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if not isinstance(obj, dict):
                raise ValueError("not_object")
            rows.append(obj)
        except Exception as exc:
            skipped += 1
            if len(errors) < 5:
                errors.append(f"line:{index}:{exc.__class__.__name__}")
    return PaperOrderLedgerReadResult(path=target, rows=tuple(rows), skipped_count=skipped, error_samples=tuple(errors))


def _tuple_str(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if str(item))


def _status_of(row: dict[str, Any]) -> str | None:
    order = row.get("order") if isinstance(row.get("order"), dict) else None
    if not isinstance(order, dict):
        return None
    status = order.get("status")
    return str(status) if status is not None else None


def _order_intent_of(row: dict[str, Any]) -> dict[str, Any]:
    order = row.get("order") if isinstance(row.get("order"), dict) else None
    if not isinstance(order, dict):
        return {}
    intent = order.get("intent")
    return dict(intent) if isinstance(intent, dict) else {}


def summarize_paper_order_ledger(path: Path | None = None, *, max_lines: int | None = 1000) -> PaperOrderLedgerSummary:
    target = path or default_paper_order_ledger_path(ensure=False)
    read = read_paper_order_ledger_rows(target, max_lines=max_lines)
    rows = read.rows
    latest = rows[-1] if rows else None
    status_counter: Counter[str] = Counter()
    blocked_counter: Counter[str] = Counter()
    warning_counter: Counter[str] = Counter()
    active_count = 0
    terminal_count = 0
    accepted_count = 0

    terminal_values = {status.value for status in TERMINAL_PAPER_ORDER_STATUSES}
    for row in rows:
        if bool(row.get("accepted")):
            accepted_count += 1
        status = _status_of(row)
        if status:
            status_counter[status] += 1
            if status in terminal_values:
                terminal_count += 1
            else:
                active_count += 1
        blocked_counter.update(_tuple_str(row.get("blocked_by")))
        warning_counter.update(_tuple_str(row.get("warnings")))

    latest_order = latest.get("order") if isinstance(latest, dict) and isinstance(latest.get("order"), dict) else {}
    latest_intent = _order_intent_of(latest) if isinstance(latest, dict) else {}

    return PaperOrderLedgerSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(rows),
        accepted_count=accepted_count,
        rejected_count=len(rows) - accepted_count,
        active_paper_order_count=active_count,
        terminal_paper_order_count=terminal_count,
        skipped_rows=read.skipped_count,
        latest_record_id=str(latest.get("record_id")) if isinstance(latest, dict) and latest.get("record_id") is not None else None,
        latest_recorded_at=str(latest.get("recorded_at")) if isinstance(latest, dict) and latest.get("recorded_at") is not None else None,
        latest_order_id=str(latest_order.get("order_id")) if latest_order.get("order_id") is not None else None,
        latest_decision_id=str(latest_intent.get("decision_id")) if latest_intent.get("decision_id") is not None else None,
        latest_status=_status_of(latest) if isinstance(latest, dict) else None,
        latest_product_code=str(latest_intent.get("product_code")) if latest_intent.get("product_code") is not None else None,
        latest_market_uid=str(latest_intent.get("market_uid")) if latest_intent.get("market_uid") is not None else None,
        latest_accepted=bool(latest.get("accepted")) if isinstance(latest, dict) else None,
        latest_blocked_by=_tuple_str(latest.get("blocked_by")) if isinstance(latest, dict) else (),
        latest_warnings=_tuple_str(latest.get("warnings")) if isinstance(latest, dict) else (),
        status_counts=dict(status_counter),
        blocked_by_counts=dict(blocked_counter),
        warning_counts=dict(warning_counter),
        error_samples=read.error_samples,
        read_only=True,
        would_send_to_broker=False,
    )



@dataclass(frozen=True)
class PaperOrderTransitionRecord:
    record_id: str
    recorded_at: str
    order_id: str
    decision_id: str
    previous_status: str | None
    new_status: str
    transition_event: str
    order: PaperOrder
    fill_size: float | None = None
    fill_price: float | None = None
    reason: str | None = None
    ledger_event: str = "autotrade.paper_order_transition_recorded"
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_event": self.ledger_event,
            "record_id": self.record_id,
            "recorded_at": self.recorded_at,
            "order_id": self.order_id,
            "decision_id": self.decision_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "transition_event": self.transition_event,
            "transition": {
                "event": self.transition_event,
                "previous_status": self.previous_status,
                "new_status": self.new_status,
                "fill_size": self.fill_size,
                "fill_price": self.fill_price,
                "reason": self.reason,
            },
            "accepted": self.new_status != PaperOrderStatus.REJECTED.value,
            "blocked_by": [self.reason] if self.new_status == PaperOrderStatus.REJECTED.value and self.reason else [],
            "warnings": [],
            "order": self.order.to_dict(),
            "read_only": self.read_only,
            "would_send_to_broker": self.would_send_to_broker,
        }


@dataclass(frozen=True)
class PaperOrderLifecycleSummary:
    path: Path
    exists: bool
    total_rows: int
    order_count: int
    active_paper_order_count: int
    terminal_paper_order_count: int
    rejected_order_count: int
    skipped_rows: int
    latest_record_id: str | None = None
    latest_recorded_at: str | None = None
    latest_order_id: str | None = None
    latest_decision_id: str | None = None
    latest_status: str | None = None
    latest_transition_event: str | None = None
    latest_product_code: str | None = None
    latest_market_uid: str | None = None
    status_counts: Dict[str, int] | None = None
    transition_event_counts: Dict[str, int] | None = None
    error_samples: Tuple[str, ...] = ()
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        data["status_counts"] = dict(self.status_counts or {})
        data["transition_event_counts"] = dict(self.transition_event_counts or {})
        return data


def _safe_id_fragment(value: str) -> str:
    return str(value or "unknown").replace(":", "").replace("-", "").replace(".", "").replace(" ", "_")


def _transition_event(previous_status: str | None, new_status: str) -> str:
    prev = previous_status or "none"
    return f"{prev}_to_{new_status}"


def build_paper_order_transition_record(
    *,
    order: PaperOrder,
    recorded_at: str,
    previous_order: PaperOrder | None = None,
    transition_event: str | None = None,
    fill_size: float | None = None,
    fill_price: float | None = None,
    reason: str | None = None,
    record_id: str | None = None,
) -> PaperOrderTransitionRecord:
    previous_status = previous_order.status.value if previous_order is not None else None
    new_status = order.status.value
    event = transition_event or _transition_event(previous_status, new_status)
    rid = record_id or f"paper_order_transition_{order.order_id}_{event}_{_safe_id_fragment(recorded_at)}"
    return PaperOrderTransitionRecord(
        record_id=rid,
        recorded_at=recorded_at,
        order_id=order.order_id,
        decision_id=order.intent.decision_id,
        previous_status=previous_status,
        new_status=new_status,
        transition_event=event,
        order=order,
        fill_size=fill_size,
        fill_price=fill_price,
        reason=reason,
        read_only=True,
        would_send_to_broker=False,
    )


def append_paper_order_transition_record(path: Path, record: PaperOrderTransitionRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, default=str) + "\n")


def record_paper_order_transition(
    *,
    order: PaperOrder,
    recorded_at: str,
    previous_order: PaperOrder | None = None,
    transition_event: str | None = None,
    fill_size: float | None = None,
    fill_price: float | None = None,
    reason: str | None = None,
    path: Path | None = None,
) -> PaperOrderTransitionRecord:
    target = path or default_paper_order_ledger_path(ensure=True)
    record = build_paper_order_transition_record(
        order=order,
        recorded_at=recorded_at,
        previous_order=previous_order,
        transition_event=transition_event,
        fill_size=fill_size,
        fill_price=fill_price,
        reason=reason,
    )
    append_paper_order_transition_record(target, record)
    return record


def _transition_event_of(row: dict[str, Any]) -> str | None:
    transition = row.get("transition") if isinstance(row.get("transition"), dict) else None
    if isinstance(transition, dict) and transition.get("event") is not None:
        return str(transition.get("event"))
    if row.get("transition_event") is not None:
        return str(row.get("transition_event"))
    return None


def summarize_paper_order_lifecycle(path: Path | None = None, *, max_lines: int | None = 1000) -> PaperOrderLifecycleSummary:
    target = path or default_paper_order_ledger_path(ensure=False)
    read = read_paper_order_ledger_rows(target, max_lines=max_lines)
    rows = read.rows
    latest_by_order: dict[str, dict[str, Any]] = {}
    transition_counter: Counter[str] = Counter()
    terminal_values = {status.value for status in TERMINAL_PAPER_ORDER_STATUSES}

    for row in rows:
        event = _transition_event_of(row)
        if event:
            transition_counter[event] += 1
        order = row.get("order") if isinstance(row.get("order"), dict) else None
        if not isinstance(order, dict):
            continue
        order_id = order.get("order_id")
        if order_id is None:
            continue
        latest_by_order[str(order_id)] = row

    status_counter: Counter[str] = Counter()
    active_count = 0
    terminal_count = 0
    rejected_count = 0
    for row in latest_by_order.values():
        status = _status_of(row)
        if not status:
            continue
        status_counter[status] += 1
        if status == PaperOrderStatus.REJECTED.value:
            rejected_count += 1
        if status in terminal_values:
            terminal_count += 1
        else:
            active_count += 1

    latest = rows[-1] if rows else None
    latest_order = latest.get("order") if isinstance(latest, dict) and isinstance(latest.get("order"), dict) else {}
    latest_intent = _order_intent_of(latest) if isinstance(latest, dict) else {}

    return PaperOrderLifecycleSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(rows),
        order_count=len(latest_by_order),
        active_paper_order_count=active_count,
        terminal_paper_order_count=terminal_count,
        rejected_order_count=rejected_count,
        skipped_rows=read.skipped_count,
        latest_record_id=str(latest.get("record_id")) if isinstance(latest, dict) and latest.get("record_id") is not None else None,
        latest_recorded_at=str(latest.get("recorded_at")) if isinstance(latest, dict) and latest.get("recorded_at") is not None else None,
        latest_order_id=str(latest_order.get("order_id")) if latest_order.get("order_id") is not None else None,
        latest_decision_id=str(latest_intent.get("decision_id")) if latest_intent.get("decision_id") is not None else None,
        latest_status=_status_of(latest) if isinstance(latest, dict) else None,
        latest_transition_event=_transition_event_of(latest) if isinstance(latest, dict) else None,
        latest_product_code=str(latest_intent.get("product_code")) if latest_intent.get("product_code") is not None else None,
        latest_market_uid=str(latest_intent.get("market_uid")) if latest_intent.get("market_uid") is not None else None,
        status_counts=dict(status_counter),
        transition_event_counts=dict(transition_counter),
        error_samples=read.error_samples,
        read_only=True,
        would_send_to_broker=False,
    )
