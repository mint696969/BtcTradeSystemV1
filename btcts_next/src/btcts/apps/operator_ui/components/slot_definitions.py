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


class WarroomGraphWidgetSpec(TypedDict):
    priority: int
    refresh_policy: WidgetRefreshPolicy
    overlay_contract: WidgetOverlayContract
    layout_hints: WidgetLayoutHints


class CommonWidgetSlotSpec(TypedDict):
    zone_id: str
    priority: int
    refresh_mode: SlotRefreshMode
    tone: WidgetTone


def warroom_widget_zone_ids() -> list[str]:
    return sorted({spec["zone_id"] for spec in _WARROOM_WIDGET_SLOT_SPECS.values()})


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


_WARROOM_GRAPH_WIDGET_SPECS: dict[str, WarroomGraphWidgetSpec] = {
    "market_monitor": {
        "priority": 30,
        "refresh_policy": build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="first candidate for fragment/partial redraw validation",
        ),
        "overlay_contract": build_overlay_contract(
            enabled=True,
            base_series=["mid_price"],
            overlay_series=["best_bid", "best_ask"],
            threshold_lines=[],
            event_markers=[],
        ),
        "layout_hints": build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        ),
    },
    "liquidity_pressure": {
        "priority": 20,
        "refresh_policy": build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="orderbook-derived pressure changes frequently",
        ),
        "overlay_contract": build_overlay_contract(
            enabled=True,
            base_series=["liquidity_pressure"],
            overlay_series=[],
            threshold_lines=["neutral_band"],
            event_markers=[],
        ),
        "layout_hints": build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        ),
    },
    "trade_flow_monitor": {
        "priority": 10,
        "refresh_policy": build_refresh_policy(
            mode="poll_fast",
            partial_update_enabled=True,
            chart_sensitive=True,
            rerender_scope="widget",
            notes="trade count and delta update frequently",
        ),
        "overlay_contract": build_overlay_contract(
            enabled=True,
            base_series=["trade_flow"],
            overlay_series=[],
            threshold_lines=["zero_line"],
            event_markers=[],
        ),
        "layout_hints": build_layout_hints(
            zone_id="primary_live",
            preferred_w=6,
            preferred_h=4,
            min_w=4,
            min_h=3,
        ),
    },
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


