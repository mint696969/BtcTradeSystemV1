# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/compact_layout_view.py
# desc: Compact WarRoom v2 viewport layout helpers. Keeps warroom_v2_page.py thin and policy-free.

from __future__ import annotations

import html
from typing import Any, Mapping, Sequence

COMPACT_VIEWPORT_LAYOUT_VERSION = "warroom_v2_compact_viewport_layout.2026_07_05.v1"

SECTION_LABELS: tuple[str, ...] = (
    "1. Market strip",
    "2. Trade strip",
    "3. Inference scenario guidance — deferred compact review",
    "4. Prediction cards — deferred to next thread",
    "5. Bottom chart",
)

_BADGE_STYLE_BY_TONE: dict[str, str] = {
    "green": "background:rgba(34,197,94,0.14);border-color:rgba(34,197,94,0.32);color:#15803d;",
    "yellow": "background:rgba(245,158,11,0.15);border-color:rgba(245,158,11,0.34);color:#92400e;",
    "red": "background:rgba(239,68,68,0.14);border-color:rgba(239,68,68,0.32);color:#b91c1c;",
    "gray": "background:rgba(100,116,139,0.10);border-color:rgba(100,116,139,0.24);color:#475569;",
}


def _status_badge_html(badge: Mapping[str, object]) -> str:
    label = html.escape(str(badge.get("label") or "-"))
    tone = str(badge.get("tone") or "gray")
    style = _BADGE_STYLE_BY_TONE.get(tone, _BADGE_STYLE_BY_TONE["gray"])
    return (
        f"<span style='display:inline-flex;align-items:center;gap:0.25rem;"
        f"padding:0.12rem 0.42rem;border:1px solid;border-radius:999px;"
        f"font-size:0.74rem;font-weight:750;line-height:1.05;white-space:nowrap;"
        f"{style}'>{label}</span>"
    )


def render_compact_page_header(st_api: Any, *, status_badges: Sequence[Mapping[str, object]] | None = None) -> dict[str, Any]:
    if status_badges:
        badges_html = "".join(_status_badge_html(badge) for badge in status_badges)
        st_api.markdown(
            "<div style='display:flex;align-items:center;gap:0.78rem;flex-wrap:wrap;margin:0.50rem 0 0.42rem 0;'>"
            "<div style='font-size:1.40rem;font-weight:800;line-height:1.12;color:rgba(49,51,63,0.88);'>War Room</div>"
            f"<div style='display:flex;align-items:center;gap:0.32rem;flex-wrap:wrap;'>{badges_html}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st_api.subheader("War Room")
    return {"ok": True, "compact_viewport_layout_version": COMPACT_VIEWPORT_LAYOUT_VERSION, "header_rendered": True, "status_badges_rendered": bool(status_badges)}


def render_compact_section_label(st_api: Any, *, index: int, title: str, note: str = "") -> dict[str, Any]:
    suffix = f" / {note}" if note else ""
    label = f"{index}. {title}{suffix}"
    st_api.caption(label)
    return {"ok": True, "section_index": index, "section_title": title, "label": label, "compact_label_rendered": True}


def compact_footer_caption() -> str:
    return " / ".join(
        [
            f"compact_viewport_layout=true:{COMPACT_VIEWPORT_LAYOUT_VERSION}",
            "scenario_cards_deferred_collapsed=true",
            "rt_visible_mount_ready=true",
            "rt_polish3_cockpit_layout_ready=true",
            "rt_section_fragment_refresh_ready=true",
            "page_reload_enabled=false",
            "websocket_send_enabled=false",
            "broker_send_enabled=false",
            "order_intent_submitted=false",
            "prediction_invoked=false",
            "classifier_invoked=false",
        ]
    )
