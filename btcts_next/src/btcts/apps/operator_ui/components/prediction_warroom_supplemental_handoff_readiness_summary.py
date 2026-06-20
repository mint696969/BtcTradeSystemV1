# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_readiness_summary.py
# desc: Read-only operator-facing readiness summary for the registered Prediction WarRoom supplemental handoff chain. Metadata derivation only; no registry mutation, rendering, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_handoff_catalog_visibility import (
    HANDOFF_CATALOG_VISIBILITY_VERSION,
    build_prediction_warroom_handoff_catalog_visibility_entry,
)

SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_VERSION = "prediction_warroom_supplemental_handoff_readiness_summary.ps_q7j.v1"
SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_ID = "prediction_warroom_supplemental_handoff_readiness_summary"
EXPECTED_BASE_WIDGET_GROUP_COUNT = 6
EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT = 5
EXPECTED_TOTAL_WIDGET_GROUP_COUNT = 11
EXPECTED_VISIBILITY_GROUP_COUNT = 6
EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_CHAIN: Tuple[Mapping[str, Any], ...] = (
    {
        "widget_group_id": "source_quality_explanation_widgets",
        "visibility_group_id": "prediction_warroom_source_explanation_visibility",
        "expected_attach_after_widget_group_id": "source_quality_widget",
        "chain_role": "source_quality_explanation",
    },
    {
        "widget_group_id": "prediction_latest_payload_dry_run_status_widget",
        "visibility_group_id": "prediction_warroom_latest_payload_dry_run_visibility",
        "expected_attach_after_widget_group_id": "warning_refresh_widget",
        "chain_role": "latest_payload_dry_run_status",
    },
    {
        "widget_group_id": "prediction_latest_payload_loader_authorization_widget",
        "visibility_group_id": "prediction_warroom_loader_authorization_visibility",
        "expected_attach_after_widget_group_id": "prediction_latest_payload_dry_run_status_widget",
        "chain_role": "loader_authorization_status",
    },
    {
        "widget_group_id": "prediction_latest_payload_loader_authorization_registry_summary_widget",
        "visibility_group_id": "prediction_warroom_loader_authorization_registry_summary_visibility",
        "expected_attach_after_widget_group_id": "prediction_latest_payload_loader_authorization_widget",
        "chain_role": "loader_authorization_registry_summary",
    },
    {
        "widget_group_id": "prediction_authorization_handoff_status_widget",
        "visibility_group_id": "prediction_warroom_authorization_handoff_status_visibility",
        "expected_attach_after_widget_group_id": "prediction_latest_payload_loader_authorization_registry_summary_widget",
        "chain_role": "authorization_handoff_status",
    },
)


@dataclass(frozen=True)
class PredictionWarRoomSupplementalHandoffReadinessSummary:
    summary_version: str
    summary_id: str
    summary_kind: str
    readiness_state: str
    visibility_state: str | None = None
    handoff_state: str | None = None
    prediction_run_id: str | None = None
    source_handoff_catalog_version: str = HANDOFF_CATALOG_VISIBILITY_VERSION
    readiness_metrics: Mapping[str, Any] = field(default_factory=dict)
    supplemental_chain_readiness: Tuple[Mapping[str, Any], ...] = ()
    readiness_blockers: Tuple[Mapping[str, Any], ...] = ()
    readiness_warnings: Tuple[Mapping[str, Any], ...] = ()
    operator_guidance_ja: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    summary_only: bool = True
    readiness_metadata_only: bool = True
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
            "summary_version": self.summary_version,
            "summary_id": self.summary_id,
            "summary_kind": self.summary_kind,
            "readiness_state": self.readiness_state,
            "visibility_state": self.visibility_state,
            "handoff_state": self.handoff_state,
            "prediction_run_id": self.prediction_run_id,
            "source_handoff_catalog_version": self.source_handoff_catalog_version,
            "readiness_metrics": dict(self.readiness_metrics),
            "supplemental_chain_readiness": [dict(item) for item in self.supplemental_chain_readiness],
            "readiness_blockers": [dict(item) for item in self.readiness_blockers],
            "readiness_warnings": [dict(item) for item in self.readiness_warnings],
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "summary_only": self.summary_only,
            "readiness_metadata_only": self.readiness_metadata_only,
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
        "summary_only": True,
        "readiness_metadata_only": True,
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


