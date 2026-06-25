# path: ./btcts_next/src/btcts/market_engine/market_state/consumer_integration_design.py
# desc: PS-Q20D read-only integration design for using market.overview consumer-preferred rows across future WarRoom, producer, replay, and strategy lanes without enabling runtime behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.market_engine.market_state.consumer_row_selection import (
    CONSUMER_PREFERRED,
    DIAGNOSTIC_TRANSITION,
    FAIL_CLOSED,
    MarketOverviewConsumerRowSelection,
)

LOGIC_VERSION = "market_state.consumer_integration_design.ps_q20d.v1"

LANE_WARROOM_READ = "warroom_read"
LANE_PREDICTION_PRODUCER_INPUT = "prediction_producer_input"
LANE_REPLAY_ANALYSIS = "replay_analysis"
LANE_STRATEGY_CANDIDATE = "strategy_candidate"
LANE_EXECUTION_CANDIDATE = "execution_candidate"
LANE_AUTOTRADE_TRIGGER = "autotrade_trigger"

SAFE_READ_LANES = (
    LANE_WARROOM_READ,
    LANE_PREDICTION_PRODUCER_INPUT,
    LANE_REPLAY_ANALYSIS,
    LANE_STRATEGY_CANDIDATE,
)
BLOCKED_EXECUTION_LANES = (
    LANE_EXECUTION_CANDIDATE,
    LANE_AUTOTRADE_TRIGGER,
)


@dataclass(frozen=True)
class MarketOverviewConsumerLanePolicy:
    lane: str
    may_use_consumer_preferred_row: bool
    may_display_diagnostic_rows: bool
    may_score_diagnostic_rows: bool
    may_trigger_execution: bool
    requires_human_policy_gate: bool
    status: str
    blockers: Tuple[str, ...]
    warnings: Tuple[str, ...]
    logic_version: str = LOGIC_VERSION
    read_only: bool = True
    non_executing: bool = True
    collector_runtime_behavior_changed: bool = False
    ps_q19r_scoring_policy_changed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        return data


@dataclass(frozen=True)
class MarketOverviewConsumerIntegrationDesign:
    selection_state: str
    preferred_row_available: bool
    diagnostic_rows_present: bool
    fail_closed: bool
    lane_policies: Tuple[MarketOverviewConsumerLanePolicy, ...]
    recommended_next_slice: str
    integration_design_only: bool = True
    logic_version: str = LOGIC_VERSION
    read_only: bool = True
    non_executing: bool = True
    collector_runtime_behavior_changed: bool = False
    market_state_writer_changed: bool = False
    warroom_runtime_behavior_changed: bool = False
    prediction_producer_behavior_changed: bool = False
    ps_q19r_scoring_policy_changed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection_state": self.selection_state,
            "preferred_row_available": self.preferred_row_available,
            "diagnostic_rows_present": self.diagnostic_rows_present,
            "fail_closed": self.fail_closed,
            "lane_policies": [policy.to_dict() for policy in self.lane_policies],
            "recommended_next_slice": self.recommended_next_slice,
            "integration_design_only": self.integration_design_only,
            "logic_version": self.logic_version,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "collector_runtime_behavior_changed": self.collector_runtime_behavior_changed,
            "market_state_writer_changed": self.market_state_writer_changed,
            "warroom_runtime_behavior_changed": self.warroom_runtime_behavior_changed,
            "prediction_producer_behavior_changed": self.prediction_producer_behavior_changed,
            "ps_q19r_scoring_policy_changed": self.ps_q19r_scoring_policy_changed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "would_send_to_broker": self.would_send_to_broker,
        }


def _safe_read_lane_policy(*, lane: str, preferred_available: bool, diagnostic_present: bool, fail_closed: bool) -> MarketOverviewConsumerLanePolicy:
    blockers: list[str] = []
    warnings: list[str] = []
    if fail_closed:
        blockers.append("consumer_preferred_market_overview_row_missing")
    if diagnostic_present:
        warnings.append("diagnostic_transition_rows_retained")
    return MarketOverviewConsumerLanePolicy(
        lane=lane,
        may_use_consumer_preferred_row=bool(preferred_available and not fail_closed),
        may_display_diagnostic_rows=True,
        may_score_diagnostic_rows=False,
        may_trigger_execution=False,
        requires_human_policy_gate=False,
        status="blocked" if blockers else "allowed_read_only",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _blocked_execution_lane_policy(*, lane: str, preferred_available: bool, diagnostic_present: bool, fail_closed: bool) -> MarketOverviewConsumerLanePolicy:
    blockers = [
        "ps_q20d_does_not_enable_execution_candidate_lane",
        "human_policy_gate_required_before_execution_use",
    ]
    if fail_closed:
        blockers.append("consumer_preferred_market_overview_row_missing")
    warnings: list[str] = []
    if preferred_available:
        warnings.append("consumer_preferred_row_exists_but_execution_lane_still_blocked")
    if diagnostic_present:
        warnings.append("diagnostic_transition_rows_retained")
    return MarketOverviewConsumerLanePolicy(
        lane=lane,
        may_use_consumer_preferred_row=False,
        may_display_diagnostic_rows=True,
        may_score_diagnostic_rows=False,
        may_trigger_execution=False,
        requires_human_policy_gate=True,
        status="blocked_by_policy",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def build_market_overview_consumer_integration_design(selection: MarketOverviewConsumerRowSelection | Mapping[str, Any]) -> MarketOverviewConsumerIntegrationDesign:
    """Build a read-only consumer integration design from a PS-Q20B selection packet.

    This is intentionally a planning/contract helper. It must not call UI, producer,
    AutoTrade, broker, writer, or collector runtime code.
    """

    if isinstance(selection, MarketOverviewConsumerRowSelection):
        selection_dict = selection.to_dict()
    else:
        selection_dict = dict(selection)

    selection_state = str(selection_dict.get("selection_state") or "")
    preferred_count = int(selection_dict.get("consumer_preferred_count") or 0)
    diagnostic_count = int(selection_dict.get("diagnostic_transition_count") or 0)
    preferred_available = bool(preferred_count > 0 and selection_state == CONSUMER_PREFERRED)
    diagnostic_present = bool(diagnostic_count > 0)
    fail_closed = bool(selection_state == FAIL_CLOSED or not preferred_available)

    lane_policies: list[MarketOverviewConsumerLanePolicy] = []
    for lane in SAFE_READ_LANES:
        lane_policies.append(
            _safe_read_lane_policy(
                lane=lane,
                preferred_available=preferred_available,
                diagnostic_present=diagnostic_present,
                fail_closed=fail_closed,
            )
        )
    for lane in BLOCKED_EXECUTION_LANES:
        lane_policies.append(
            _blocked_execution_lane_policy(
                lane=lane,
                preferred_available=preferred_available,
                diagnostic_present=diagnostic_present,
                fail_closed=fail_closed,
            )
        )

    if preferred_available:
        next_slice = "PS-Q20E_WARROOM_AND_PRODUCER_READ_ONLY_PREFERRED_ROW_ADAPTER"
    else:
        next_slice = "continue_collector_reanchor_observation"

    return MarketOverviewConsumerIntegrationDesign(
        selection_state=selection_state,
        preferred_row_available=preferred_available,
        diagnostic_rows_present=diagnostic_present,
        fail_closed=fail_closed,
        lane_policies=tuple(lane_policies),
        recommended_next_slice=next_slice,
    )
