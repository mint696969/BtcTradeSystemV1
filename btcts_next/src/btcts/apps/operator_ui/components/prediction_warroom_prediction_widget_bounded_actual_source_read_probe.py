# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_bounded_actual_source_read_probe.py
# desc: PS-Q18B bounded read-only actual-source read probe for one explicitly supplied JSON artifact. No Streamlit import, no D-hot discovery, no refresh, no writes.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION = "prediction_warroom_prediction_widget_bounded_actual_source_read_probe.ps_q18b.v1"
ALLOW_ACK = "PS_Q18B_ALLOW_ONE_BOUNDED_READ_ONLY_JSON_PROBE"
DEFAULT_MAX_BYTES = 65536


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _preview_keys(payload: Any) -> list[str]:
    if isinstance(payload, Mapping):
        return [str(key) for key in list(payload.keys())[:12]]
    return []


def build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet(
    *,
    source_packet_id: str,
    source_artifact_ref_field: str,
    explicit_source_path: str = "",
    allow_actual_read: bool = False,
    explicit_ack: str = "",
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    """Read one explicitly supplied JSON file only when allow flag and ack are both present."""
    blockers: list[str] = []
    warnings: list[str] = []
    path_hint = str(explicit_source_path or "")
    source_packet = str(source_packet_id or "")
    artifact_ref_field = str(source_artifact_ref_field or "")
    max_read_bytes = max(1, int(max_bytes or DEFAULT_MAX_BYTES))
    payload: Any | None = None
    observed_file_size_bytes: int | None = None
    payload_preview_keys: list[str] = []
    actual_file_read_attempted = False
    actual_file_read_succeeded = False
    payload_decode_attempted = False
    payload_decode_succeeded = False
    path_exists_checked = False
    path_exists = False
    schema_probe_checked = False
    schema_probe_ok = False
    exception_class = ""
    exception_message = ""

    if not source_packet:
        blockers.append("source_packet_id_missing")
    if not artifact_ref_field:
        blockers.append("source_artifact_ref_field_missing")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    if explicit_ack != ALLOW_ACK:
        blockers.append("explicit_ack_missing_or_mismatch")
    if not path_hint:
        blockers.append("explicit_source_path_missing")

    if not blockers:
        path = Path(path_hint)
        path_exists_checked = True
        path_exists = path.exists() and path.is_file()
        if not path_exists:
            blockers.append("explicit_source_path_not_file")
        else:
            try:
                observed_file_size_bytes = int(path.stat().st_size)
                if observed_file_size_bytes > max_read_bytes:
                    blockers.append("explicit_source_file_exceeds_max_bytes")
                else:
                    actual_file_read_attempted = True
                    raw = path.read_bytes()
                    actual_file_read_succeeded = True
                    payload_decode_attempted = True
                    payload = json.loads(raw.decode("utf-8"))
                    payload_decode_succeeded = True
                    payload_preview_keys = _preview_keys(payload)
                    schema_probe_checked = True
                    schema_probe_ok = isinstance(payload, Mapping) and bool(payload_preview_keys)
                    if not schema_probe_ok:
                        blockers.append("payload_schema_probe_not_mapping_or_empty")
            except Exception as exc:  # noqa: BLE001 - return bounded diagnostic only
                exception_class = exc.__class__.__name__
                exception_message = str(exc)[:240]
                if actual_file_read_attempted and not actual_file_read_succeeded:
                    blockers.append("actual_file_read_failed")
                elif payload_decode_attempted and not payload_decode_succeeded:
                    blockers.append("payload_decode_failed")
                else:
                    blockers.append("bounded_actual_source_probe_exception")

    ok = bool(
        allow_actual_read
        and explicit_ack == ALLOW_ACK
        and path_hint
        and path_exists_checked
        and path_exists
        and actual_file_read_attempted
        and actual_file_read_succeeded
        and payload_decode_attempted
        and payload_decode_succeeded
        and schema_probe_checked
        and schema_probe_ok
        and not blockers
    )
    return {
        "ok": ok,
        "probe_version": BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION,
        "probe_state": "bounded_actual_source_read_probe_succeeded" if ok else "bounded_actual_source_read_probe_blocked",
        "source_packet_id": source_packet,
        "source_artifact_ref_field": artifact_ref_field,
        "explicit_source_path_supplied": bool(path_hint),
        "explicit_ack_required": ALLOW_ACK,
        "explicit_ack_matched": explicit_ack == ALLOW_ACK,
        "allow_actual_read_requested": bool(allow_actual_read),
        "max_bytes": max_read_bytes,
        "path_exists_checked": path_exists_checked,
        "path_exists": path_exists,
        "observed_file_size_bytes": observed_file_size_bytes,
        "actual_file_read_attempted": actual_file_read_attempted,
        "actual_file_read_succeeded": actual_file_read_succeeded,
        "payload_decode_attempted": payload_decode_attempted,
        "payload_decode_succeeded": payload_decode_succeeded,
        "payload_type": type(payload).__name__ if payload is not None else "",
        "payload_preview_keys": payload_preview_keys,
        "payload_preview_key_count": len(payload_preview_keys),
        "schema_probe_checked": schema_probe_checked,
        "schema_probe_ok": schema_probe_ok,
        "blocker_reasons": blockers,
        "warning_reasons": warnings,
        "exception_class": exception_class,
        "exception_message": exception_message,
        "read_only": True,
        "non_executing": True,
        "bounded_actual_source_read_probe_only": True,
        "single_file_probe_only": True,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
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
