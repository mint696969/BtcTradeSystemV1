# path: ./btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py
# desc: Operator UI の slot metadata 定義レイヤ。page/component 直書きから段階的に寄せる共通入口。

from __future__ import annotations

from btcts.apps.operator_ui.components.live_shell import (
    SlotMeta,
    WidgetTone,
    SlotRefreshMode,
    make_slot_meta,
)


def slot_def(
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
    return make_slot_meta(
        page_id,
        zone_id,
        widget_id,
        label=label,
        tone=tone,
        help_text=help_text,
        refresh_mode=refresh_mode,
        priority=priority,
    )


def warroom_slot(
    zone_id: str,
    widget_id: str,
    *,
    label: str | None = None,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
) -> SlotMeta:
    return slot_def(
        "warroom",
        zone_id,
        widget_id,
        label=label,
        tone=tone,
        help_text=help_text,
        refresh_mode=refresh_mode,
        priority=priority,
    )


def health_slot(
    zone_id: str,
    widget_id: str,
    *,
    label: str | None = None,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
) -> SlotMeta:
    return slot_def(
        "health",
        zone_id,
        widget_id,
        label=label,
        tone=tone,
        help_text=help_text,
        refresh_mode=refresh_mode,
        priority=priority,
    )


def collector_slot(
    zone_id: str,
    widget_id: str,
    *,
    label: str | None = None,
    tone: WidgetTone = "neutral",
    help_text: str | None = None,
    refresh_mode: SlotRefreshMode = "static",
    priority: int = 0,
) -> SlotMeta:
    return slot_def(
        "collector",
        zone_id,
        widget_id,
        label=label,
        tone=tone,
        help_text=help_text,
        refresh_mode=refresh_mode,
        priority=priority,
    )