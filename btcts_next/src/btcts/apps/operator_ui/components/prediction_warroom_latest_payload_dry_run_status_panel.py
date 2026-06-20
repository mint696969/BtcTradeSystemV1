# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_dry_run_status_panel.py
# desc: Display-only WarRoom status panel packet for latest-payload loader dry-run simulation. Pure transform; no file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_latest_payload_loader_dry_run_simulator import (
    LOADER_DRY_RUN_SIMULATOR_VERSION,
    build_prediction_warroom_latest_payload_loader_dry_run_simulation,
)

DRY_RUN_STATUS_PANEL_VERSION = "prediction_warroom_latest_payload_dry_run_status_panel.ps_q6d.v1"


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadDryRunStatusPanelPacket:
    panel_version: str
    panel_id: str
    panel_state: str
    panel_label_ja: str
    widget_group_id: str
    refresh_group_id: str
    refresh_interval_sec: int
    refresh_priority: int
    source_simulation_version: str | None = None
    source_simulation_state: str | None = None
    headline_ja: str = ""
    status_badge: Mapping[str, Any] = field(default_factory=dict)
    summary_metrics: Mapping[str, Any] = field(default_factory=dict)
    artifact_status_cards: Tuple[Mapping[str, Any], ...] = ()
    blocked_reason_cards: Tuple[Mapping[str, Any], ...] = ()
    warning_reason_cards: Tuple[Mapping[str, Any], ...] = ()
    operator_guidance_ja: Tuple[str, ...] = ()
    ui_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    stale_behavior: str = "show_blocked_or_stale_badge_keep_last_good_packet"
    independent_refresh_allowed: bool = True
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    actual_loader_execution_allowed: bool = False
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panel_version": self.panel_version,
            "panel_id": self.panel_id,
            "panel_state": self.panel_state,
            "panel_label_ja": self.panel_label_ja,
            "widget_group_id": self.widget_group_id,
            "refresh_group_id": self.refresh_group_id,
            "refresh_interval_sec": self.refresh_interval_sec,
            "refresh_priority": self.refresh_priority,
            "source_simulation_version": self.source_simulation_version,
            "source_simulation_state": self.source_simulation_state,
            "headline_ja": self.headline_ja,
            "status_badge": dict(self.status_badge),
            "summary_metrics": dict(self.summary_metrics),
            "artifact_status_cards": [dict(item) for item in self.artifact_status_cards],
            "blocked_reason_cards": [dict(item) for item in self.blocked_reason_cards],
            "warning_reason_cards": [dict(item) for item in self.warning_reason_cards],
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "ui_contract": dict(self.ui_contract),
            "boundaries": dict(self.boundaries),
            "stale_behavior": self.stale_behavior,
            "independent_refresh_allowed": self.independent_refresh_allowed,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "actual_loader_execution_allowed": self.actual_loader_execution_allowed,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _severity_for_evaluation(item: Mapping[str, Any]) -> str:
    if item.get("candidate_for_future_guarded_loader") is True:
        return "candidate"
    if item.get("required") is True:
        return "blocked"
    if item.get("supplied_by_metadata_input") is True and item.get("blocker_reasons"):
        return "blocked_optional"
    return "warning"


def _status_badge(simulation: Mapping[str, Any]) -> Mapping[str, Any]:
    if simulation.get("simulated_preflight_ready_for_payload_handoff") is True and int(simulation.get("candidate_artifact_count", 0) or 0) > 0:
        return {
            "badge_kind": "candidate_disabled",
            "label_ja": "候補あり・実ローダー無効",
            "color_hint": "amber",
            "operator_message_ja": "メタデータ上は候補がありますが、PS-Q6Dでは実ファイル読み込みは許可されていません。",
        }
    return {
        "badge_kind": "blocked_or_waiting",
        "label_ja": "未読込・待機/ブロック",
        "color_hint": "red",
        "operator_message_ja": "最新payloadは未読込です。dry-run metadataまたは将来loaderのguardが必要です。",
    }


def _artifact_card(item: Mapping[str, Any], idx: int) -> Mapping[str, Any]:
    severity = _severity_for_evaluation(item)
    candidate = item.get("candidate_for_future_guarded_loader") is True
    return {
        "card_version": DRY_RUN_STATUS_PANEL_VERSION,
        "card_kind": "latest_payload_artifact_dry_run_status",
        "card_id": f"latest_payload_artifact:{idx}:{item.get('artifact_role') or 'unknown'}",
        "artifact_role": item.get("artifact_role"),
        "required": bool(item.get("required", False)),
        "severity": severity,
        "candidate_for_future_guarded_loader": candidate,
        "dry_run_outcome": item.get("dry_run_outcome"),
        "path_scope_status": item.get("path_scope_status"),
        "extension_status": item.get("extension_status"),
        "file_size_status": item.get("file_size_status"),
        "freshness_status": item.get("freshness_status"),
        "schema_validation_status": item.get("schema_validation_status"),
        "observed_age_sec": item.get("observed_age_sec"),
        "observed_file_size_bytes": item.get("observed_file_size_bytes"),
        "blocker_count": len(_list(item.get("blocker_reasons"))),
        "warning_count": len(_list(item.get("warning_reasons"))),
        "blocker_reasons": _list(item.get("blocker_reasons")),
        "warning_reasons": _list(item.get("warning_reasons")),
        "operator_action_kind": "observe_only",
        "operator_message_ja": "将来loader候補です。実読込はまだ無効です。" if candidate else "このartifactはdry-run上で未候補またはブロック中です。",
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "actual_file_read_allowed_by_this_contract": False,
        "would_read_runtime_file": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }


