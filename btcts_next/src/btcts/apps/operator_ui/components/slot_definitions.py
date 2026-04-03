# path: ./btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py
# desc: Operator UI の slot metadata 定義レイヤ。page/component 直書きから段階的に寄せる共通入口。

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.components.live_shell import (
    SlotMeta,
    WidgetTone,
    SlotRefreshMode,
    make_slot_meta,
)


class WidgetContract(TypedDict, total=False):
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


class WidgetLayoutHints(TypedDict, total=False):
    zone_id: str
    preferred_w: int
    preferred_h: int
    min_w: int
    min_h: int


def build_layout_hints(
    *,
    zone_id: str,
    preferred_w: int | None = None,
    preferred_h: int | None = None,
    min_w: int | None = None,
    min_h: int | None = None,
) -> WidgetLayoutHints:
    hints: WidgetLayoutHints = {
        "zone_id": zone_id,
    }
    if preferred_w is not None:
        hints["preferred_w"] = preferred_w
    if preferred_h is not None:
        hints["preferred_h"] = preferred_h
    if min_w is not None:
        hints["min_w"] = min_w
    if min_h is not None:
        hints["min_h"] = min_h
    return hints


class WidgetOverlayContract(TypedDict, total=False):
    enabled: bool
    base_series: list[str]
    overlay_series: list[str]
    threshold_lines: list[str]
    event_markers: list[str]


class WidgetRefreshPolicy(TypedDict, total=False):
    mode: SlotRefreshMode
    partial_update_enabled: bool
    chart_sensitive: bool
    rerender_scope: str
    notes: str | None


def build_overlay_contract(
    *,
    enabled: bool = False,
    base_series: list[str] | None = None,
    overlay_series: list[str] | None = None,
    threshold_lines: list[str] | None = None,
    event_markers: list[str] | None = None,
) -> WidgetOverlayContract:
    return {
        "enabled": enabled,
        "base_series": list(base_series or []),
        "overlay_series": list(overlay_series or []),
        "threshold_lines": list(threshold_lines or []),
        "event_markers": list(event_markers or []),
    }


def build_refresh_policy(
    *,
    mode: SlotRefreshMode = "static",
    partial_update_enabled: bool = False,
    chart_sensitive: bool = False,
    rerender_scope: str = "page",
    notes: str | None = None,
) -> WidgetRefreshPolicy:
    return {
        "mode": mode,
        "partial_update_enabled": partial_update_enabled,
        "chart_sensitive": chart_sensitive,
        "rerender_scope": rerender_scope,
        "notes": notes,
    }


def build_widget_contract(
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
) -> WidgetContract:
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
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
) -> SlotMeta:
    contract = build_widget_contract(
        page_id,
        zone_id,
        widget_id,
        label=label,
        tone=tone,
        help_text=help_text,
        refresh_mode=refresh_mode,
        priority=priority,
        overlay_enabled=overlay_enabled,
        partial_update_enabled=partial_update_enabled,
    )
    return make_slot_meta(
        contract["page_id"],
        contract["zone_id"],
        contract["widget_id"],
        label=contract.get("label"),
        tone=contract.get("tone", "neutral"),
        help_text=contract.get("help_text"),
        refresh_mode=contract.get("refresh_mode", "static"),
        priority=contract.get("priority", 0),
        overlay_enabled=contract.get("overlay_enabled", False),
        partial_update_enabled=contract.get("partial_update_enabled", False),
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
    overlay_enabled: bool = False,
    partial_update_enabled: bool = False,
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
        overlay_enabled=overlay_enabled,
        partial_update_enabled=partial_update_enabled,
    )


def warroom_graph_overlay_contract(widget_id: str) -> WidgetOverlayContract:
    overlay_map: dict[str, WidgetOverlayContract] = {
        "market_monitor": build_overlay_contract(
            enabled=True,
            base_series=["mid_price"],
            overlay_series=["best_bid", "best_ask"],
            threshold_lines=[],
            event_markers=[],
        ),
        "trade_flow_monitor": build_overlay_contract(
            enabled=True,
            base_series=["trade_flow"],
            overlay_series=[],
            threshold_lines=["zero_line"],
            event_markers=[],
        ),
        "liquidity_pressure": build_overlay_contract(
            enabled=True,
            base_series=["liquidity_pressure"],
            overlay_series=[],
            threshold_lines=["neutral_band"],
            event_markers=[],
        ),
    }
    return overlay_map.get(widget_id, build_overlay_contract(enabled=False))


def warroom_overlay_enabled(widget_id: str) -> bool:
    return bool(warroom_graph_overlay_contract(widget_id).get("enabled"))


def warroom_overlay_widget_ids() -> list[str]:
    return [
        "market_monitor",
        "trade_flow_monitor",
        "liquidity_pressure",
    ]


