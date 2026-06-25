# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_preferred_row_adapter.py
# desc: PS-Q20E read-only WarRoom / producer preferred-row adapter. Builds compact consumer packets from PS-Q20B row selection and PS-Q20D lane policy without reading/writing runtime artifacts.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Tuple

from btcts.market_engine.market_state.consumer_integration_design import (
    LANE_PREDICTION_PRODUCER_INPUT,
    LANE_WARROOM_READ,
    build_market_overview_consumer_integration_design,
)
from btcts.market_engine.market_state.consumer_row_selection import (
    CONSUMER_PREFERRED,
    FAIL_CLOSED,
    MarketOverviewConsumerRowSelection,
    select_market_overview_consumer_preferred_row,
)

PREFERRED_ROW_ADAPTER_VERSION = "prediction_warroom.preferred_row_adapter.ps_q20e.v1"
SUPPORTED_READ_ONLY_LANES = (LANE_WARROOM_READ, LANE_PREDICTION_PRODUCER_INPUT)


@dataclass(frozen=True)
class PredictionWarRoomPreferredRowAdapterPacket:
    adapter_version: str
    adapter_state: str
    requested_lane: str
    selected_row: Mapping[str, Any] | None
    selected_row_index: int | None
    selection_state: str
    consumer_preferred_count: int
    diagnostic_transition_count: int
    diagnostic_rows_retained: bool
    allowed_for_requested_lane: bool
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    lane_policy: Mapping[str, Any]
    integration_design: Mapping[str, Any]
    read_only_adapter: bool = True
    non_executing: bool = True
    warroom_read_adapter: bool = True
    producer_input_adapter: bool = True
    existing_warroom_runtime_rewired: bool = False
    existing_producer_runtime_rewired: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    warroom_ui_trigger_enabled: bool = False
    runtime_artifact_write_allowed: bool = False
    prediction_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    view_artifact_write_allowed: bool = False
    ps_q19r_scoring_policy_changed: bool = False
    collector_runtime_behavior_changed: bool = False
    market_state_writer_changed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["selected_row"] = dict(self.selected_row) if self.selected_row is not None else None
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        data["lane_policy"] = dict(self.lane_policy)
        data["integration_design"] = dict(self.integration_design)
        return data


def _lane_policy(design: Mapping[str, Any], lane: str) -> Mapping[str, Any]:
    policies = design.get("lane_policies")
    if not isinstance(policies, list):
        return {}
    for item in policies:
        if isinstance(item, Mapping) and str(item.get("lane") or "") == lane:
            return item
    return {}


def _build_from_selection(selection: MarketOverviewConsumerRowSelection, *, lane: str) -> PredictionWarRoomPreferredRowAdapterPacket:
    lane_text = str(lane or "")
    selection_dict = selection.to_dict()
    design = build_market_overview_consumer_integration_design(selection).to_dict()
    policy = _lane_policy(design, lane_text)
    blocked: list[str] = []
    warnings: list[str] = []

    if lane_text not in SUPPORTED_READ_ONLY_LANES:
        blocked.append("preferred_row_adapter_lane_not_supported_for_ps_q20e")
    if selection.selection_state == FAIL_CLOSED:
        blocked.extend(str(item) for item in selection.blocked_reasons)
    if selection.selection_state != CONSUMER_PREFERRED:
        blocked.append("consumer_preferred_market_overview_row_missing")

    policy_blockers = policy.get("blockers") if isinstance(policy, Mapping) else []
    if isinstance(policy_blockers, list):
        blocked.extend(str(item) for item in policy_blockers)
    policy_warnings = policy.get("warnings") if isinstance(policy, Mapping) else []
    if isinstance(policy_warnings, list):
        warnings.extend(str(item) for item in policy_warnings)
    warnings.extend(str(item) for item in selection.warning_reasons)

    allowed = bool(
        not blocked
        and lane_text in SUPPORTED_READ_ONLY_LANES
        and policy.get("may_use_consumer_preferred_row") is True
        and selection.selected_row is not None
    )
    state = "preferred_row_adapter_ready" if allowed else "preferred_row_adapter_blocked"

    return PredictionWarRoomPreferredRowAdapterPacket(
        adapter_version=PREFERRED_ROW_ADAPTER_VERSION,
        adapter_state=state,
        requested_lane=lane_text,
        selected_row=selection.selected_row,
        selected_row_index=selection.selected_row_index,
        selection_state=str(selection.selection_state),
        consumer_preferred_count=int(selection.consumer_preferred_count),
        diagnostic_transition_count=int(selection.diagnostic_transition_count),
        diagnostic_rows_retained=bool(selection.diagnostic_transition_count > 0),
        allowed_for_requested_lane=allowed,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
        lane_policy=dict(policy),
        integration_design=design,
    )


def build_prediction_warroom_preferred_row_adapter(
    rows: Iterable[Mapping[str, Any]],
    *,
    lane: str = LANE_WARROOM_READ,
) -> PredictionWarRoomPreferredRowAdapterPacket:
    """Build a read-only adapter packet from raw market.overview rows.

    The function is intentionally pure mapping. It does not read files, write
    artifacts, mutate WarRoom, run a producer, schedule anything, or call broker APIs.
    """

    selection = select_market_overview_consumer_preferred_row(rows)
    return _build_from_selection(selection, lane=lane)


def build_prediction_warroom_preferred_row_adapter_from_selection(
    selection: MarketOverviewConsumerRowSelection,
    *,
    lane: str = LANE_WARROOM_READ,
) -> PredictionWarRoomPreferredRowAdapterPacket:
    """Build the same read-only adapter packet from a precomputed PS-Q20B selection."""

    return _build_from_selection(selection, lane=lane)
