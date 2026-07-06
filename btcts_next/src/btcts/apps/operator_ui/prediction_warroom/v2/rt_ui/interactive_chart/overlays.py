# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/overlays.py
# desc: Read-only overlay layer contract for WarRoom interactive chart. Pure normalization only; no prediction/order execution.

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

SUPPORTED_OVERLAY_KINDS = {"line", "marker", "price_band", "board_band"}
RENDERED_OVERLAY_KINDS = {"line", "marker"}
RESERVED_OVERLAY_KINDS = {"price_band", "board_band"}


def _epoch_seconds(value: object) -> int | None:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return int(ts.timestamp())


def _number(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:  # noqa: BLE001
        return None


def _safe_text(value: object, *, limit: int = 96) -> str:
    return str(value or "")[:limit]


def _safe_color(value: object, default: str) -> str:
    text = str(value or default)[:24]
    return text if text else default


def _normalize_line_layer(raw_layer: Mapping[str, Any], *, max_points_per_layer: int) -> dict[str, Any] | None:
    points: list[dict[str, Any]] = []
    for raw_point in list(raw_layer.get("points") or [])[:max_points_per_layer]:
        if not isinstance(raw_point, Mapping):
            continue
        epoch = _epoch_seconds(raw_point.get("ts") or raw_point.get("time"))
        value = _number(raw_point.get("value") or raw_point.get("price"))
        if epoch is None or value is None:
            continue
        points.append({"time": epoch, "value": round(value, 6)})
    if len(points) < 2:
        return None
    return {
        "points": sorted(points, key=lambda row: row["time"]),
        "color": _safe_color(raw_layer.get("color"), "#7c3aed"),
        "line_width": int(raw_layer.get("line_width") or 2),
        "line_style": _safe_text(raw_layer.get("line_style") or "dashed", limit=24),
    }


def _normalize_marker_layer(raw_layer: Mapping[str, Any], *, max_points_per_layer: int) -> dict[str, Any] | None:
    markers: list[dict[str, Any]] = []
    for raw_marker in list(raw_layer.get("markers") or raw_layer.get("points") or [])[:max_points_per_layer]:
        if not isinstance(raw_marker, Mapping):
            continue
        epoch = _epoch_seconds(raw_marker.get("ts") or raw_marker.get("time"))
        if epoch is None:
            continue
        markers.append(
            {
                "time": epoch,
                "position": _safe_text(raw_marker.get("position") or "aboveBar", limit=24),
                "color": _safe_color(raw_marker.get("color") or raw_layer.get("color"), "#0f766e"),
                "shape": _safe_text(raw_marker.get("shape") or "circle", limit=24),
                "text": _safe_text(raw_marker.get("text") or raw_marker.get("label") or raw_layer.get("label"), limit=64),
            }
        )
    if not markers:
        return None
    return {"markers": sorted(markers, key=lambda row: row["time"]), "color": _safe_color(raw_layer.get("color"), "#0f766e")}


def _normalize_reserved_layer(raw_layer: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "reserved_only": True,
        "rendered_now": False,
        "contract_note": "reserved for future board/depth/spread band rendering; ignored by current frontend renderer",
        "color": _safe_color(raw_layer.get("color"), "#64748b"),
    }


def normalize_interactive_overlay_layers(layers: object, *, max_layers: int = 12, max_points_per_layer: int = 240) -> list[dict[str, Any]]:
    """Normalize optional read-only chart overlays for frontend rendering.

    Supported contract:
    - line: prediction/liquidity flow line. points=[{ts/time, value/price}]
    - marker: order/execution/manual event markers. markers or points=[{ts/time, position, shape, text}]
    - price_band: reserved for spread/liquidity bands. Normalized but not rendered yet.
    - board_band: reserved for board/depth layers. Normalized but not rendered yet.

    This function is intentionally pure. It must not call prediction, classifier,
    broker, order, ledger, filesystem, websocket, or runtime side effects.
    """
    if not isinstance(layers, list):
        return []
    normalized: list[dict[str, Any]] = []
    for raw_layer in layers[:max_layers]:
        if not isinstance(raw_layer, Mapping):
            continue
        kind = _safe_text(raw_layer.get("kind") or "line", limit=32)
        if kind not in SUPPORTED_OVERLAY_KINDS:
            continue
        payload: dict[str, Any] | None
        if kind == "line":
            payload = _normalize_line_layer(raw_layer, max_points_per_layer=max_points_per_layer)
        elif kind == "marker":
            payload = _normalize_marker_layer(raw_layer, max_points_per_layer=max_points_per_layer)
        else:
            payload = _normalize_reserved_layer(raw_layer)
        if payload is None:
            continue
        normalized.append(
            {
                "layer_id": _safe_text(raw_layer.get("layer_id") or raw_layer.get("id") or f"overlay_{len(normalized) + 1}", limit=64),
                "label": _safe_text(raw_layer.get("label") or raw_layer.get("layer_id") or kind, limit=96),
                "kind": kind,
                "rendered_now": kind in RENDERED_OVERLAY_KINDS,
                "reserved_for_future": kind in RESERVED_OVERLAY_KINDS,
                "read_only": True,
                "websocket_send_enabled": False,
                "broker_send_enabled": False,
                "order_intent_submitted": False,
                "ledger_append_allowed": False,
                "prediction_invoked": False,
                "classifier_invoked": False,
                **payload,
            }
        )
    return normalized
