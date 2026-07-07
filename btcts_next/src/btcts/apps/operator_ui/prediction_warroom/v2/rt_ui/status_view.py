# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/status_view.py
# desc: Compact WarRoom v2 RT runtime status renderer with top badges and bottom diagnostics.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"


def _bool_label(value: object) -> str:
    return "true" if bool(value) else "false"


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _age_ms(runtime_status: Mapping[str, Any]) -> int | None:
    latest_ms = _safe_int(runtime_status.get("latest_message_at_ms"), 0)
    if latest_ms <= 0:
        return None
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return max(0, now_ms - latest_ms)


def _freshness_from_age(age_ms: int | None, *, connected: bool, messages_applied: int) -> tuple[str, str]:
    if not connected and messages_applied <= 0:
        return "waiting", "⚪"
    if age_ms is None:
        return ("receiving", "🟢") if messages_applied > 0 else ("waiting", "⚪")
    if age_ms <= 15_000:
        return "live", "🟢"
    if age_ms <= 60_000:
        return "attention", "🟡"
    return "stale", "🔴"


def _freshness_tone(freshness: str) -> str:
    if freshness in {"live", "receiving"}:
        return "green"
    if freshness == "attention":
        return "yellow"
    if freshness == "stale":
        return "red"
    return "gray"


def _age_tone(age_ms: int | None, *, connected: bool, messages_applied: int) -> str:
    if age_ms is None:
        return "gray" if not connected and messages_applied <= 0 else "yellow"
    if age_ms <= 15_000:
        return "green"
    if age_ms <= 60_000:
        return "yellow"
    return "red"


def _format_age(age_ms: int | None) -> str:
    return f"age {age_ms / 1000:.1f}s" if age_ms is not None else "age unknown"


