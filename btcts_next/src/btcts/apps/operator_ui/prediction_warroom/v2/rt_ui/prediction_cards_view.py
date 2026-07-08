# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Reuses original WarRoom market-regime card shell first; no prediction/classifier/broker action.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (
    WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
    render_warroom_market_regime_card_shell,
)

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"
RT_MARKET_REGIME_CARD_BRIDGE_VERSION = "warroom_v2_rt_market_regime_card_bridge.2026_07_08.v1"
RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT = "D:/btc_ts_hot"
FUTURE_PREDICTION_CARD_ROWS = ("方向感", "反転候補", "ボラ警戒", "流動性 / 約定品質")


def _generated_at(packet: Mapping[str, Any]) -> str:
    for key in ("generated_at", "forecast_generated_at", "source_generated_at"):
        value = packet.get(key)
        if value:
            return str(value)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _render_prediction_boundary(packet: Mapping[str, Any], st_api: Any) -> None:
    generated_at = packet.get("generated_at") or packet.get("forecast_generated_at") or packet.get("source_generated_at")
    parts = [
        f"entry_gate={ENTRY_GATE_VERSION}",
        f"bridge={RT_MARKET_REGIME_CARD_BRIDGE_VERSION}",
        "prediction_cards_scope=market_regime_first",
        "original_warroom_market_regime_shell=true",
        "prediction_invoked=false",
        "classifier_invoked=false",
        "broker_action_allowed=false",
    ]
    if generated_at:
        parts.append(f"source_generated_at={generated_at}")
    st_api.caption(" / ".join(parts))


def _render_future_row_reservation(st_api: Any) -> None:
    st_api.caption(
        "次の予測カード行 追加枠: "
        + " / ".join(FUTURE_PREDICTION_CARD_ROWS)
        + "（未接続・今後追加）"
    )


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _short_list(values: list[str], *, limit: int = 4) -> str:
    shown = values[:limit]
    if len(values) > limit:
        shown.append(f"+{len(values) - limit}")
    return ",".join(shown)