def _visibility_groups_by_id(catalog_entry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    groups: Dict[str, Mapping[str, Any]] = {}
    for raw in _list(catalog_entry.get("visibility_groups")):
        group = _as_mapping(raw)
        group_id = str(group.get("visibility_group_id") or "")
        if group_id:
            groups[group_id] = group
    return groups


def _blocker(issue_code: str, message_ja: str, *, widget_group_id: str | None = None, visibility_group_id: str | None = None) -> Mapping[str, Any]:
    payload = {
        "issue_code": issue_code,
        "severity": "blocker",
        "message_ja": message_ja,
        "widget_group_id": widget_group_id,
        "visibility_group_id": visibility_group_id,
        **_safe_flags(),
    }
    return {key: value for key, value in payload.items() if value is not None}


def _chain_readiness(catalog_entry: Mapping[str, Any]) -> tuple[Tuple[Mapping[str, Any], ...], Tuple[Mapping[str, Any], ...]]:
    combined_order = [str(item) for item in _list(catalog_entry.get("combined_widget_group_order"))]
    visibility_groups = _visibility_groups_by_id(catalog_entry)
    rows: list[Mapping[str, Any]] = []
    blockers: list[Mapping[str, Any]] = []
    previous_order_index: int | None = None
    for expected in EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_CHAIN:
        widget_group_id = str(expected["widget_group_id"])
        visibility_group_id = str(expected["visibility_group_id"])
        expected_attach = str(expected["expected_attach_after_widget_group_id"])
        group = visibility_groups.get(visibility_group_id, {})
        widget_ids = [str(item) for item in _list(group.get("widget_group_ids"))]
        present_in_order = widget_group_id in combined_order
        present_in_visibility = widget_group_id in widget_ids
        attach_after = group.get("attach_after_widget_group_id")
        attach_ok = attach_after == expected_attach
        order_index = combined_order.index(widget_group_id) if present_in_order else None
        order_after_previous_ok = previous_order_index is None or (order_index is not None and order_index > previous_order_index)
        ready = present_in_order and present_in_visibility and attach_ok and order_after_previous_ok
        if not present_in_order:
            blockers.append(_blocker("widget_missing_from_combined_order", "supplemental widgetがcombined orderにありません。", widget_group_id=widget_group_id, visibility_group_id=visibility_group_id))
        if not present_in_visibility:
            blockers.append(_blocker("widget_missing_from_visibility_group", "supplemental widgetがvisibility groupにありません。", widget_group_id=widget_group_id, visibility_group_id=visibility_group_id))
        if not attach_ok:
            blockers.append(_blocker("unexpected_attach_after_widget_group_id", "supplemental widgetのattach先が期待値と一致しません。", widget_group_id=widget_group_id, visibility_group_id=visibility_group_id))
        if not order_after_previous_ok:
            blockers.append(_blocker("supplemental_chain_order_mismatch", "supplemental widget chainの順序が期待値と一致しません。", widget_group_id=widget_group_id, visibility_group_id=visibility_group_id))
        if order_index is not None:
            previous_order_index = order_index
        rows.append(
            {
                "widget_group_id": widget_group_id,
                "visibility_group_id": visibility_group_id,
                "chain_role": expected.get("chain_role"),
                "expected_attach_after_widget_group_id": expected_attach,
                "actual_attach_after_widget_group_id": attach_after,
                "present_in_combined_order": present_in_order,
                "present_in_visibility_group": present_in_visibility,
                "attach_after_ok": attach_ok,
                "order_index": order_index,
                "order_after_previous_ok": order_after_previous_ok,
                "ready": ready,
                **_safe_flags(),
            }
        )
    return tuple(rows), tuple(blockers)


def _readiness_state(*, visible: bool, counts_ok: bool, chain_ready: bool, blocker_count: int) -> str:
    if visible and counts_ok and chain_ready and blocker_count == 0:
        return "ready_supplemental_handoff_visible_loader_disabled"
    if not visible:
        return "hidden_or_blocked_supplemental_handoff_loader_disabled"
    if not counts_ok:
        return "blocked_supplemental_handoff_count_mismatch_loader_disabled"
    if not chain_ready:
        return "blocked_supplemental_handoff_chain_mismatch_loader_disabled"
    return "blocked_supplemental_handoff_readiness_loader_disabled"


def build_prediction_warroom_supplemental_handoff_readiness_summary(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomSupplementalHandoffReadinessSummary:
    """Build a read-only readiness summary over the registered supplemental handoff chain."""
    entry = dict(_as_mapping(catalog_entry)) if catalog_entry is not None else build_prediction_warroom_handoff_catalog_visibility_entry(
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    chain, chain_blockers = _chain_readiness(entry)
    counts = {
        "base_widget_group_count": int(entry.get("base_widget_group_count") or 0),
        "supplemental_widget_group_count": int(entry.get("supplemental_widget_group_count") or 0),
        "total_widget_group_count": int(entry.get("total_widget_group_count") or 0),
        "visibility_group_count": int(entry.get("visibility_group_count") or 0),
    }
    expected_counts = {
        "base_widget_group_count": EXPECTED_BASE_WIDGET_GROUP_COUNT,
        "supplemental_widget_group_count": EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT,
        "total_widget_group_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "visibility_group_count": EXPECTED_VISIBILITY_GROUP_COUNT,
    }
    counts_ok = counts == expected_counts
    count_blockers: list[Mapping[str, Any]] = []
    if not counts_ok:
        count_blockers.append(_blocker("supplemental_handoff_count_mismatch", "supplemental handoffの件数が期待値と一致しません。"))
    visible = entry.get("visibility_state") == "visible_read_only" and entry.get("handoff_state") == "ready_for_read_only_warroom_handoff"
    chain_ready = all(bool(item.get("ready")) for item in chain)
    blockers = tuple([*count_blockers, *chain_blockers])
    metrics = {
        **counts,
        "expected_base_widget_group_count": EXPECTED_BASE_WIDGET_GROUP_COUNT,
        "expected_supplemental_widget_group_count": EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT,
        "expected_total_widget_group_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "expected_visibility_group_count": EXPECTED_VISIBILITY_GROUP_COUNT,
        "counts_ok": counts_ok,
        "chain_ready": chain_ready,
        "ready_widget_count": sum(1 for item in chain if item.get("ready") is True),
        "expected_supplemental_chain_length": len(EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_CHAIN),
        "blocker_count": len(blockers),
        "warning_count": 0,
        "preflight_visible_read_only": visible,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    readiness_state = _readiness_state(visible=visible, counts_ok=counts_ok, chain_ready=chain_ready, blocker_count=len(blockers))
    integration_contract = {
        "contract_version": SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_VERSION,
        "source_handoff_catalog_contract": HANDOFF_CATALOG_VISIBILITY_VERSION,
        "integration_kind": "read_only_supplemental_handoff_readiness_summary",
        "summary_derivation_only": True,
        "does_not_modify_handoff_catalog": True,
        "does_not_register_widgets": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        **_safe_flags(),
    }
    guidance = (
        "このsummaryは登録済みsupplemental widget chainの可視性・順序・attach状態を要約するだけです。",
        "ready状態でも承認記録・loader実行・hot/latest読取・payload decodeは行いません。",
        "実loaderや承認書込を進める場合は、別slice・別guard・別commitで扱ってください。",
    )
    return PredictionWarRoomSupplementalHandoffReadinessSummary(
        summary_version=SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_VERSION,
        summary_id=SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_ID,
        summary_kind="prediction_warroom_registered_supplemental_handoff_readiness_summary",
        readiness_state=readiness_state,
        visibility_state=str(entry.get("visibility_state")) if entry.get("visibility_state") else None,
        handoff_state=str(entry.get("handoff_state")) if entry.get("handoff_state") else None,
        prediction_run_id=str(entry.get("prediction_run_id")) if entry.get("prediction_run_id") else None,
        readiness_metrics=metrics,
        supplemental_chain_readiness=chain,
        readiness_blockers=blockers,
        readiness_warnings=(),
        operator_guidance_ja=guidance,
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_supplemental_handoff_readiness_summary_index(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact read-only index for the registered supplemental handoff readiness summary."""
    summary = build_prediction_warroom_supplemental_handoff_readiness_summary(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "summary_index_version": SUPPLEMENTAL_HANDOFF_READINESS_SUMMARY_VERSION,
        "summary_id": summary.get("summary_id"),
        "summary_kind": summary.get("summary_kind"),
        "readiness_state": summary.get("readiness_state"),
        "visibility_state": summary.get("visibility_state"),
        "handoff_state": summary.get("handoff_state"),
        "readiness_metrics": dict(_as_mapping(summary.get("readiness_metrics"))),
        "supplemental_chain_readiness": [dict(item) for item in _list(summary.get("supplemental_chain_readiness"))],
        "readiness_blockers": [dict(item) for item in _list(summary.get("readiness_blockers"))],
        "integration_contract": dict(_as_mapping(summary.get("integration_contract"))),
        "boundaries": dict(_as_mapping(summary.get("boundaries"))),
        **_safe_flags(),
    }
