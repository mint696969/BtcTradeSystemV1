# path: ./btcts_next/src/btcts/apps/operator_ui/components/live_shell.py
# desc: Operator UI 全体で使う低ノイズ・固定骨格向けの共通 UI helper。

from __future__ import annotations

from typing import Callable, Literal, TypedDict
import json

import streamlit as st
import streamlit.components.v1 as components


PanelTone = Literal["neutral", "primary", "strong"]
ZoneKind = Literal["overview", "primary_live", "secondary", "diagnostics"]
WidgetTone = Literal["neutral", "primary", "strong", "danger"]
SlotRefreshMode = Literal["static", "poll_fast", "poll_normal", "poll_slow", "stream"]


class SlotMeta(TypedDict):
    page_id: str
    zone_id: str
    widget_id: str
    label: str | None
    tone: WidgetTone
    help_text: str | None
    refresh_mode: SlotRefreshMode
    priority: int
    overlay_enabled: bool
    partial_update_enabled: bool


def _inject_live_shell_styles() -> None:
    st.markdown(
        """
        <style>
        .live-shell-page-title {
            margin-top: 0.10rem;
            margin-bottom: 0.15rem;
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .live-shell-page-subtitle {
            margin-top: 0.00rem;
            margin-bottom: 0.45rem;
            color: rgba(250,250,250,0.72);
            font-size: 0.82rem;
            line-height: 1.2;
        }

        .live-shell-panel-label {
            margin-top: -0.15rem;
            margin-bottom: 0.45rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.15;
        }

        .live-shell-panel-label-neutral {
            color: rgba(250,250,250,0.78);
        }

        .live-shell-panel-label-primary {
            color: #93c5fd;
        }

        .live-shell-panel-label-strong {
            color: #fcd34d;
        }

        .live-shell-zone-title {
            margin-top: 0.00rem;
            margin-bottom: 0.35rem;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            line-height: 1.1;
            color: rgba(250,250,250,0.66);
            text-transform: uppercase;
        }

        .live-shell-widget-label {
            margin-top: -0.10rem;
            margin-bottom: 0.30rem;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.1;
        }

        .live-shell-widget-label-neutral {
            color: rgba(250,250,250,0.74);
        }

        .live-shell-widget-label-primary {
            color: #93c5fd;
        }

        .live-shell-widget-label-strong {
            color: #fcd34d;
        }

        .live-shell-widget-label-danger {
            color: #fca5a5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _panel_tone_class(tone: PanelTone) -> str:
    return {
        "neutral": "live-shell-panel-label-neutral",
        "primary": "live-shell-panel-label-primary",
        "strong": "live-shell-panel-label-strong",
    }.get(tone, "live-shell-panel-label-neutral")


def _widget_tone_class(tone: WidgetTone) -> str:
    return {
        "neutral": "live-shell-widget-label-neutral",
        "primary": "live-shell-widget-label-primary",
        "strong": "live-shell-widget-label-strong",
        "danger": "live-shell-widget-label-danger",
    }.get(tone, "live-shell-widget-label-neutral")


def render_compact_page_header(
    title: str,
    *,
    subtitle: str | None = None,
    help_text: str | None = None,
) -> None:
    _inject_live_shell_styles()

    if not help_text:
        st.markdown(
            f"<div class='live-shell-page-title'>{title}</div>",
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f"<div class='live-shell-page-subtitle'>{subtitle}</div>",
                unsafe_allow_html=True,
            )
        return

    header_cols = st.columns([12, 1])

    with header_cols[0]:
        st.markdown(
            f"<div class='live-shell-page-title'>{title}</div>",
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f"<div class='live-shell-page-subtitle'>{subtitle}</div>",
                unsafe_allow_html=True,
            )

    with header_cols[1]:
        with st.popover("ⓘ", use_container_width=True):
            st.caption(help_text)


def panel_container(
    label: str | None = None,
    *,
    tone: PanelTone = "neutral",
    help_text: str | None = None,
):
    _inject_live_shell_styles()

    container = st.container(border=True)

    with container:
        if label or help_text:
            tone_class = _panel_tone_class(tone)

            if not help_text:
                if label:
                    st.markdown(
                        (
                            "<div class='live-shell-panel-label "
                            f"{tone_class}'>{label}</div>"
                        ),
                        unsafe_allow_html=True,
                    )
                return container

            label_cols = st.columns([12, 1])

            with label_cols[0]:
                if label:
                    st.markdown(
                        (
                            "<div class='live-shell-panel-label "
                            f"{tone_class}'>{label}</div>"
                        ),
                        unsafe_allow_html=True,
                    )

            with label_cols[1]:
                with st.popover("ⓘ", use_container_width=True):
                    st.caption(help_text)

    return container


def render_zone_title(label: str) -> None:
    _inject_live_shell_styles()
    st.markdown(
        f"<div class='live-shell-zone-title'>{label}</div>",
        unsafe_allow_html=True,
    )


# zone_container は page 全体 rerun 中でも「どの領域が overview / primary_live / secondary / diagnostics か」
# を先に固定し、後段で widget / slot 単位更新へ差し替えるための境界として使う。


def zone_container(
    *,
    label: str | None = None,
    zone_kind: ZoneKind = "secondary",
    help_text: str | None = None,
):
    tone: PanelTone = {
        "overview": "strong",
        "primary_live": "primary",
        "secondary": "neutral",
        "diagnostics": "neutral",
    }.get(zone_kind, "neutral")

    if label:
        render_zone_title(label)

    return panel_container(label=None, tone=tone, help_text=help_text)


def widget_container(
    label: str | None = None,
    *,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
):
    _inject_live_shell_styles()

    container = st.container(border=False)

    with container:
        if label or help_text:
            tone_class = _widget_tone_class(tone)

            if not help_text:
                if label:
                    st.markdown(
                        (
                            "<div class='live-shell-widget-label "
                            f"{tone_class}'>{label}</div>"
                        ),
                        unsafe_allow_html=True,
                    )
                return container

            label_cols = st.columns([12, 1])

            with label_cols[0]:
                if label:
                    st.markdown(
                        (
                            "<div class='live-shell-widget-label "
                            f"{tone_class}'>{label}</div>"
                        ),
                        unsafe_allow_html=True,
                    )

            with label_cols[1]:
                with st.popover("ⓘ", use_container_width=True):
                    st.caption(help_text)

    return container


def responsive_columns(
    count: int,
    *,
    compact: bool = False,
):
    _inject_live_shell_styles()

    if count <= 1:
        return st.columns(1)

    if compact:
        return st.columns(count, gap="small")

    return st.columns(count)


def register_slot_meta(
    page_id: str,
    zone_id: str,
    widget_id: str,
    *,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
) -> str:
    slot_key = build_slot_key(page_id, zone_id, widget_id)
    slot_registry = st.session_state.setdefault("_live_shell_slot_registry", {})
    slot_registry[slot_key] = {
        "page_id": page_id,
        "zone_id": zone_id,
        "widget_id": widget_id,
        "refresh_mode": refresh_mode,
        "priority": priority,
        "overlay_enabled": overlay_enabled,
        "partial_update_enabled": partial_update_enabled,
    }
    return slot_key


def make_slot_meta(
    page_id: str,
    zone_id: str,
    widget_id: str,
    *,
    label: str | None = None,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
) -> SlotMeta:
    return {
        "page_id": page_id,
        "zone_id": zone_id,
        "widget_id": widget_id,
        "label": label,
        "tone": tone,
        "help_text": help_text,
        "refresh_mode": refresh_mode,
        "priority": priority,
        "overlay_enabled": overlay_enabled,
        "partial_update_enabled": partial_update_enabled,
    }


def _meta_str(meta: SlotMeta, key: str, default: str = "") -> str:
    value = meta.get(key)
    return value if isinstance(value, str) else default


def _meta_optional_str(meta: SlotMeta, key: str) -> str | None:
    value = meta.get(key)
    return value if isinstance(value, str) else None


def _meta_int(meta: SlotMeta, key: str, default: int = 0) -> int:
    value = meta.get(key)
    return value if isinstance(value, int) else default


def build_slot_key(
    page_id: str,
    zone_id: str,
    widget_id: str,
) -> str:
    return f"{page_id}:{zone_id}:{widget_id}"


def render_slot_anchor(
    page_id: str,
    zone_id: str,
    widget_id: str,
    *,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
):
    slot_key = register_slot_meta(
        page_id,
        zone_id,
        widget_id,
        refresh_mode=refresh_mode,
        priority=priority,
        overlay_enabled=overlay_enabled,
        partial_update_enabled=partial_update_enabled,
    )
    return st.container(key=slot_key)


def slot_widget_container(
    page_id: str,
    zone_id: str,
    widget_id: str,
    *,
    label: str | None = None,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
):
    slot = render_slot_anchor(
        page_id,
        zone_id,
        widget_id,
        refresh_mode=refresh_mode,
        priority=priority,
        overlay_enabled=overlay_enabled,
        partial_update_enabled=partial_update_enabled,
    )

    with slot:
        with widget_container(
            label=label,
            tone=tone,
            help_text=help_text,
        ):
            return slot


def slot_widget_from_meta(meta: SlotMeta):
    return slot_widget_container(
        _meta_str(meta, "page_id"),
        _meta_str(meta, "zone_id"),
        _meta_str(meta, "widget_id"),
        label=_meta_optional_str(meta, "label"),
        tone=_meta_str(meta, "tone", "neutral"),
        help_text=_meta_optional_str(meta, "help_text"),
        refresh_mode=_meta_str(meta, "refresh_mode", "static"),
        priority=_meta_int(meta, "priority", 0),
        overlay_enabled=bool(meta.get("overlay_enabled", False)),
        partial_update_enabled=bool(meta.get("partial_update_enabled", False)),
    )


def get_registered_slots(page_id: str | None = None) -> list[dict[str, str | int | bool | None]]:
    slot_registry = st.session_state.get("_live_shell_slot_registry", {})
    if not isinstance(slot_registry, dict):
        return []

    rows: list[dict] = []
    for slot_key, row in slot_registry.items():
        if not isinstance(row, dict):
            continue

        normalized = {
            "slot_key": slot_key,
            "page_id": row.get("page_id"),
            "zone_id": row.get("zone_id"),
            "widget_id": row.get("widget_id"),
            "refresh_mode": row.get("refresh_mode"),
            "priority": row.get("priority"),
            "overlay_enabled": row.get("overlay_enabled"),
            "partial_update_enabled": row.get("partial_update_enabled"),
        }
        rows.append(normalized)

    rows.sort(
        key=lambda row: (
            row.get("page_id") or "",
            row.get("priority") or 0,
            row.get("zone_id") or "",
            row.get("widget_id") or "",
        )
    )

    if page_id is None:
        return rows

    return [row for row in rows if row.get("page_id") == page_id]


def reset_registered_slots(page_id: str | None = None) -> None:
    slot_registry = st.session_state.get("_live_shell_slot_registry")
    if not isinstance(slot_registry, dict):
        st.session_state["_live_shell_slot_registry"] = {}
        return

    if page_id is None:
        st.session_state["_live_shell_slot_registry"] = {}
        return

    remove_keys = [
        slot_key
        for slot_key, row in slot_registry.items()
        if isinstance(row, dict) and row.get("page_id") == page_id
    ]
    for slot_key in remove_keys:
        slot_registry.pop(slot_key, None)


def page_supports_auto_refresh(page_id: str) -> bool:
    rows = get_registered_slots(page_id)
    return any(str(row.get("refresh_mode") or "static") != "static" for row in rows)


def refresh_mode_interval_sec(
    refresh_mode: str,
    *,
    default_sec: int = 15,
) -> int:
    mode = str(refresh_mode or "static")
    mapping = {
        "stream": 1,
        "poll_fast": 3,
        "poll_normal": 5,
        "poll_slow": 15,
        "static": default_sec,
    }
    return int(mapping.get(mode, default_sec))


def page_auto_refresh_interval_sec(
    page_id: str,
    *,
    default_sec: int = 15,
) -> int:
    rows = get_registered_slots(page_id)
    active_modes = [
        str(row.get("refresh_mode") or "static")
        for row in rows
        if str(row.get("refresh_mode") or "static") != "static"
    ]
    if not active_modes:
        return int(default_sec)

    return min(
        refresh_mode_interval_sec(mode, default_sec=default_sec)
        for mode in active_modes
    )


def resolve_page_refresh_plan(
    *,
    page_key: str,
    ui_auto_refresh: bool,
    ui_refresh_interval_sec: int,
    fragment_supported: bool | None = None,
) -> dict[str, bool | int]:
    is_slot_refresh_target = page_supports_auto_refresh(page_key)

    supports_fragment = (
        supports_streamlit_fragment()
        if fragment_supported is None
        else bool(fragment_supported)
    )

    is_fragment_refresh_target = (
        page_key == "health"
        and supports_fragment
        and is_slot_refresh_target
    )
    is_page_auto_refresh_target = page_key == "logs" or (
        is_slot_refresh_target and not is_fragment_refresh_target
    )

    effective_refresh_interval_sec = int(ui_refresh_interval_sec)
    if is_slot_refresh_target:
        slot_recommended_interval_sec = page_auto_refresh_interval_sec(
            page_key,
            default_sec=effective_refresh_interval_sec,
        )
        effective_refresh_interval_sec = min(
            effective_refresh_interval_sec,
            int(slot_recommended_interval_sec),
        )

    refresh_status_visible = bool(
        ui_auto_refresh and (
            is_page_auto_refresh_target or is_fragment_refresh_target
        )
    )

    return {
        "slot_refresh_target": is_slot_refresh_target,
        "fragment_refresh_target": is_fragment_refresh_target,
        "page_auto_refresh_target": is_page_auto_refresh_target,
        "page_reload_enabled": bool(ui_auto_refresh and is_page_auto_refresh_target),
        "fragment_refresh_enabled": bool(ui_auto_refresh and is_fragment_refresh_target),
        "refresh_status_visible": refresh_status_visible,
        "effective_refresh_interval_sec": effective_refresh_interval_sec,
    }


def supports_streamlit_fragment() -> bool:
    return callable(getattr(st, "fragment", None))


def render_fragment_block(
    render_body: Callable[[], None],
    *,
    enabled: bool = True,
    refresh_mode: str = "static",
    default_sec: int = 15,
) -> None:
    use_fragment = (
        enabled
        and str(refresh_mode or "static") != "static"
        and supports_streamlit_fragment()
    )

    if not use_fragment:
        render_body()
        return

    interval_sec = refresh_mode_interval_sec(
        str(refresh_mode or "static"),
        default_sec=default_sec,
    )
    fragment = getattr(st, "fragment")

    @fragment(run_every=f"{int(interval_sec)}s")
    def _fragment_runner() -> None:
        render_body()

    _fragment_runner()


def render_fragment_slot(
    meta: SlotMeta,
    render_body: Callable[[], None],
    *,
    enabled: bool = True,
    default_sec: int = 15,
) -> None:
    refresh_mode = _meta_str(meta, "refresh_mode", "static")

    def _render_slot() -> None:
        with slot_widget_from_meta(meta):
            render_body()

    render_fragment_block(
        _render_slot,
        enabled=enabled,
        refresh_mode=refresh_mode,
        default_sec=default_sec,
    )


def render_page_auto_refresh(
    *,
    enabled: bool,
    interval_sec: int,
    page_key: str,
) -> None:
    interval_ms = max(1000, int(interval_sec) * 1000)

    payload = {
        "enabled": bool(enabled),
        "interval_ms": interval_ms,
        "page_key": str(page_key),
    }

    components.html(
        f"""
        <script>
        const config = {json.dumps(payload)};
        const parentWindow = window.parent;

        if (!parentWindow) {{
            return;
        }}

        const timerKey = "__btcts_auto_refresh_timer__";
        const pageKeyKey = "__btcts_auto_refresh_page_key__";

        if (parentWindow[timerKey]) {{
            parentWindow.clearTimeout(parentWindow[timerKey]);
            parentWindow[timerKey] = null;
        }}

        if (!config.enabled) {{
            parentWindow[pageKeyKey] = null;
            return;
        }}

        parentWindow[pageKeyKey] = config.page_key;
        parentWindow[timerKey] = parentWindow.setTimeout(() => {{
            if (parentWindow[pageKeyKey] === config.page_key) {{
                parentWindow.location.reload();
            }}
        }}, config.interval_ms);
        </script>
        """,
        height=0,
        width=0,
    )


def render_folded_section(
    label: str,
    *,
    expanded: bool = False,
):
    _inject_live_shell_styles()
    return st.expander(label, expanded=expanded)