def _market_regime_render_summary(renderer_packet: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(renderer_packet, Mapping):
        return {
            "packet_available": False,
            "preview_cards_used": False,
            "source_snapshot_ok": None,
            "source_snapshot_missing_sources": [],
            "source_snapshot_warnings": [],
            "prediction_warnings": [],
            "feature_bundle_available_signal_count": 0,
            "card_count": 0,
            "first_card_label": "",
            "first_card_confidence": None,
            "first_card_freshness": "",
            "preview_disabled_reason": "renderer_packet_unavailable",
        }
    cards = [card for card in renderer_packet.get("cards", []) if isinstance(card, Mapping)]
    first = cards[0] if cards else {}
    return {
        "packet_available": True,
        "preview_cards_used": bool(renderer_packet.get("preview_cards_used")),
        "source_snapshot_ok": renderer_packet.get("source_snapshot_ok"),
        "source_snapshot_missing_sources": _as_text_list(renderer_packet.get("source_snapshot_missing_sources")),
        "source_snapshot_warnings": _as_text_list(renderer_packet.get("source_snapshot_warnings")),
        "prediction_warnings": _as_text_list(renderer_packet.get("prediction_warnings")),
        "feature_bundle_available_signal_count": int(renderer_packet.get("feature_bundle_available_signal_count") or 0),
        "card_count": int(renderer_packet.get("card_count") or len(cards)),
        "first_card_label": str(first.get("regime_label") or first.get("regime_code") or ""),
        "first_card_confidence": first.get("confidence_percent"),
        "first_card_freshness": str(first.get("freshness_badge") or ""),
        "preview_disabled_reason": str(renderer_packet.get("preview_disabled_reason") or ""),
    }


def _render_market_regime_render_status(renderer_packet: Mapping[str, Any] | None, st_api: Any) -> dict[str, Any]:
    summary = _market_regime_render_summary(renderer_packet)
    source_label = "D-hot preview" if summary["preview_cards_used"] else "sample/fallback"
    first_label = summary["first_card_label"] or "-"
    first_confidence = summary["first_card_confidence"]
    first_freshness = summary["first_card_freshness"] or "-"
    parts = [
        f"地合いカード: {source_label}",
        f"cards={summary['card_count']}",
        f"source_snapshot={summary['source_snapshot_ok']}",
        f"signals={summary['feature_bundle_available_signal_count']}",
        f"first={first_label}/{first_confidence}%/{first_freshness}",
    ]
    if summary["source_snapshot_missing_sources"]:
        parts.append(f"missing={_short_list(summary['source_snapshot_missing_sources'])}")
    if summary["source_snapshot_warnings"]:
        parts.append(f"source_warn={_short_list(summary['source_snapshot_warnings'])}")
    if summary["prediction_warnings"]:
        parts.append(f"pred_warn={_short_list(summary['prediction_warnings'])}")
    if summary["preview_disabled_reason"]:
        parts.append(f"reason={summary['preview_disabled_reason']}")
    st_api.caption(" / ".join(parts))
    return summary


def _render_context_packets(packet: Mapping[str, Any], st_api: Any) -> None:
    cards = [card for card in packet.get("cards", []) if isinstance(card, Mapping)]
    if not cards:
        return
    with st_api.expander("Prediction card context packets", expanded=False):
        st_api.dataframe([
            {
                "card": str(card.get("title") or ""),
                "market_state": str(card.get("market_state") or ""),
                "chart": str(card.get("chart_summary") or ""),
                "operator_note": str(card.get("operator_note") or ""),
                "stale_guard": str(card.get("stale_guard") or ""),
                "read_only": bool(card.get("read_only", True)),
                "prediction_invoked": bool(card.get("prediction_invoked", False)),
                "classifier_invoked": bool(card.get("classifier_invoked", False)),
            }
            for card in cards
        ], width="stretch")


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    _render_prediction_boundary(packet, st_api)
    market_regime_packet = render_warroom_market_regime_card_shell(
        preview_enabled=True,
        hot_root=RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT,
        generated_at=_generated_at(packet),
    )
    market_regime_summary = _render_market_regime_render_status(market_regime_packet, st_api)
    _render_future_row_reservation(st_api)
    _render_context_packets(packet, st_api)
    return {
        "ok": True,
        "entry_gate_version": ENTRY_GATE_VERSION,
        "rt_market_regime_card_bridge_version": RT_MARKET_REGIME_CARD_BRIDGE_VERSION,
        "renderer_version": WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
        "market_regime_card_shell_rendered": True,
        "market_regime_renderer_packet_available": bool(market_regime_summary["packet_available"]),
        "market_regime_preview_cards_used": bool(market_regime_summary["preview_cards_used"]),
        "market_regime_source_snapshot_ok": market_regime_summary["source_snapshot_ok"],
        "market_regime_source_snapshot_missing_sources": list(market_regime_summary["source_snapshot_missing_sources"]),
        "market_regime_source_snapshot_warnings": list(market_regime_summary["source_snapshot_warnings"]),
        "market_regime_prediction_warnings": list(market_regime_summary["prediction_warnings"]),
        "market_regime_feature_bundle_available_signal_count": int(market_regime_summary["feature_bundle_available_signal_count"]),
        "market_regime_card_count": int(market_regime_summary["card_count"]),
        "market_regime_first_card_label": str(market_regime_summary["first_card_label"]),
        "market_regime_first_card_confidence": market_regime_summary["first_card_confidence"],
        "market_regime_first_card_freshness": str(market_regime_summary["first_card_freshness"]),
        "market_regime_first": True,
        "future_prediction_rows_reserved": True,
        "future_prediction_card_rows": list(FUTURE_PREDICTION_CARD_ROWS),
        "rendered_prediction_card_count": 1,
        "read_only": True,
        "prediction_invoked": False,
        "classifier_invoked": False,
        "broker_action_allowed": False,
        "prediction_card_enrichment_deferred": True,
    }
