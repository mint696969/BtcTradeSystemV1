# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
# desc: WarRoom v2 realtime prediction-card context renderer. Reuses original WarRoom market-regime card shell first; no prediction/classifier/broker action.

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import (
    WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
    render_warroom_market_regime_card_shell,
)

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"
RT_MARKET_REGIME_CARD_BRIDGE_VERSION = "warroom_v2_rt_market_regime_card_bridge.2026_07_08.v2_artifact_read_model_only"
RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH = "prediction/market_regime/latest_cards.json"
RT_MARKET_REGIME_CARDS_ARTIFACT_MAX_BYTES = 2_000_000
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
        "market_regime_read_model_artifact_only=true",
        "ui_market_regime_preview_inference=false",
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


def _market_regime_cards_artifact_path() -> Path:
    root = os.environ.get("BTCTS_HOT_ROOT") or os.environ.get("BTCTS_DATA_ROOT") or "D:/btc_ts_hot"
    return Path(root) / RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH


def _extract_market_regime_cards(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    candidates = payload.get("cards")
    if not isinstance(candidates, list):
        candidates = payload.get("market_regime_cards")
    if not isinstance(candidates, list):
        candidates = payload.get("card_rows")
    if not isinstance(candidates, list):
        return []
    return [dict(card) for card in candidates if isinstance(card, Mapping)]


def _read_market_regime_latest_cards_artifact() -> dict[str, Any]:
    path = _market_regime_cards_artifact_path()
    base: dict[str, Any] = {
        "read_attempted": True,
        "artifact_relative_path": RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH,
        "artifact_path": str(path),
        "artifact_present": False,
        "artifact_cards_used": False,
        "artifact_card_count": 0,
        "artifact_payload_schema_version": "",
        "artifact_generated_at": "",
        "artifact_read_error": "",
        "cards": [],
        "raw_market_source_read_performed": False,
        "preview_inference_invoked": False,
        "classifier_invoked": False,
    }
    try:
        if not path.exists():
            base["artifact_read_error"] = "latest_cards_artifact_missing"
            return base
        size = path.stat().st_size
        if size > RT_MARKET_REGIME_CARDS_ARTIFACT_MAX_BYTES:
            base["artifact_present"] = True
            base["artifact_read_error"] = f"latest_cards_artifact_too_large:{size}"
            return base
        payload = json.loads(path.read_text(encoding="utf-8"))
        cards = _extract_market_regime_cards(payload)
        base.update({
            "artifact_present": True,
            "artifact_cards_used": bool(cards),
            "artifact_card_count": len(cards),
            "artifact_payload_schema_version": str(payload.get("schema_version") or "") if isinstance(payload, Mapping) else "",
            "artifact_generated_at": str(payload.get("generated_at") or payload.get("created_at") or "") if isinstance(payload, Mapping) else "",
            "artifact_read_error": "" if cards else "latest_cards_artifact_has_no_cards",
            "cards": cards,
        })
        return base
    except Exception as exc:  # pragma: no cover - defensive UI read path
        base["artifact_read_error"] = f"latest_cards_artifact_read_failed:{type(exc).__name__}"
        return base


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
            "artifact_cards_used": False,
            "artifact_path": "",
            "artifact_read_error": "renderer_packet_unavailable",
            "raw_market_source_read_performed": False,
            "preview_inference_invoked": False,
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
        "artifact_cards_used": bool(renderer_packet.get("artifact_cards_used")),
        "artifact_path": str(renderer_packet.get("artifact_path") or ""),
        "artifact_read_error": str(renderer_packet.get("artifact_read_error") or ""),
        "raw_market_source_read_performed": bool(renderer_packet.get("raw_market_source_read_performed")),
        "preview_inference_invoked": bool(renderer_packet.get("preview_inference_invoked")),
    }


def _render_market_regime_render_status(renderer_packet: Mapping[str, Any] | None, st_api: Any) -> dict[str, Any]:
    summary = _market_regime_render_summary(renderer_packet)
    source_label = "artifact latest_cards" if summary["artifact_cards_used"] else "sample/fallback"
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
    if summary["artifact_read_error"]:
        parts.append(f"artifact={summary['artifact_read_error']}")
    if summary["preview_disabled_reason"]:
        parts.append(f"reason={summary['preview_disabled_reason']}")
    parts.append(f"preview_inference={summary['preview_inference_invoked']}")
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
    artifact_packet = _read_market_regime_latest_cards_artifact()
    artifact_cards = artifact_packet.get("cards") if artifact_packet.get("artifact_cards_used") else None
    market_regime_packet = render_warroom_market_regime_card_shell(
        cards=artifact_cards if isinstance(artifact_cards, list) else None,
    )
    market_regime_packet.update({
        "artifact_read_model_only": True,
        "artifact_read_attempted": bool(artifact_packet.get("read_attempted")),
        "artifact_relative_path": str(artifact_packet.get("artifact_relative_path") or ""),
        "artifact_path": str(artifact_packet.get("artifact_path") or ""),
        "artifact_present": bool(artifact_packet.get("artifact_present")),
        "artifact_cards_used": bool(artifact_packet.get("artifact_cards_used")),
        "artifact_card_count": int(artifact_packet.get("artifact_card_count") or 0),
        "artifact_payload_schema_version": str(artifact_packet.get("artifact_payload_schema_version") or ""),
        "artifact_generated_at": str(artifact_packet.get("artifact_generated_at") or ""),
        "artifact_read_error": str(artifact_packet.get("artifact_read_error") or ""),
        "preview_enabled": False,
        "preview_cards_used": False,
        "preview_inference_invoked": False,
        "explicit_source_root_read_performed": False,
        "dry_run_invoked": False,
        "source_snapshot_ok": None,
        "source_snapshot_missing_sources": [],
        "source_snapshot_warnings": [],
        "prediction_warnings": [],
        "feature_bundle_available_signal_count": 0,
        "raw_market_source_read_performed": False,
        "classifier_invoked": False,
    })
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
        "market_regime_preview_cards_used": False,
        "market_regime_artifact_read_model_only": True,
        "market_regime_artifact_cards_used": bool(market_regime_summary["artifact_cards_used"]),
        "market_regime_artifact_path": str(market_regime_summary["artifact_path"]),
        "market_regime_artifact_read_error": str(market_regime_summary["artifact_read_error"]),
        "market_regime_preview_inference_invoked": False,
        "market_regime_raw_market_source_read_performed": False,
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
        "ui_market_regime_preview_inference_removed": True,
        "implementation_marker": "PS_REMOVE_UI_MARKET_REGIME_PREVIEW_INFERENCE_2026_07_08",
        "broker_action_allowed": False,
        "prediction_card_enrichment_deferred": True,
    }
