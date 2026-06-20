# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_sample_packets.py
# desc: Synthetic sample packets for Prediction WarRoom display/widget/L4 adapter validation. Fixture contract only; no runtime reads, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

from .prediction_warroom_l4_latest_adapter import build_prediction_warroom_l4_latest_adapter_contract
from .prediction_warroom_widget_groups import build_prediction_warroom_widget_group_packet_index

SAMPLE_PACKET_VERSION = "prediction_warroom_sample_packets.ps_q4d.v1"
SAMPLE_PREDICTION_RUN_ID = "synthetic_prediction_run_20260620T000000Z"


@dataclass(frozen=True)
class PredictionWarRoomSamplePacketBundle:
    sample_version: str
    sample_id: str
    display_packet: Mapping[str, Any] = field(default_factory=dict)
    widget_group_index: Mapping[str, Any] = field(default_factory=dict)
    l4_latest_adapter_contract: Mapping[str, Any] = field(default_factory=dict)
    fixture_metadata: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    synthetic_only: bool = True
    fixture_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_version": self.sample_version,
            "sample_id": self.sample_id,
            "display_packet": dict(self.display_packet),
            "widget_group_index": dict(self.widget_group_index),
            "l4_latest_adapter_contract": dict(self.l4_latest_adapter_contract),
            "fixture_metadata": dict(self.fixture_metadata),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "synthetic_only": self.synthetic_only,
            "fixture_only": self.fixture_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _common_boundaries() -> dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
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


def build_prediction_warroom_sample_display_packet() -> dict[str, Any]:
    """Return a deterministic synthetic display packet for WarRoom widget/adapter validation."""
    boundaries = _common_boundaries()
    primary_signal_summary = {
        "summary_version": "prediction_signal_strength_bands.ps_q3c.v1",
        "estimated_signal_strength_percent": 59,
        "estimated_reference_hit_rate_percent": 59,
        "signal_strength_band": "useful_reference",
        "signal_strength_band_label_ja": "参考になる",
        "signal_strength_band_range": "50-69",
        "signal_strength_cap_reasons": ["context_profile_family_minimum_sources_missing"],
        "prediction_unavailable_reasons": [],
        "horizon_group_count": 1,
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
    }
    source_ledger = [
        {
            "ledger_version": "prediction_source_contribution_ledger.ps_q3a.v1",
            "source_id": "tier0_source_quality_gate",
            "source_family": "source_quality_freshness_integrity_gate",
            "gate_state": "passed",
            "effect": "none",
            "cap_applied": False,
        },
        {
            "ledger_version": "prediction_source_contribution_ledger.ps_q3b.v1",
            "source_id": "trend_short_horizon_v1",
            "source_family": "context_evidence_profile_minimum_source_gate",
            "effect": "family_profile_minimum_sources_missing_cap",
            "cap_percent": 59,
            "cap_applied": True,
        },
    ]
    horizon_card = {
        "card_version": "prediction_warroom_horizon_card.ps_q4a.v1",
        "horizon_group": "short_horizon",
        "display_label_ja": "短期",
        "horizons_sec": [300, 600, 900],
        "primary_label": "long_bias",
        "regime_state": "trend_candidate",
        "trend_bias": "long_bias",
        "confidence": "medium",
        "caution_level": "medium",
        "score": 0.59,
        "signal_strength_summary": primary_signal_summary,
        "estimated_signal_strength_percent": 59,
        "estimated_reference_hit_rate_percent": 59,
        "signal_strength_band": "useful_reference",
        "signal_strength_band_label_ja": "参考になる",
        "scenario_lite": {
            "scenario_balance_state": "continuation_bias",
            "turning_point_risk": "medium",
            "evidence_conflict_state": "context_evidence_profile_input_incomplete",
            "scenario_switch_hint": "watch_for_scenario_switch:false_break_or_reversal_resolution",
        },
        "invalidation_state": "soft_invalidation_watch",
        "scenario_switch_hint": "watch_for_scenario_switch:false_break_or_reversal_resolution",
        "lifetime": {
            "valid_from": "2026-06-20T00:00:00Z",
            "valid_until": "2026-06-20T00:05:00Z",
            "stale_after_sec": 300,
            "refresh_required": False,
        },
        "refresh_required": False,
        "trigger_eligibility_state": "not_applicable",
        "trigger_enabled": False,
        "human_narrative_ja": "短期は上方向がやや優勢。ただし根拠ソース不足のため参考度は59%に制限。",
        "blockers": [],
        "warnings": ["context_profile_family_minimum_sources_missing"],
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
    }
    family_card = {
        "card_version": "prediction_warroom_family_card.ps_q4a.v1",
        "prediction_id": "synthetic:trend_bias:300",
        "family": "trend_bias",
        "horizon_sec": 300,
        "primary_label": "long_bias",
        "confidence": "medium",
        "score": 0.59,
        "estimated_signal_strength_percent": 59,
        "estimated_reference_hit_rate_percent": 59,
        "source_quality_gate_state": "passed",
        "source_quality_gate_effect": "none",
        "signal_strength_cap_reason": "context_profile_family_minimum_sources_missing",
        "context_profile_source_caps": [
            {
                "ledger_version": "prediction_source_contribution_ledger.ps_q3b.v1",
                "evidence_profile_id": "trend_short_horizon_v1",
                "cap_percent": 59,
                "missing_minimum_required_sources": ["bitflyer_trades", "bitflyer_board_summary"],
            }
        ],
        "source_contribution_ledger": source_ledger,
        "driver_count": 2,
        "drivers": ["synthetic_trend_alignment", "synthetic_cross_venue_confirmation"],
        "blockers": [],
        "warnings": ["context_profile_family_minimum_sources_missing"],
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "synthetic_only": True,
    }
    return {
        "packet_version": "prediction_warroom_display_packet.ps_q4a.v1",
        "packet_id": f"prediction_warroom_display_packet.ps_q4a.v1:{SAMPLE_PREDICTION_RUN_ID}",
        "generated_at": "2026-06-20T00:00:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "prediction_run_id": SAMPLE_PREDICTION_RUN_ID,
        "headline_ja": "Synthetic: 短期は上方向優勢、参考度59%。",
        "primary_signal_summary": primary_signal_summary,
        "horizon_cards": [horizon_card],
        "family_cards": [family_card],
        "source_quality_panel": {
            "panel_version": "prediction_warroom_source_quality_panel.ps_q4a.v1",
            "tier0_source_quality_gate": {"gate_state": "passed", "gate_version": "prediction_tier0_source_quality_gate.ps_q2d.v1"},
            "source_artifact_coverage": {"input_coverage_state": "incomplete", "input_coverage_ratio": 0.75},
            "source_artifact_input_coverage_state": "incomplete",
            "source_artifact_input_coverage_ratio": 0.75,
            "selected_context_evidence_profile_ids": ["trend_short_horizon_v1"],
            "context_profile_signal_strength_cap_reasons": ["context_profile_family_minimum_sources_missing"],
            "read_only": True,
            "non_executing": True,
            "synthetic_only": True,
        },
        "evidence_panel": {
            "panel_version": "prediction_warroom_evidence_panel.ps_q4a.v1",
            "scenario_trace": {"trace_version": "synthetic_scenario_trace.ps_q4d.v1"},
            "scenario_digest": {"digest_version": "synthetic_scenario_digest.ps_q4d.v1"},
            "source_contribution_ledger_count": len(source_ledger),
            "family_card_count": 1,
            "horizon_card_count": 1,
            "read_only": True,
            "non_executing": True,
            "synthetic_only": True,
        },
        "warning_panel": {
            "panel_version": "prediction_warroom_warning_panel.ps_q4a.v1",
            "blockers": [],
            "warnings": ["context_profile_family_minimum_sources_missing"],
            "scenario_blockers": [],
            "scenario_warnings": ["context_profile_family_minimum_sources_missing"],
            "signal_strength_cap_reasons": ["context_profile_family_minimum_sources_missing"],
            "prediction_unavailable_reasons": [],
            "read_only": True,
            "non_executing": True,
            "synthetic_only": True,
        },
        "ui_contract": {
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
            "synthetic_only": True,
        },
        "boundaries": boundaries,
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "synthetic_only": True,
        "fixture_only": True,
    }