def _reason_cards(reasons: Iterable[Any], *, kind: str) -> Tuple[Mapping[str, Any], ...]:
    cards: list[Mapping[str, Any]] = []
    for idx, raw in enumerate(reasons):
        reason = str(raw)
        if not reason:
            continue
        cards.append({
            "card_version": DRY_RUN_STATUS_PANEL_VERSION,
            "card_kind": kind,
            "card_id": f"{kind}:{idx}:{reason}",
            "reason_code": reason,
            "operator_action_kind": "observe_only",
            "operator_message_ja": "実payload表示前に解消が必要です。" if kind == "blocked_reason" else "将来loader実装時に確認してください。",
            "read_only": True,
            "non_executing": True,
            "display_only": True,
            "render_intent_only": True,
            "would_read_runtime_file": False,
            "would_write_runtime_artifact": False,
            "would_send_to_broker": False,
        })
    return tuple(cards)


def build_prediction_warroom_latest_payload_dry_run_status_panel(
    *,
    simulation_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLatestPayloadDryRunStatusPanelPacket:
    """Build a display-only WarRoom status panel from a Q6C dry-run simulation or metadata-only inputs."""
    simulation = _as_mapping(simulation_packet)
    if not simulation:
        simulation = build_prediction_warroom_latest_payload_loader_dry_run_simulation(
            artifact_metadata_inputs=artifact_metadata_inputs,
            hot_latest_root_hint=hot_latest_root_hint,
        ).to_dict()
    evaluations = tuple(_artifact_card(_as_mapping(item), idx) for idx, item in enumerate(_list(simulation.get("artifact_evaluations"))))
    candidate_count = int(simulation.get("candidate_artifact_count", 0) or 0)
    blocker_count = int(simulation.get("evaluation_blocker_count", 0) or 0)
    warning_count = int(simulation.get("evaluation_warning_count", 0) or 0)
    preflight_ready = simulation.get("simulated_preflight_ready_for_payload_handoff") is True
    badge = _status_badge(simulation)
    panel_state = "candidate_visible_actual_loader_disabled" if preflight_ready and candidate_count else "blocked_or_waiting_actual_loader_disabled"
    headline = "最新payload候補はありますが、実ローダーは無効です。" if candidate_count else "最新payloadは未読込・待機/ブロック中です。"
    boundaries = {
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
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
    }
    return PredictionWarRoomLatestPayloadDryRunStatusPanelPacket(
        panel_version=DRY_RUN_STATUS_PANEL_VERSION,
        panel_id=f"{DRY_RUN_STATUS_PANEL_VERSION}:latest:{simulation.get('simulation_id') or 'pending'}",
        panel_state=panel_state,
        panel_label_ja="Prediction latest payload dry-run status",
        widget_group_id="prediction_latest_payload_dry_run_status_widget",
        refresh_group_id="prediction_warroom:latest_payload_dry_run_status_widget",
        refresh_interval_sec=30,
        refresh_priority=55,
        source_simulation_version=str(simulation.get("simulation_version")) if simulation.get("simulation_version") else LOADER_DRY_RUN_SIMULATOR_VERSION,
        source_simulation_state=str(simulation.get("simulation_state")) if simulation.get("simulation_state") else None,
        headline_ja=headline,
        status_badge=badge,
        summary_metrics={
            "candidate_artifact_count": candidate_count,
            "evaluation_blocker_count": blocker_count,
            "evaluation_warning_count": warning_count,
            "artifact_evaluation_count": len(evaluations),
            "simulated_preflight_ready_for_payload_handoff": preflight_ready,
            "actual_loader_execution_allowed": False,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
        },
        artifact_status_cards=evaluations,
        blocked_reason_cards=_reason_cards(_list(simulation.get("blocked_reasons")), kind="blocked_reason"),
        warning_reason_cards=_reason_cards(_list(simulation.get("warning_reasons")), kind="warning_reason"),
        operator_guidance_ja=(
            "このpanelはdry-run表示専用です。",
            "実payload表示には別sliceでloader guardとhuman approvalが必要です。",
            "ブロック理由がある場合は、実読込前にpath/freshness/schema条件を確認してください。",
        ),
        ui_contract={
            "widget_group_id": "prediction_latest_payload_dry_run_status_widget",
            "display_group": "prediction_warroom_latest_payload_dry_run",
            "auto_refresh_expected": True,
            "trigger_buttons_allowed": False,
            "broker_controls_allowed": False,
            "mode_controls_allowed": False,
            "file_picker_allowed": False,
            "operator_action_kind": "observe_only",
        },
        boundaries=boundaries,
    )
