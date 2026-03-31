# path: ./btcts_next/src/btcts/apps/operator_ui/components/live_shell.py
# desc: Operator UI 全体で使う低ノイズ・固定骨格向けの共通 UI helper。

from __future__ import annotations

from typing import Literal

import streamlit as st


PanelTone = Literal["neutral", "primary", "strong"]
ZoneKind = Literal["overview", "primary_live", "secondary", "diagnostics"]
WidgetTone = Literal["neutral", "primary", "strong", "danger"]
SlotRefreshMode = Literal["static", "poll_fast", "poll_normal", "poll_slow", "stream"]
SlotMeta = dict[str, str | int | None]


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
) -> str:
    slot_key = build_slot_key(page_id, zone_id, widget_id)
    slot_registry = st.session_state.setdefault("_live_shell_slot_registry", {})
    slot_registry[slot_key] = {
        "page_id": page_id,
        "zone_id": zone_id,
        "widget_id": widget_id,
        "refresh_mode": refresh_mode,
        "priority": priority,
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
):
    slot_key = register_slot_meta(
        page_id,
        zone_id,
        widget_id,
        refresh_mode=refresh_mode,
        priority=priority,
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
):
    slot = render_slot_anchor(
        page_id,
        zone_id,
        widget_id,
        refresh_mode=refresh_mode,
        priority=priority,
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
    )


def get_registered_slots(page_id: str | None = None) -> list[dict]:
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


def render_folded_section(
    label: str,
    *,
    expanded: bool = False,
):
    _inject_live_shell_styles()
    return st.expander(label, expanded=expanded)