def warroom_overlay_contract_count() -> int:
    return len(warroom_overlay_widget_ids())


def warroom_partial_update_widget_ids() -> list[str]:
    return [
        "market_monitor",
        "trade_flow_monitor",
        "liquidity_pressure",
    ]


def warroom_partial_update_enabled(widget_id: str) -> bool:
    return widget_id in set(warroom_partial_update_widget_ids())


def warroom_refresh_policy(widget_id: str) -> WidgetRefreshPolicy:
    if widget_id == "market_monitor":
        return build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="first candidate for fragment/partial redraw validation",
        )
    if widget_id == "trade_flow_monitor":
        return build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="trade count and delta update frequently",
        )
    if widget_id == "liquidity_pressure":
        return build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="orderbook-derived pressure changes frequently",
        )
    return build_refresh_policy()


def warroom_chart_sensitive(widget_id: str) -> bool:
    return bool(warroom_refresh_policy(widget_id).get("chart_sensitive"))


def warroom_chart_sensitive_widget_ids() -> list[str]:
    return [
        widget_id
        for widget_id in warroom_overlay_widget_ids()
        if warroom_chart_sensitive(widget_id)
    ]


def warroom_chart_sensitive_count() -> int:
    return len(warroom_chart_sensitive_widget_ids())


def warroom_refresh_mode_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for widget_id in warroom_overlay_widget_ids():
        mode = str(warroom_refresh_policy(widget_id).get("mode", "static"))
        counts[mode] = counts.get(mode, 0) + 1
    return counts


def warroom_widget_refresh_mode(widget_id: str) -> SlotRefreshMode:
    mode = warroom_refresh_policy(widget_id).get("mode", "static")
    return str(mode)  # type: ignore[return-value]


def warroom_widget_priority(widget_id: str) -> int:
    if widget_id == "market_monitor":
        return 30
    if widget_id == "liquidity_pressure":
        return 20
    if widget_id == "trade_flow_monitor":
        return 10
    return 0


def warroom_graph_widget_slot(widget_id: str) -> SlotMeta:
    return warroom_slot(
        "primary_live",
        widget_id,
        label=None,
        tone="primary",
        refresh_mode=warroom_widget_refresh_mode(widget_id),
        priority=warroom_widget_priority(widget_id),
        overlay_enabled=warroom_overlay_enabled(widget_id),
        partial_update_enabled=warroom_partial_update_enabled(widget_id),
    )


class WarroomGraphWidgetBundle(TypedDict):
    widget_id: str
    slot_meta: SlotMeta
    overlay_contract: WidgetOverlayContract


def warroom_graph_widget_bundle(widget_id: str) -> WarroomGraphWidgetBundle:
    return {
        "widget_id": widget_id,
        "slot_meta": warroom_graph_widget_slot(widget_id),
        "overlay_contract": warroom_graph_overlay_contract(widget_id),
    }


def warroom_layout_hints(widget_id: str) -> WidgetLayoutHints:
    if widget_id == "market_monitor":
        return build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        )
    if widget_id == "trade_flow_monitor":
        return build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        )
    if widget_id == "liquidity_pressure":
        return build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        )
    return build_layout_hints(zone_id="secondary")


def overlay_contract_caption(overlay_contract: dict | None) -> str:
    if not overlay_contract:
        return "overlay: disabled"

    if not overlay_contract.get("enabled"):
        return "overlay: disabled"

    base_series = overlay_contract.get("base_series") or []
    overlay_series = overlay_contract.get("overlay_series") or []
    threshold_lines = overlay_contract.get("threshold_lines") or []
    event_markers = overlay_contract.get("event_markers") or []

    return (
        "overlay: "
        f"base={', '.join(base_series) if base_series else '-'} / "
        f"overlay={', '.join(overlay_series) if overlay_series else '-'} / "
        f"thresholds={', '.join(threshold_lines) if threshold_lines else '-'} / "
        f"events={', '.join(event_markers) if event_markers else '-'}"
    )


def overlay_contract_metric_rows(overlay_contract: dict | None) -> list[tuple[str, str]]:
    if not overlay_contract:
        return [("overlay_enabled", "False")]

    enabled = bool(overlay_contract.get("enabled"))
    if not enabled:
        return [("overlay_enabled", "False")]

    base_series = overlay_contract.get("base_series") or []
    overlay_series = overlay_contract.get("overlay_series") or []
    threshold_lines = overlay_contract.get("threshold_lines") or []
    event_markers = overlay_contract.get("event_markers") or []

    return [
        ("overlay_enabled", "True"),
        ("base_series_count", str(len(base_series))),
        ("overlay_series_count", str(len(overlay_series))),
        ("threshold_line_count", str(len(threshold_lines))),
        ("event_marker_count", str(len(event_markers))),
    ]


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