def build_prediction_warroom_sample_packet_bundle() -> PredictionWarRoomSamplePacketBundle:
    """Build a deterministic synthetic bundle spanning display packet, widget group index, and L4 adapter contract."""
    display_packet = build_prediction_warroom_sample_display_packet()
    widget_group_index = build_prediction_warroom_widget_group_packet_index(display_packet)
    adapter_contract = build_prediction_warroom_l4_latest_adapter_contract(display_packet=display_packet).to_dict()
    fixture_metadata = {
        "sample_version": SAMPLE_PACKET_VERSION,
        "sample_kind": "synthetic_prediction_warroom_fixture",
        "prediction_run_id": SAMPLE_PREDICTION_RUN_ID,
        "created_for": "WarRoom widget and L4/latest adapter contract validation",
        "safe_for_ui_snapshot_tests": True,
        "uses_live_market_data": False,
        "loads_runtime_artifacts": False,
        "writes_runtime_artifacts": False,
        "synthetic_only": True,
        "fixture_only": True,
    }
    return PredictionWarRoomSamplePacketBundle(
        sample_version=SAMPLE_PACKET_VERSION,
        sample_id=f"{SAMPLE_PACKET_VERSION}:{SAMPLE_PREDICTION_RUN_ID}",
        display_packet=display_packet,
        widget_group_index=widget_group_index,
        l4_latest_adapter_contract=adapter_contract,
        fixture_metadata=fixture_metadata,
    )


def build_prediction_warroom_sample_packet_index() -> dict[str, Any]:
    """Return a compact serializable index for synthetic WarRoom sample packets."""
    bundle = build_prediction_warroom_sample_packet_bundle().to_dict()
    widget_index = dict(bundle["widget_group_index"])
    adapter = dict(bundle["l4_latest_adapter_contract"])
    return {
        "sample_index_version": SAMPLE_PACKET_VERSION,
        "sample_id": bundle["sample_id"],
        "prediction_run_id": SAMPLE_PREDICTION_RUN_ID,
        "display_packet_version": bundle["display_packet"].get("packet_version"),
        "widget_group_index_version": widget_index.get("index_version"),
        "adapter_version": adapter.get("adapter_version"),
        "widget_group_count": widget_index.get("widget_group_count"),
        "widget_group_order": widget_index.get("widget_group_order"),
        "adapter_state": adapter.get("adapter_state"),
        "fixture_metadata": dict(bundle["fixture_metadata"]),
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