def build_rt_runtime_status_view_model(
    runtime_status: Mapping[str, Any],
    bridge_packet: Mapping[str, Any],
    *,
    display_source: str = "unknown",
    auto_refresh_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    receiver_started = bool(runtime_status.get("receiver_runtime_started"))
    receive_loop = bool(runtime_status.get("receive_loop_started"))
    socket_opened = bool(runtime_status.get("socket_opened") or runtime_status.get("websocket_opened"))
    connected = bool(socket_opened or receive_loop or receiver_started)
    messages_applied = _safe_int(bridge_packet.get("messages_applied"), 0)
    drained = _safe_int(runtime_status.get("drained_message_count") or runtime_status.get("last_drain_count"), 0)
    pending = _safe_int(runtime_status.get("pending_message_count"), 0)
    received = _safe_int(runtime_status.get("received_message_count"), 0)
    age_ms = _age_ms(runtime_status)
    freshness, icon = _freshness_from_age(age_ms, connected=connected, messages_applied=messages_applied)
    endpoint_label = "D-hot" if str(runtime_status.get("endpoint_url_present")) == "True" or runtime_status.get("endpoint_url_present") else "not configured"
    latest_label = f"{age_ms / 1000:.1f}s ago" if age_ms is not None else "unknown"
    broker_enabled = bool(runtime_status.get("broker_send_enabled"))
    prediction_invoked = bool(runtime_status.get("prediction_invoked"))
    classifier_invoked = bool(runtime_status.get("classifier_invoked"))
    auto_refresh = dict(auto_refresh_packet or {})
    auto_enabled = bool(auto_refresh.get("auto_refresh_enabled"))
    interval_ms = _safe_int(auto_refresh.get("interval_ms"), 3000)

    badges = [
        {"label": "Runtime connected" if receiver_started else "Runtime waiting", "tone": "green" if receiver_started else "yellow"},
        {"label": f"{icon} Push {freshness}", "tone": _freshness_tone(freshness)},
        {"label": f"recv {received}", "tone": "green" if received > 0 else "gray"},
        {"label": f"applied {messages_applied}", "tone": "green" if messages_applied > 0 else "gray"},
        {"label": f"pending {pending}", "tone": "green" if pending == 0 else ("yellow" if pending < 100 else "red")},
        {"label": _format_age(age_ms), "tone": _age_tone(age_ms, connected=connected, messages_applied=messages_applied)},
        {"label": "broker ON" if broker_enabled else "broker OFF", "tone": "red" if broker_enabled else "gray"},
        {"label": "prediction ON" if prediction_invoked else "prediction OFF", "tone": "red" if prediction_invoked else "gray"},
    ]

    diagnostics = [
        "compact viewport / D-hot live observation / section-fragment refresh / no page reload / no broker",
        " / ".join(
            [
                f"endpoint={endpoint_label}",
                f"receiver_runtime_started={receiver_started}",
                f"socket_opened={socket_opened}",
                f"receive_loop_started={receive_loop}",
                f"pending={pending}",
                f"latest_message_age={latest_label}",
            ]
        ),
        " / ".join(
            [
                f"entry_gate={ENTRY_GATE_VERSION}",
                "manual_review_only=true",
                "autotrade_resume_authorized=false",
                "websocket_send_enabled=false",
                f"broker_send_enabled={_bool_label(broker_enabled)}",
                f"order_intent_submitted={_bool_label(runtime_status.get('order_intent_submitted'))}",
                f"ledger_append_allowed={_bool_label(runtime_status.get('ledger_append_allowed'))}",
                f"prediction_invoked={_bool_label(prediction_invoked)}",
                f"classifier_invoked={_bool_label(classifier_invoked)}",
            ]
        ),
        " / ".join(
            [
                f"cockpit_auto_refresh={'on' if auto_enabled else 'off'}",
                f"interval_ms={interval_ms}",
                "transport=streamlit_section_fragment_refresh",
                "page_reload_enabled=false",
                "broker_send_enabled=false",
                "prediction_invoked=false",
            ]
        ),
        f"display_source={display_source} / fallback_sample_suppressed=true / rt_section_fragment_refresh_ready=true",
    ]

    return {
        "ok": True,
        "badges": badges,
        "diagnostic_lines": diagnostics,
        "entry_gate_version": ENTRY_GATE_VERSION,
        "receiver_started": receiver_started,
        "socket_opened": socket_opened,
        "receive_loop_started": receive_loop,
        "freshness": freshness,
        "latest_message_age_ms": age_ms,
        "messages_applied": messages_applied,
        "received_message_count": received,
        "drained_message_count": drained,
        "pending_message_count": pending,
        "read_only": True,
        "manual_review_only": True,
        "autotrade_resume_authorized": False,
        "websocket_send_enabled": False,
        "broker_send_enabled": broker_enabled,
        "prediction_invoked": prediction_invoked,
        "classifier_invoked": classifier_invoked,
    }


def render_rt_runtime_status(
    runtime_status: Mapping[str, Any],
    bridge_packet: Mapping[str, Any],
    st_api: Any,
    *,
    view_model: Mapping[str, Any] | None = None,
    render_badges: bool = True,
) -> dict[str, Any]:
    model = dict(view_model or build_rt_runtime_status_view_model(runtime_status, bridge_packet))

    if render_badges:
        # The header normally owns badge rendering. This fallback keeps the renderer useful in isolation.
        from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.compact_layout_view import render_compact_page_header

        render_compact_page_header(st_api, status_badges=model.get("badges") or [])

    freshness = str(model.get("freshness") or "unknown")
    if freshness == "stale":
        st_api.warning("Push lane is stale. Treat visible widget values as last-known read-only context until the next live packet arrives.")
    elif freshness == "attention":
        st_api.info("Push lane has not updated in the short attention window. This is observation-only and does not authorize action.")

    error = runtime_status.get("receiver_error")
    if isinstance(error, Mapping) and error:
        st_api.warning(f"receiver_error={error.get('error_type')}: {error.get('error_message')}")

    return model


def render_rt_runtime_diagnostics(
    view_model: Mapping[str, Any],
    st_api: Any,
) -> dict[str, Any]:
    lines = [str(line) for line in (view_model.get("diagnostic_lines") or ())]
    for line in lines:
        st_api.caption(line)
    return {"ok": True, "runtime_diagnostics_rendered": True, "line_count": len(lines)}
