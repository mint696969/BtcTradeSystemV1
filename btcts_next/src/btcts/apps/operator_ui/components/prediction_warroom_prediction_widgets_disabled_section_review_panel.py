# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widgets_disabled_section_review_panel.py
# desc: PS-Q17W pure-data disabled-section review packet builder for Prediction WarRoom widget skeleton packets. No Streamlit import, no D-hot read, no refresh, no writes.

from __future__ import annotations

from typing import Any, Mapping

PREDICTION_WARROOM_DISABLED_SECTION_REVIEW_PANEL_VERSION = "prediction_warroom_prediction_widgets_disabled_section_review_panel.ps_q17w.v1"
PAGE_PATCH_SOURCE = "PS-Q17V"
EXPECTED_WIDGET_COUNT = 12
EXPECTED_ZONE_ORDER = ("prediction_overview_zone", "prediction_realtime_review_zone", "prediction_operator_support_zone")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def build_prediction_widget_disabled_section_review_rows(packets: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, packet_value in enumerate(_as_list(packets)):
        packet = _as_mapping(packet_value)
        widget_id = str(packet.get("widget_family_id") or "")
        rows.append({
            "row_index": index,
            "widget_family_id": widget_id,
            "source_packet_id": str(packet.get("source_packet_id") or ""),
            "mount_zone_id": str(packet.get("mount_zone_id") or ""),
            "mount_slot_id": str(packet.get("mount_slot_id") or ""),
            "component_state": str(packet.get("component_state") or ""),
            "release_gate_state": str(packet.get("release_gate_state") or ""),
            "operator_summary_ja": str(packet.get("operator_summary_ja") or ""),
            "read_only": packet.get("read_only") is True,
            "non_executing": packet.get("non_executing") is True,
            "component_skeleton_only": packet.get("component_skeleton_only") is True,
            "fallback_component_only": packet.get("fallback_component_only") is True,
            "display_packet_only": packet.get("display_packet_only") is True,
            "streamlit_render_allowed": packet.get("streamlit_render_allowed") is True,
            "actual_source_read_allowed": packet.get("actual_source_read_allowed") is True,
            "refresh_invocation_allowed": packet.get("refresh_invocation_allowed") is True,
            "runtime_artifact_write_allowed": packet.get("runtime_artifact_write_allowed") is True,
            "status_artifact_write_allowed": packet.get("status_artifact_write_allowed") is True,
            "parameter_apply_allowed": packet.get("parameter_apply_allowed") is True,
            "parameter_staging_write_allowed": packet.get("parameter_staging_write_allowed") is True,
            "ledger_append_allowed": packet.get("ledger_append_allowed") is True,
            "autotrade_trigger_allowed": packet.get("autotrade_trigger_allowed") is True,
            "broker_private_api_allowed": packet.get("broker_private_api_allowed") is True,
            "review_row_state": "disabled_section_review_row_ready_render_still_disabled",
        })
    return rows


def build_prediction_widget_disabled_section_zone_rows(review_rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_rows = [_as_mapping(row) for row in _as_list(review_rows)]
    for zone_id in EXPECTED_ZONE_ORDER:
        zone_rows = [row for row in source_rows if row.get("mount_zone_id") == zone_id]
        rows.append({
            "mount_zone_id": zone_id,
            "review_row_count": len(zone_rows),
            "widget_family_ids": [str(row.get("widget_family_id") or "") for row in zone_rows],
            "all_render_disabled": all(row.get("streamlit_render_allowed") is False for row in zone_rows),
            "all_actual_source_read_disabled": all(row.get("actual_source_read_allowed") is False for row in zone_rows),
            "zone_review_state": "disabled_section_zone_review_ready_render_still_disabled",
        })
    return rows


def build_prediction_warroom_prediction_widgets_disabled_section_review_packet(*, packets: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...], source_checker_version: str = "", page_patch_checker_version: str = "") -> dict[str, Any]:
    review_rows = build_prediction_widget_disabled_section_review_rows(packets)
    zone_rows = build_prediction_widget_disabled_section_zone_rows(review_rows)
    failures: list[str] = []
    if len(review_rows) != EXPECTED_WIDGET_COUNT:
        failures.append("review_row_count_mismatch")
    for row in review_rows:
        widget_id = str(row.get("widget_family_id") or "")
        if row.get("component_state") != "read_only_component_skeleton_render_disabled":
            failures.append(f"component_state_mismatch:{widget_id}")
        for key in ("read_only", "non_executing", "component_skeleton_only", "fallback_component_only", "display_packet_only"):
            if row.get(key) is not True:
                failures.append(f"true_boundary_missing:{widget_id}:{key}")
        for key in (
            "streamlit_render_allowed",
            "actual_source_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"false_boundary_not_false:{widget_id}:{key}")
    return {
        "ok": not failures,
        "panel_version": PREDICTION_WARROOM_DISABLED_SECTION_REVIEW_PANEL_VERSION,
        "page_patch_source": PAGE_PATCH_SOURCE,
        "source_checker_version": str(source_checker_version or ""),
        "page_patch_checker_version": str(page_patch_checker_version or ""),
        "review_state": "disabled_section_review_packet_ready_render_still_disabled",
        "review_row_count": len(review_rows),
        "review_zone_count": len(zone_rows),
        "review_rows": review_rows,
        "zone_rows": zone_rows,
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "disabled_section_review_only": True,
        "pure_data_review_packet": True,
        "streamlit_render_allowed": False,
        "warroom_page_mutation_allowed": False,
        "page_body_call_enabled": False,
        "future_section_call_enabled": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }
