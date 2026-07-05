# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/compact_layout_view.py
# desc: Compact WarRoom v2 viewport layout helpers. Keeps warroom_v2_page.py thin and policy-free.

from __future__ import annotations

from typing import Any

COMPACT_VIEWPORT_LAYOUT_VERSION = "warroom_v2_compact_viewport_layout.2026_07_05.v1"

SECTION_LABELS: tuple[str, ...] = (
    "1. Market strip",
    "2. Trade strip",
    "3. Inference scenario guidance — deferred compact review",
    "4. Prediction cards — deferred to next thread",
    "5. Bottom chart",
)


def render_compact_page_header(st_api: Any) -> dict[str, Any]:
    st_api.subheader("WarRoom v2 / Realtime Cockpit")
    st_api.caption("compact viewport / D-hot live observation / section-fragment refresh / no page reload / no broker")
    return {"ok": True, "compact_viewport_layout_version": COMPACT_VIEWPORT_LAYOUT_VERSION, "header_rendered": True}


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
