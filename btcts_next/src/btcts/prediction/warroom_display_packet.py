# path: ./btcts_next/src/btcts/prediction/warroom_display_packet.py
# desc: WarRoom display packet contract for standalone Prediction System outputs. Read-only transform; no UI runtime, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .system_contract import PredictionSystemResult

PACKET_VERSION = "prediction_warroom_display_packet.ps_q4a.v1"


@dataclass(frozen=True)
class PredictionWarRoomDisplayPacket:
    packet_version: str
    packet_id: str
    generated_at: str
    market_uid: str
    prediction_run_id: str
    headline_ja: str = ""
    primary_signal_summary: Mapping[str, Any] = field(default_factory=dict)
    horizon_cards: Tuple[Mapping[str, Any], ...] = ()
    family_cards: Tuple[Mapping[str, Any], ...] = ()
    source_quality_panel: Mapping[str, Any] = field(default_factory=dict)
    evidence_panel: Mapping[str, Any] = field(default_factory=dict)
    warning_panel: Mapping[str, Any] = field(default_factory=dict)
    ui_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packet_version": self.packet_version,
            "packet_id": self.packet_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "prediction_run_id": self.prediction_run_id,
            "headline_ja": self.headline_ja,
            "primary_signal_summary": dict(self.primary_signal_summary),
            "horizon_cards": [dict(item) for item in self.horizon_cards],
            "family_cards": [dict(item) for item in self.family_cards],
            "source_quality_panel": dict(self.source_quality_panel),
            "evidence_panel": dict(self.evidence_panel),
            "warning_panel": dict(self.warning_panel),
            "ui_contract": dict(self.ui_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _headline(result_data: Mapping[str, Any], scenario: Mapping[str, Any]) -> str:
    narrative = str(result_data.get("human_narrative_ja") or "").strip()
    if narrative:
        return narrative.splitlines()[0]
    primary = _as_mapping(scenario.get("gpt_review_digest")).get("primary_story")
    if isinstance(primary, Mapping) and primary.get("headline_ja"):
        return str(primary.get("headline_ja"))
    return "Prediction System の表示用パケットです。"


def _horizon_card(outlook: Mapping[str, Any]) -> dict[str, Any]:
    digest = _as_mapping(outlook.get("gpt_review_digest"))
    signal = dict(_as_mapping(digest.get("signal_strength_summary")))
    scenario_lite = dict(_as_mapping(digest.get("scenario_lite")))
    lifetime = dict(_as_mapping(outlook.get("lifetime")))
    trigger = dict(_as_mapping(outlook.get("trigger_eligibility")))
    return {
        "card_version": "prediction_warroom_horizon_card.ps_q4a.v1",
        "horizon_group": outlook.get("horizon_group"),
        "display_label_ja": outlook.get("display_label_ja"),
        "horizons_sec": _list(outlook.get("horizons_sec")),
        "primary_label": outlook.get("primary_label"),
        "regime_state": outlook.get("regime_state"),
        "trend_bias": outlook.get("trend_bias"),
        "confidence": outlook.get("confidence"),
        "caution_level": outlook.get("caution_level"),
        "score": outlook.get("score"),
        "signal_strength_summary": signal,
        "estimated_signal_strength_percent": signal.get("estimated_signal_strength_percent"),
        "estimated_reference_hit_rate_percent": signal.get("estimated_reference_hit_rate_percent"),
        "signal_strength_band": signal.get("signal_strength_band"),
        "signal_strength_band_label_ja": signal.get("signal_strength_band_label_ja"),
        "scenario_lite": scenario_lite,
        "invalidation_state": outlook.get("invalidation_state"),
        "scenario_switch_hint": outlook.get("scenario_switch_hint"),
        "lifetime": lifetime,
        "refresh_required": lifetime.get("refresh_required"),
        "trigger_eligibility_state": trigger.get("trigger_eligibility_state"),
        "trigger_enabled": False,
        "human_narrative_ja": outlook.get("human_narrative_ja"),
        "blockers": _list(outlook.get("blockers")),
        "warnings": _list(outlook.get("warnings")),
        "read_only": True,
        "non_executing": True,
    }


def _family_card(output: Mapping[str, Any]) -> dict[str, Any]:
    values = dict(_as_mapping(output.get("values")))
    horizon = dict(_as_mapping(output.get("horizon")))
    ledger = _list(values.get("source_contribution_ledger"))
    return {
        "card_version": "prediction_warroom_family_card.ps_q4a.v1",
        "prediction_id": output.get("prediction_id"),
        "family": output.get("family"),
        "horizon_sec": horizon.get("horizon_sec"),
        "primary_label": output.get("primary_label"),
        "confidence": output.get("confidence"),
        "score": output.get("score"),
        "estimated_signal_strength_percent": values.get("estimated_signal_strength_percent"),
        "estimated_reference_hit_rate_percent": values.get("estimated_reference_hit_rate_percent"),
        "source_quality_gate_state": values.get("source_quality_gate_state"),
        "source_quality_gate_effect": values.get("source_quality_gate_effect"),
        "signal_strength_cap_reason": values.get("signal_strength_cap_reason") or values.get("context_profile_signal_strength_cap_reason"),
        "context_profile_source_caps": _list(values.get("context_profile_source_caps")),
        "source_contribution_ledger": ledger,
        "driver_count": len(_list(output.get("drivers"))),
        "drivers": _list(output.get("drivers")),
        "blockers": _list(output.get("blockers")),
        "warnings": _list(output.get("warnings")),
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
    }


def build_prediction_warroom_display_packet(result: PredictionSystemResult) -> PredictionWarRoomDisplayPacket:
    """Build a read-only WarRoom display packet from an already-built PredictionSystemResult."""
    data = result.to_dict()
    run_identity = _as_mapping(data.get("run_identity"))
    system_input = _as_mapping(data.get("system_input"))
    scenario = _as_mapping(data.get("scenario_core"))
    digest = _as_mapping(data.get("gpt_review_digest"))
    scenario_digest = _as_mapping(scenario.get("gpt_review_digest"))
    scenario_trace = _as_mapping(scenario.get("scenario_trace"))
    outlooks = [_as_mapping(item) for item in _list(scenario.get("outlooks"))]
    outputs = [_as_mapping(item) for item in _list(data.get("outputs"))]
    source_artifact_coverage = _as_mapping(system_input.get("source_artifact_coverage_summary"))
    provider_quality = _as_mapping(system_input.get("provider_quality_summary"))
    tier0_gate = _as_mapping(provider_quality.get("tier0_source_quality_gate"))
    primary_signal = dict(_as_mapping(digest.get("signal_strength_summary")))
    packet_id = f"{PACKET_VERSION}:{run_identity.get('prediction_run_id', 'unknown')}"
    boundaries = {
        "read_only": True,
        "non_executing": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "trigger_enabled": False,
        "autotrade_trigger_enabled": False,
    }
    ui_contract = {
        "contract_version": "prediction_warroom_ui_contract.ps_q4a.v1",
        "intended_consumer": "WarRoom",
        "packet_kind": "prediction_system_display_packet",
        "display_only": True,
        "render_intent_only": True,
        "safe_to_render_without_side_effects": True,
        "requires_runtime_artifact_write": False,
        "requires_collector_runtime": False,
        "requires_autotrade_runtime": False,
        "trigger_buttons_allowed": False,
        "mode_controls_allowed": False,
        "broker_controls_allowed": False,
        "not_loaded_as_runtime_display_source": True,
    }
    return PredictionWarRoomDisplayPacket(
        packet_version=PACKET_VERSION,
        packet_id=packet_id,
        generated_at=str(run_identity.get("generated_at") or data.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or system_input.get("market_uid") or "BTC_JPY:bitFlyer"),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        headline_ja=_headline(data, scenario),
        primary_signal_summary=primary_signal,
        horizon_cards=tuple(_horizon_card(outlook) for outlook in outlooks),
        family_cards=tuple(_family_card(output) for output in outputs),
        source_quality_panel={
            "panel_version": "prediction_warroom_source_quality_panel.ps_q4a.v1",
            "tier0_source_quality_gate": dict(tier0_gate),
            "source_artifact_coverage": dict(source_artifact_coverage),
            "source_artifact_input_coverage_state": digest.get("source_artifact_input_coverage_state"),
            "source_artifact_input_coverage_ratio": digest.get("source_artifact_input_coverage_ratio"),
            "selected_context_evidence_profile_ids": _list(digest.get("selected_context_evidence_profile_ids")),
            "context_profile_signal_strength_cap_reasons": _list(digest.get("context_profile_signal_strength_cap_reasons")),
            "read_only": True,
            "non_executing": True,
        },
        evidence_panel={
            "panel_version": "prediction_warroom_evidence_panel.ps_q4a.v1",
            "scenario_trace": dict(scenario_trace),
            "scenario_digest": dict(scenario_digest),
            "source_contribution_ledger_count": sum(len(_list(card.get("source_contribution_ledger"))) for card in tuple(_family_card(output) for output in outputs)),
            "family_card_count": len(outputs),
            "horizon_card_count": len(outlooks),
            "read_only": True,
            "non_executing": True,
        },
        warning_panel={
            "panel_version": "prediction_warroom_warning_panel.ps_q4a.v1",
            "blockers": _list(data.get("blockers")),
            "warnings": _list(data.get("warnings")),
            "scenario_blockers": _list(scenario.get("blockers")),
            "scenario_warnings": _list(scenario.get("warnings")),
            "signal_strength_cap_reasons": _list(primary_signal.get("signal_strength_cap_reasons")),
            "prediction_unavailable_reasons": _list(primary_signal.get("prediction_unavailable_reasons")),
            "read_only": True,
            "non_executing": True,
        },
        ui_contract=ui_contract,
        boundaries=boundaries,
    )