_WARROOM_WIDGET_SLOT_SPECS: dict[str, CommonWidgetSlotSpec] = {
    "warroom_header": {
        "zone_id": "overview",
        "priority": 10,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "warroom_alert_engine": {
        "zone_id": "overview",
        "priority": 20,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "ai_operator_panel": {
        "zone_id": "overview",
        "priority": 30,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "decision_log_panel": {
        "zone_id": "secondary",
        "priority": 40,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "watch_list_panel": {
        "zone_id": "secondary",
        "priority": 50,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "warroom_timeline": {
        "zone_id": "secondary",
        "priority": 60,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "ai_reasoning_panel": {
        "zone_id": "ai_diagnostics",
        "priority": 70,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "ai_market_summary_panel": {
        "zone_id": "ai_diagnostics",
        "priority": 80,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "ai_conversation_panel": {
        "zone_id": "ai_diagnostics",
        "priority": 90,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "market_regime": {
        "zone_id": "primary_live",
        "priority": 35,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "ai_signal": {
        "zone_id": "primary_live",
        "priority": 40,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "strategy_state": {
        "zone_id": "primary_live",
        "priority": 45,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
    "risk_monitor": {
        "zone_id": "primary_live",
        "priority": 50,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "agent_panels": {
        "zone_id": "primary_live",
        "priority": 60,
        "refresh_mode": "poll_slow",
        "tone": "primary",
    },
}


def warroom_graph_overlay_contract(widget_id: str) -> WidgetOverlayContract:
    spec = warroom_graph_widget_specs().get(widget_id)
    if spec is not None:
        return spec["overlay_contract"]
    return build_overlay_contract(enabled=False)


def warroom_overlay_enabled(widget_id: str) -> bool:
    return bool(warroom_graph_overlay_contract(widget_id).get("enabled"))


def warroom_overlay_widget_ids() -> list[str]:
    return list(warroom_graph_widget_ids())


def warroom_graph_widget_ids() -> list[str]:
    return [
        "market_monitor",
        "liquidity_pressure",
        "trade_flow_monitor",
    ]


def warroom_graph_widget_specs() -> dict[str, WarroomGraphWidgetSpec]:
    return dict(_WARROOM_GRAPH_WIDGET_SPECS)


def warroom_overlay_contract_count() -> int:
    return len(warroom_overlay_widget_ids())


def warroom_partial_update_widget_ids() -> list[str]:
    return list(warroom_graph_widget_ids())


def warroom_partial_update_enabled(widget_id: str) -> bool:
    return widget_id in set(warroom_partial_update_widget_ids())


def warroom_refresh_policy(widget_id: str) -> WidgetRefreshPolicy:
    spec = warroom_graph_widget_specs().get(widget_id)
    if spec is not None:
        return spec["refresh_policy"]
    return build_refresh_policy()


def warroom_chart_sensitive(widget_id: str) -> bool:
    return bool(warroom_refresh_policy(widget_id).get("chart_sensitive"))


def warroom_chart_sensitive_widget_ids() -> list[str]:
    return [
        widget_id
        for widget_id in warroom_graph_widget_ids()
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


def warroom_rerender_scope_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for widget_id in warroom_overlay_widget_ids():
        scope = str(warroom_refresh_policy(widget_id).get("rerender_scope", "page"))
        counts[scope] = counts.get(scope, 0) + 1
    return counts


def warroom_first_partial_redraw_candidate() -> str | None:
    preferred_order = [
        "market_monitor",
        "liquidity_pressure",
        "trade_flow_monitor",
    ]
    for widget_id in preferred_order:
        policy = warroom_refresh_policy(widget_id)
        if (
            bool(policy.get("partial_update_enabled"))
            and bool(policy.get("chart_sensitive"))
            and str(policy.get("rerender_scope", "page")) == "widget"
        ):
            return widget_id
    return None


def warroom_widget_refresh_mode(widget_id: str) -> SlotRefreshMode:
    mode = warroom_refresh_policy(widget_id).get("mode", "static")
    return str(mode)  # type: ignore[return-value]


def warroom_widget_priority(widget_id: str) -> int:
    spec = warroom_graph_widget_specs().get(widget_id)
    if spec is not None:
        return spec["priority"]
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


def warroom_widget_slot(widget_id: str) -> SlotMeta:
    spec = _WARROOM_WIDGET_SLOT_SPECS.get(widget_id)
    if spec is None:
        return warroom_slot("secondary", widget_id)

    return warroom_slot(
        spec["zone_id"],
        widget_id,
        label=None,
        tone=spec["tone"],
        refresh_mode=spec["refresh_mode"],
        priority=spec["priority"],
    )


def warroom_widget_ids() -> list[str]:
    return list(_WARROOM_WIDGET_SLOT_SPECS.keys())


def warroom_all_widget_ids() -> list[str]:
    return list(dict.fromkeys(warroom_widget_ids() + warroom_graph_widget_ids()))


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
    spec = warroom_graph_widget_specs().get(widget_id)
    if spec is not None:
        return spec["layout_hints"]
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


_HEALTH_WIDGET_SLOT_SPECS: dict[str, CommonWidgetSlotSpec] = {
    "collector_summary": {
        "zone_id": "overview",
        "priority": 10,
        "refresh_mode": "poll_normal",
        "tone": "strong",
    },
    "api_summary": {
        "zone_id": "overview",
        "priority": 20,
        "refresh_mode": "poll_fast",
        "tone": "primary",
    },
    "ws_summary": {
        "zone_id": "overview",
        "priority": 30,
        "refresh_mode": "poll_fast",
        "tone": "primary",
    },
    "layer3_summary": {
        "zone_id": "overview",
        "priority": 40,
        "refresh_mode": "poll_normal",
        "tone": "neutral",
    },
    "live_tick_caption": {
        "zone_id": "overview",
        "priority": 45,
        "refresh_mode": "poll_fast",
        "tone": "neutral",
    },
    "market_summary_caption": {
        "zone_id": "detail",
        "priority": 115,
        "refresh_mode": "poll_normal",
        "tone": "neutral",
    },
    "api_chart_panel": {
        "zone_id": "primary_live",
        "priority": 50,
        "refresh_mode": "poll_fast",
        "tone": "primary",
    },
    "ws_chart_panel": {
        "zone_id": "primary_live",
        "priority": 60,
        "refresh_mode": "poll_fast",
        "tone": "primary",
    },
    "layer3_chart_panel": {
        "zone_id": "primary_live",
        "priority": 70,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "api_continuity_panel": {
        "zone_id": "primary_live",
        "priority": 80,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "ws_continuity_panel": {
        "zone_id": "primary_live",
        "priority": 90,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "current_state_section": {
        "zone_id": "detail",
        "priority": 100,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "recent_events_section": {
        "zone_id": "detail",
        "priority": 110,
        "refresh_mode": "poll_normal",
        "tone": "neutral",
    },
}


def health_widget_slot(widget_id: str) -> SlotMeta:
    spec = _HEALTH_WIDGET_SLOT_SPECS.get(widget_id)
    if spec is None:
        return health_slot("detail", widget_id)

    return health_slot(
        spec["zone_id"],
        widget_id,
        label=None,
        tone=spec["tone"],
        refresh_mode=spec["refresh_mode"],
        priority=spec["priority"],
    )


def health_widget_ids() -> list[str]:
    return list(_HEALTH_WIDGET_SLOT_SPECS.keys())


def health_widget_zone_ids() -> list[str]:
    return sorted({spec["zone_id"] for spec in _HEALTH_WIDGET_SLOT_SPECS.values()})


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


def collector_widget_slot(widget_id: str) -> SlotMeta:
    spec = _COLLECTOR_WIDGET_SLOT_SPECS.get(widget_id)
    if spec is None:
        return collector_slot("primary_live", widget_id)

    return collector_slot(
        spec["zone_id"],
        widget_id,
        label=None,
        tone=spec["tone"],
        refresh_mode=spec["refresh_mode"],
        priority=spec["priority"],
    )


def collector_widget_ids() -> list[str]:
    return list(_COLLECTOR_WIDGET_SLOT_SPECS.keys())


def collector_widget_zone_ids() -> list[str]:
    return sorted({spec["zone_id"] for spec in _COLLECTOR_WIDGET_SLOT_SPECS.values()})


_COLLECTOR_WIDGET_SLOT_SPECS: dict[str, CommonWidgetSlotSpec] = {
    "origin_continuity_audit": {
        "zone_id": "primary_live",
        "priority": 70,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "system_stats": {
        "zone_id": "primary_live",
        "priority": 80,
        "refresh_mode": "poll_normal",
        "tone": "primary",
    },
    "execution_feed": {
        "zone_id": "primary_live",
        "priority": 90,
        "refresh_mode": "poll_fast",
        "tone": "primary",
    },
}