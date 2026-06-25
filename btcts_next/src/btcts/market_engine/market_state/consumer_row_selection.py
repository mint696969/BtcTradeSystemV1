# path: ./btcts_next/src/btcts/market_engine/market_state/consumer_row_selection.py
# desc: Read-only market.overview consumer-row selection contracts. Separates consumer-preferred rows from diagnostic transition rows without changing collector output or scoring policy.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Tuple

LOGIC_VERSION = "market_state.consumer_row_selection.ps_q20b.v1"

CONSUMER_PREFERRED = "consumer_preferred"
DIAGNOSTIC_TRANSITION = "diagnostic_transition"
FAIL_CLOSED = "fail_closed"

QUALITY_REASONS = (
    "market_overview_not_trusted",
    "market_overview_not_allow_structural_use",
    "market_overview_semantic_observer_broken",
    "market_overview_negative_spread",
    "market_overview_crossed_book",
    "market_overview_missing_top_book",
)


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _quality_reasons(row: Mapping[str, Any]) -> tuple[str, ...]:
    reasons: list[str] = []
    trust_state = str(row.get("trust_state") or "")
    bucket = str(row.get("interpretation_bucket") or "")
    semantic_status = str(row.get("semantic_observer_status") or "")
    best_bid = _safe_float(row.get("best_bid"))
    best_ask = _safe_float(row.get("best_ask"))
    spread = _safe_float(row.get("spread"))

    if trust_state != "trusted":
        reasons.append("market_overview_not_trusted")
    if bucket != "allow_structural_use":
        reasons.append("market_overview_not_allow_structural_use")
    if semantic_status == "broken":
        reasons.append("market_overview_semantic_observer_broken")
    if best_bid is None or best_ask is None:
        reasons.append("market_overview_missing_top_book")
    if spread is not None and spread < 0:
        reasons.append("market_overview_negative_spread")
    if best_bid is not None and best_ask is not None and best_bid > best_ask:
        reasons.append("market_overview_crossed_book")
    return tuple(dict.fromkeys(reasons))


def _quality_rank(row: Mapping[str, Any], reasons: tuple[str, ...]) -> int:
    if not reasons:
        return 0
    rank = 100
    if "market_overview_negative_spread" in reasons or "market_overview_crossed_book" in reasons:
        rank += 100
    if "market_overview_semantic_observer_broken" in reasons:
        rank += 50
    if "market_overview_not_trusted" in reasons:
        rank += 20
    if "market_overview_not_allow_structural_use" in reasons:
        rank += 10
    if "market_overview_missing_top_book" in reasons:
        rank += 200
    return rank


def _compact_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "collector_ts": str(row.get("collector_ts") or ""),
        "exchange_ts": row.get("exchange_ts"),
        "trust_state": str(row.get("trust_state") or ""),
        "boundary_reason": str(row.get("boundary_reason") or ""),
        "continuity_state": str(row.get("continuity_state") or ""),
        "interpretation_bucket": str(row.get("interpretation_bucket") or ""),
        "interpretation_reason": str(row.get("interpretation_reason") or ""),
        "semantic_observer_status": str(row.get("semantic_observer_status") or ""),
        "best_bid": row.get("best_bid"),
        "best_ask": row.get("best_ask"),
        "spread": row.get("spread"),
        "mid_price": row.get("mid_price"),
        "source_series_id": str(row.get("source_series_id") or ""),
        "source_stream_session_id": str(row.get("source_stream_session_id") or ""),
    }


@dataclass(frozen=True)
class MarketOverviewRowRole:
    row_index: int
    row_role: str
    quality_rank: int
    quality_ok: bool
    quality_reasons: Tuple[str, ...]
    usable_for_prediction: bool
    usable_for_strategy_candidate: bool
    usable_for_execution_candidate: bool
    diagnostic_visible: bool
    row: Mapping[str, Any]
    logic_version: str = LOGIC_VERSION
    read_only: bool = True
    non_executing: bool = True
    would_change_collector_runtime: bool = False
    would_change_scoring_policy: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["quality_reasons"] = list(self.quality_reasons)
        data["row"] = dict(self.row)
        return data


