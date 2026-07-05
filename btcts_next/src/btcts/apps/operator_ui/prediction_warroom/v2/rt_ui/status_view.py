# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/status_view.py
# desc: Compact WarRoom v2 RT runtime status renderer with entry-gate safety status.

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
    return "stale", "🟠"


def _render_boundary_caption(st_api: Any, runtime_status: Mapping[str, Any]) -> None:
    st_api.caption(
        " / ".join(
            [
                f"entry_gate={ENTRY_GATE_VERSION}",
                "manual_review_only=true",
                "autotrade_resume_authorized=false",
                "websocket_send_enabled=false",
                "broker_send_enabled=false",
                f"order_intent_submitted={_bool_label(runtime_status.get('order_intent_submitted'))}",
                f"ledger_append_allowed={_bool_label(runtime_status.get('ledger_append_allowed'))}",
                f"prediction_invoked={_bool_label(runtime_status.get('prediction_invoked'))}",
                f"classifier_invoked={_bool_label(runtime_status.get('classifier_invoked'))}",
            ]
        )
    )


def render_rt_runtime_status(runtime_status: Mapping[str, Any], bridge_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    receiver_started = bool(runtime_status.get("receiver_runtime_started"))
    receive_loop = bool(runtime_status.get("receive_loop_started"))
    socket_opened = bool(runtime_status.get("socket_opened") or runtime_status.get("websocket_opened"))
    messages_applied = _safe_int(bridge_packet.get("messages_applied"), 0)
    drained = _safe_int(runtime_status.get("drained_message_count") or runtime_status.get("last_drain_count"), 0)
    pending = _safe_int(runtime_status.get("pending_message_count"), 0)
    received = _safe_int(runtime_status.get("received_message_count"), 0)
    age_ms = _age_ms(runtime_status)
    freshness, icon = _freshness_from_age(age_ms, connected=bool(socket_opened or receive_loop or receiver_started), messages_applied=messages_applied)

    c1, c2, c3, c4, c5 = st_api.columns(5)
    c1.metric("Runtime", "connected" if receiver_started else "waiting")
    c2.metric("Push lane", f"{icon} {freshness}")
    c3.metric("Received", received)
    c4.metric("Drained", drained)
    c5.metric("Applied", messages_applied)

    endpoint_label = "D-hot" if str(runtime_status.get("endpoint_url_present")) == "True" or runtime_status.get("endpoint_url_present") else "not configured"
    latest_label = f"{age_ms / 1000:.1f}s ago" if age_ms is not None else "unknown"
    st_api.caption(
        " / ".join(
            [
                f"endpoint={endpoint_label}",
                f"receiver_runtime_started={receiver_started}",
                f"socket_opened={socket_opened}",
                f"receive_loop_started={receive_loop}",
                f"pending={pending}",
                f"latest_message_age={latest_label}",
            ]
        )
    )

    if freshness == "stale":
        st_api.warning("Push lane is stale. Treat visible widget values as last-known read-only context until the next live packet arrives.")
    elif freshness == "attention":
        st_api.info("Push lane has not updated in the short attention window. This is observation-only and does not authorize action.")

    error = runtime_status.get("receiver_error")
    if isinstance(error, Mapping) and error:
        st_api.warning(f"receiver_error={error.get('error_type')}: {error.get('error_message')}")

    _render_boundary_caption(st_api, runtime_status)
    return {
        "ok": True,
        "entry_gate_version": ENTRY_GATE_VERSION,
        "receiver_started": receiver_started,
        "socket_opened": socket_opened,
        "receive_loop_started": receive_loop,
        "freshness": freshness,
        "latest_message_age_ms": age_ms,
        "messages_applied": messages_applied,
        "read_only": True,
        "manual_review_only": True,
        "autotrade_resume_authorized": False,
        "websocket_send_enabled": False,
        "broker_send_enabled": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }
