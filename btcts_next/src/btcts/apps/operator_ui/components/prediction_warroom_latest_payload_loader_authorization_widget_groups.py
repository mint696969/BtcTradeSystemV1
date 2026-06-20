# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_authorization_widget_groups.py
# desc: Supplemental widget-group index for Prediction WarRoom latest-payload loader authorization request status. Display grouping only; no approval write, loader execution, file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_latest_payload_loader_authorization_request import (
    LOADER_AUTHORIZATION_REQUEST_VERSION,
    build_prediction_warroom_latest_payload_loader_authorization_request,
)
from .prediction_warroom_widget_groups import PredictionWarRoomWidgetGroupPacket

AUTHORIZATION_WIDGET_GROUP_VERSION = "prediction_warroom_latest_payload_loader_authorization_widget_groups.ps_q7b.v1"
AUTHORIZATION_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"
ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_dry_run_status_widget"


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadLoaderAuthorizationWidgetGroupIndex:
    index_version: str
    supplemental_widget_group_count: int = 0
    attach_after_widget_group_id: str = ATTACH_AFTER_WIDGET_GROUP_ID
    supplemental_widget_group_order: Tuple[str, ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    source_authorization_request_version: str = LOADER_AUTHORIZATION_REQUEST_VERSION
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    approval_granted_by_this_contract: bool = False
    authorization_granted_by_this_contract: bool = False
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
            "index_version": self.index_version,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "attach_after_widget_group_id": self.attach_after_widget_group_id,
            "supplemental_widget_group_order": list(self.supplemental_widget_group_order),
            "auto_refresh_groups": [dict(item) for item in self.auto_refresh_groups],
            "widget_groups": [dict(item) for item in self.widget_groups],
            "integration_contract": dict(self.integration_contract),
            "source_authorization_request_version": self.source_authorization_request_version,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "approval_granted_by_this_contract": self.approval_granted_by_this_contract,
            "authorization_granted_by_this_contract": self.authorization_granted_by_this_contract,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
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


def _badge_for_state(state: str) -> Mapping[str, Any]:
    if state == "prepared_for_human_review_actual_read_disabled":
        return {
            "badge_kind": "review_ready_loader_disabled",
            "badge_label_ja": "レビュー待ち・読取無効",
            "severity": "info",
            "operator_action_required": True,
            **_safe_flags(),
        }
    return {
        "badge_kind": "blocked_loader_disabled",
        "badge_label_ja": "ブロック中・読取無効",
        "severity": "warning",
        "operator_action_required": True,
        **_safe_flags(),
    }


def _review_cards(request: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    cards: list[Mapping[str, Any]] = []
    for idx, item in enumerate(_list(request.get("authorization_review_sequence")), start=1):
        cards.append(
            {
                "card_id": f"authorization_review_step_{idx:02d}",
                "sequence_no": idx,
                "review_item": str(item),
                "review_state": "required_before_future_loader_slice",
                "checked_by_this_widget": False,
                **_safe_flags(),
            }
        )
    return tuple(cards)


def _failure_cards(request: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    cards: list[Mapping[str, Any]] = []
    for idx, item in enumerate(_list(request.get("authorization_failure_behavior_sequence")), start=1):
        cards.append(
            {
                "card_id": f"authorization_failure_behavior_{idx:02d}",
                "sequence_no": idx,
                "failure_behavior": str(item),
                "enforced_by_this_widget": False,
                "displayed_for_operator_awareness": True,
                **_safe_flags(),
            }
        )
    return tuple(cards)


def _payload_from_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    state = str(request.get("authorization_request_state") or "unknown")
    ready = request.get("request_ready_for_human_review") is True
    safe = request.get("permission_contract_safe_for_request") is True
    headline = "最新payload loader承認レビュー待ち（読取無効）" if ready and safe else "最新payload loader承認リクエストはブロック中（読取無効）"
    return {
        "payload_version": AUTHORIZATION_WIDGET_GROUP_VERSION,
        "source_authorization_request_version": request.get("authorization_request_version"),
        "authorization_request_id": request.get("authorization_request_id"),
        "authorization_request_state": state,
        "authorization_request_kind": request.get("authorization_request_kind"),
        "headline_ja": headline,
        "status_badge": dict(_badge_for_state(state)),
        "summary_metrics": {
            "request_ready_for_human_review": ready,
            "permission_contract_safe_for_request": safe,
            "requested_path_rule_count": int(request.get("requested_path_rule_count") or 0),
            "required_artifact_count": int(request.get("required_artifact_count") or 0),
            "optional_artifact_count": int(request.get("optional_artifact_count") or 0),
            "approval_granted_by_this_contract": False,
            "authorization_granted_by_this_contract": False,
            "actual_loader_execution_allowed": False,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
        },
        "requested_loader_scope": request.get("requested_loader_scope"),
        "requested_artifact_roles": list(request.get("requested_artifact_roles") or ()),
        "authorization_review_cards": [dict(item) for item in _review_cards(request)],
        "authorization_failure_behavior_cards": [dict(item) for item in _failure_cards(request)],
        "authorization_gates": dict(_as_mapping(request.get("authorization_gates"))),
        "approval_contract": dict(_as_mapping(request.get("approval_contract"))),
        "permission_contract_summary": dict(_as_mapping(request.get("permission_contract_summary"))),
        "boundaries": dict(_as_mapping(request.get("boundaries"))),
        "operator_guidance_ja": (
            "このwidgetは承認状態を表示するだけで、承認の記録・loader実行・hot/latest読取・payload decodeは行いません。",
            "実loaderを実装する場合は、別slice・別guard・別commitで明示的に進めてください。",
            "承認が必要な場合でも、このcontract自体は approval_granted_by_this_contract=False のままです。",
        ),
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        **_safe_flags(),
    }


def build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet(
    *,
    authorization_request: Mapping[str, Any] | Any | None = None,
    permission_contract: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomWidgetGroupPacket:
    """Build a supplemental display-only widget group for the Q7A latest-payload loader authorization request."""
    request = dict(_as_mapping(authorization_request)) if authorization_request is not None else build_prediction_warroom_latest_payload_loader_authorization_request(
        permission_contract=permission_contract,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    payload = _payload_from_request(request)
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=AUTHORIZATION_WIDGET_GROUP_VERSION,
        widget_group_id=AUTHORIZATION_WIDGET_GROUP_ID,
        widget_group_label_ja="最新payload loader承認状態",
        widget_group_kind="latest_payload_loader_authorization_status",
        refresh_group_id=f"prediction_warroom:{AUTHORIZATION_WIDGET_GROUP_ID}",
        refresh_interval_sec=60,
        refresh_priority=58,
        payload=payload,
        data_dependencies=(
            "q7a.latest_payload_loader_authorization_request",
            "q6b.loader_permission_contract",
            "q6a.latest_payload_preflight_status",
        ),
        stale_behavior="show_authorization_stale_badge_keep_loader_disabled",
        independent_refresh_allowed=True,
        ui_mount_hint="warroom_prediction:latest_payload_loader_authorization_status",
    )


def build_prediction_warroom_latest_payload_loader_authorization_widget_group_index(
    *,
    authorization_request: Mapping[str, Any] | Any | None = None,
    permission_contract: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLatestPayloadLoaderAuthorizationWidgetGroupIndex:
    """Return supplemental widget-group metadata for the latest-payload loader authorization request without rendering or file reads."""
    group = build_prediction_warroom_latest_payload_loader_authorization_widget_group_packet(
        authorization_request=authorization_request,
        permission_contract=permission_contract,
        hot_latest_root_hint=hot_latest_root_hint,
    )
    group_dict = group.to_dict()
    group_dict.update(_safe_flags())
    payload = dict(group_dict.get("payload") or {})
    payload.update(_safe_flags())
    group_dict["payload"] = payload
    auto_refresh = {
        "widget_group_id": group.widget_group_id,
        "refresh_group_id": group.refresh_group_id,
        "refresh_interval_sec": group.refresh_interval_sec,
        "refresh_priority": group.refresh_priority,
        "data_dependencies": list(group.data_dependencies),
        "independent_refresh_allowed": group.independent_refresh_allowed,
        "stale_behavior": group.stale_behavior,
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        **_safe_flags(),
    }
    integration_contract = {
        "contract_version": AUTHORIZATION_WIDGET_GROUP_VERSION,
        "authorization_request_contract": LOADER_AUTHORIZATION_REQUEST_VERSION,
        "integration_kind": "supplemental_widget_group_append_after_latest_payload_dry_run_status",
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "does_not_modify_base_q4b_group_order": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        **_safe_flags(),
    }
    return PredictionWarRoomLatestPayloadLoaderAuthorizationWidgetGroupIndex(
        index_version=AUTHORIZATION_WIDGET_GROUP_VERSION,
        supplemental_widget_group_count=1,
        attach_after_widget_group_id=ATTACH_AFTER_WIDGET_GROUP_ID,
        supplemental_widget_group_order=(group.widget_group_id,),
        auto_refresh_groups=(auto_refresh,),
        widget_groups=(group_dict,),
        integration_contract=integration_contract,
    )