@dataclass(frozen=True)
class MarketOverviewConsumerRowSelection:
    selection_state: str
    selected_row_index: int | None
    selected_row: Mapping[str, Any] | None
    row_roles: Tuple[MarketOverviewRowRole, ...]
    input_row_count: int
    consumer_preferred_count: int
    diagnostic_transition_count: int
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    logic_version: str = LOGIC_VERSION
    read_only: bool = True
    non_executing: bool = True
    collector_runtime_behavior_changed: bool = False
    ps_q19r_scoring_policy_changed: bool = False
    row_selection_contract_only: bool = True
    preferred_row_available_for_future_consumers: bool = False
    diagnostic_rows_retained: bool = True
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection_state": self.selection_state,
            "selected_row_index": self.selected_row_index,
            "selected_row": dict(self.selected_row) if self.selected_row is not None else None,
            "row_roles": [role.to_dict() for role in self.row_roles],
            "input_row_count": self.input_row_count,
            "consumer_preferred_count": self.consumer_preferred_count,
            "diagnostic_transition_count": self.diagnostic_transition_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "logic_version": self.logic_version,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "collector_runtime_behavior_changed": self.collector_runtime_behavior_changed,
            "ps_q19r_scoring_policy_changed": self.ps_q19r_scoring_policy_changed,
            "row_selection_contract_only": self.row_selection_contract_only,
            "preferred_row_available_for_future_consumers": self.preferred_row_available_for_future_consumers,
            "diagnostic_rows_retained": self.diagnostic_rows_retained,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
        }


def classify_market_overview_consumer_row(row: Mapping[str, Any], *, row_index: int) -> MarketOverviewRowRole:
    reasons = _quality_reasons(row)
    quality_ok = not reasons
    role = CONSUMER_PREFERRED if quality_ok else DIAGNOSTIC_TRANSITION
    return MarketOverviewRowRole(
        row_index=int(row_index),
        row_role=role,
        quality_rank=_quality_rank(row, reasons),
        quality_ok=quality_ok,
        quality_reasons=reasons,
        usable_for_prediction=quality_ok,
        usable_for_strategy_candidate=quality_ok,
        usable_for_execution_candidate=False,
        diagnostic_visible=True,
        row=_compact_row(row),
    )


def select_market_overview_consumer_preferred_row(rows: Iterable[Mapping[str, Any]]) -> MarketOverviewConsumerRowSelection:
    roles = tuple(
        classify_market_overview_consumer_row(row, row_index=index)
        for index, row in enumerate(rows)
    )
    if not roles:
        return MarketOverviewConsumerRowSelection(
            selection_state=FAIL_CLOSED,
            selected_row_index=None,
            selected_row=None,
            row_roles=(),
            input_row_count=0,
            consumer_preferred_count=0,
            diagnostic_transition_count=0,
            blocked_reasons=("market_overview_rows_missing",),
            warning_reasons=(),
            preferred_row_available_for_future_consumers=False,
        )

    preferred = [role for role in roles if role.row_role == CONSUMER_PREFERRED]
    diagnostics = [role for role in roles if role.row_role == DIAGNOSTIC_TRANSITION]
    if not preferred:
        return MarketOverviewConsumerRowSelection(
            selection_state=FAIL_CLOSED,
            selected_row_index=None,
            selected_row=None,
            row_roles=roles,
            input_row_count=len(roles),
            consumer_preferred_count=0,
            diagnostic_transition_count=len(diagnostics),
            blocked_reasons=("consumer_preferred_market_overview_row_missing",),
            warning_reasons=("diagnostic_transition_rows_present",) if diagnostics else (),
            preferred_row_available_for_future_consumers=False,
        )

    selected = sorted(preferred, key=lambda role: (role.quality_rank, role.row_index))[0]
    warnings: list[str] = []
    if diagnostics:
        warnings.append("diagnostic_transition_rows_retained")
    if len(preferred) > 1:
        warnings.append("multiple_consumer_preferred_rows_available")

    return MarketOverviewConsumerRowSelection(
        selection_state=CONSUMER_PREFERRED,
        selected_row_index=selected.row_index,
        selected_row=selected.row,
        row_roles=roles,
        input_row_count=len(roles),
        consumer_preferred_count=len(preferred),
        diagnostic_transition_count=len(diagnostics),
        blocked_reasons=(),
        warning_reasons=tuple(warnings),
        preferred_row_available_for_future_consumers=True,
    )
