# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_preview_status_display.py
# desc: Read-only Operator/UI display packet for AutoTradePredictionPreviewStatus. No Streamlit rendering, runtime wiring, writes, commands, mode apply, grant execution, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.autotrade.prediction_preview_status import AutoTradePredictionPreviewStatus

AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT = {
    "section_type": "autotrade_prediction_preview_status_display_packet",
    "source_type": "autotrade_prediction_preview_status",
    "dashboard_role": "operator_ui_read_only_display",
    "read_only_contract": True,
    "non_executing": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
    "would_append_shadow_decision": False,
    "would_apply_mode": False,
    "would_execute_prearmed_grant": False,
    "would_write_runtime_artifact": False,
    "would_send_to_broker": False,
    "broker_execution_requested": False,
    "mode_apply_requested": False,
    "command_ledger_append_requested": False,
    "approval_append_requested": False,
}


def _payload(status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> dict[str, Any]:
    if status is None:
        return {}
    if isinstance(status, Mapping):
        return dict(status)
    return status.to_dict()


def _text(value: Any, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def _severity(state: str) -> str:
    if state == "ok":
        return "ok"
    if state == "review":
        return "review"
    if state == "blocked":
        return "blocked"
    return "unavailable"


def prediction_preview_status_compact_line(status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> str:
    data = _payload(status)
    if not data:
        return "prediction_preview_status unavailable / display_only"
    return (
        "prediction_preview_status="
        f"{_text(data.get('status_state'))} / "
        f"action={_text(data.get('preview_action'))} / "
        f"bias={_text(data.get('preview_bias'))} / "
        f"confidence={_text(data.get('preview_confidence'))} / "
        f"readiness={_text(data.get('readiness_state'))} / display_only"
    )


def prediction_preview_status_snapshot_lines(status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None) -> tuple[str, ...]:
    data = _payload(status)
    if not data:
        return (
            "status_available=false",
            "display_state=unavailable",
            "read_only_contract=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
            "no_command_buttons=true",
        )

    blockers = tuple(str(item) for item in data.get("blockers") or ())
    warnings = tuple(str(item) for item in data.get("warnings") or ())
    weak_families = tuple(str(item) for item in data.get("weak_families") or ())
    lines = [
        "status_available=true",
        "display_state=" + _severity(_text(data.get("status_state"), "unavailable")),
        "status_id=" + _text(data.get("status_id")),
        "generated_at=" + _text(data.get("generated_at")),
        "preview_id=" + _text(data.get("preview_id")),
        "readiness_id=" + _text(data.get("readiness_id")),
        "readiness_state=" + _text(data.get("readiness_state")),
        "intended_mode=" + _text(data.get("intended_mode")),
        "preview_action=" + _text(data.get("preview_action")),
        "preview_bias=" + _text(data.get("preview_bias")),
        "preview_confidence=" + _text(data.get("preview_confidence")),
        "validation_state=" + _text(data.get("validation_state")),
        "average_score=" + _text(data.get("average_score")),
        "label_hit_rate=" + _text(data.get("label_hit_rate")),
        "weak_families=" + ",".join(weak_families),
        "blocker_count=" + str(len(blockers)),
        "warning_count=" + str(len(warnings)),
        "read_only=" + _bool_token(data.get("read_only")),
        "non_executing=" + _bool_token(data.get("non_executing")),
        "would_append_shadow_decision=" + _bool_token(data.get("would_append_shadow_decision")),
        "would_apply_mode=" + _bool_token(data.get("would_apply_mode")),
        "would_execute_prearmed_grant=" + _bool_token(data.get("would_execute_prearmed_grant")),
        "would_write_runtime_artifact=" + _bool_token(data.get("would_write_runtime_artifact")),
        "would_send_to_broker=" + _bool_token(data.get("would_send_to_broker")),
        "broker_execution_requested=" + _bool_token(data.get("broker_execution_requested")),
        "mode_apply_requested=" + _bool_token(data.get("mode_apply_requested")),
        "command_ledger_append_requested=" + _bool_token(data.get("command_ledger_append_requested")),
        "approval_append_requested=" + _bool_token(data.get("approval_append_requested")),
        "read_only_contract=true",
        "not_runtime_wiring=true",
        "not_ui_rendering=true",
        "no_command_buttons=true",
    ]
    if blockers:
        lines.append("blockers=" + ",".join(blockers))
    if warnings:
        lines.append("warnings=" + ",".join(warnings))
    return tuple(lines)


def build_autotrade_prediction_preview_status_display_packet(
    status: AutoTradePredictionPreviewStatus | Mapping[str, Any] | None,
) -> dict[str, Any]:
    data = _payload(status)
    status_state = _text(data.get("status_state"), "unavailable") if data else "unavailable"
    blockers = tuple(str(item) for item in data.get("blockers") or ()) if data else ()
    warnings = tuple(str(item) for item in data.get("warnings") or ()) if data else ()
    weak_families = tuple(str(item) for item in data.get("weak_families") or ()) if data else ()
    return {
        **AUTOTRADE_PREDICTION_PREVIEW_STATUS_DISPLAY_CONTRACT,
        "status_available": bool(data),
        "display_state": _severity(status_state),
        "status_state": status_state,
        "status_id": data.get("status_id") if data else None,
        "generated_at": data.get("generated_at") if data else None,
        "preview_id": data.get("preview_id") if data else None,
        "readiness_id": data.get("readiness_id") if data else None,
        "readiness_state": data.get("readiness_state") if data else None,
        "intended_mode": data.get("intended_mode") if data else None,
        "preview_action": data.get("preview_action") if data else None,
        "preview_bias": data.get("preview_bias") if data else None,
        "preview_confidence": data.get("preview_confidence") if data else None,
        "validation_state": data.get("validation_state") if data else None,
        "average_score": data.get("average_score") if data else None,
        "label_hit_rate": data.get("label_hit_rate") if data else None,
        "weak_families": weak_families,
        "blockers": blockers,
        "warnings": warnings,
        "compact_line": prediction_preview_status_compact_line(status),
        "snapshot_lines": prediction_preview_status_snapshot_lines(status),
    }
