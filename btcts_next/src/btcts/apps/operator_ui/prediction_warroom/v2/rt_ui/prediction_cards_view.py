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
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_explanation_adapter import (
    MARKET_REGIME_EXPLANATION_ADAPTER_VERSION,
    build_market_regime_explanation_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui.market_regime_selected_read_model_bridge import (
    build_market_regime_selected_read_model_bridge,
)

ENTRY_GATE_VERSION = "warroom_v2_rt_entry_gate.2026_07_05.v1"
RT_MARKET_REGIME_CARD_BRIDGE_VERSION = "warroom_v2_rt_market_regime_card_bridge.2026_07_08.v2_artifact_read_model_only"
RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH = "prediction/market_regime/latest_cards.json"
RT_MARKET_REGIME_CALIBRATION_READ_MODEL_RELATIVE_PATH = "prediction/market_regime/calibration/latest_read_model.json"
RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_RELATIVE_PATH = "prediction/market_regime/parameter_set_comparison/latest_read_model.json"
RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_RELATIVE_PATH = "prediction/scenario_guidance/latest_read_model.json"
RT_MARKET_REGIME_CARDS_ARTIFACT_MAX_BYTES = 2_000_000
RT_MARKET_REGIME_CALIBRATION_READ_MODEL_MAX_BYTES = 1_000_000
RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_MAX_BYTES = 1_000_000
RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_MAX_BYTES = 1_000_000
FUTURE_PREDICTION_CARD_ROWS = ("方向感", "反転候補", "ボラ警戒", "流動性 / 約定品質")


def _generated_at(packet: Mapping[str, Any]) -> str:
    for key in ("generated_at", "forecast_generated_at", "source_generated_at"):
        value = packet.get(key)
        if value:
            return str(value)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _render_prediction_boundary(packet: Mapping[str, Any], st_api: Any) -> None:
    # Runtime boundary remains available in the returned packet and tests.
    # Do not render internal diagnostics in the normal WarRoom field.
    _ = packet, st_api


def _render_future_row_reservation(st_api: Any) -> None:
    # Future-family reservation is an internal roadmap concern, not a live field.
    _ = st_api


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


def _market_regime_cards_artifact_root() -> Path:
    hot_root = os.environ.get("BTCTS_HOT_ROOT")
    if hot_root:
        return Path(hot_root)
    data_root = os.environ.get("BTCTS_DATA_ROOT")
    if data_root:
        candidate = Path(data_root)
        if candidate.name.lower() == "data":
            return candidate.parent
        return candidate
    return Path("D:/btc_ts_hot")


def _market_regime_cards_artifact_path() -> Path:
    return _market_regime_cards_artifact_root() / RT_MARKET_REGIME_CARDS_ARTIFACT_RELATIVE_PATH


def _market_regime_calibration_read_model_path() -> Path:
    return _market_regime_cards_artifact_root() / RT_MARKET_REGIME_CALIBRATION_READ_MODEL_RELATIVE_PATH


def _market_regime_parameter_set_comparison_read_model_path() -> Path:
    return _market_regime_cards_artifact_root() / RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_RELATIVE_PATH


def _parent_scenario_guidance_read_model_path() -> Path:
    return _market_regime_cards_artifact_root() / RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_RELATIVE_PATH


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


def _read_market_regime_calibration_read_model_artifact() -> dict[str, Any]:
    path = _market_regime_calibration_read_model_path()
    base: dict[str, Any] = {
        "read_attempted": True,
        "artifact_relative_path": RT_MARKET_REGIME_CALIBRATION_READ_MODEL_RELATIVE_PATH,
        "artifact_path": str(path),
        "artifact_present": False,
        "artifact_used": False,
        "artifact_read_error": "",
        "primary_observation_source": "",
        "primary_score": None,
        "primary_known_total": 0,
        "primary_counts": {"hit": 0, "partial": 0, "miss": 0, "unknown": 0, "invalidated": 0},
        "reference_score": None,
        "raw_market_source_read_performed": False,
        "preview_inference_invoked": False,
        "classifier_invoked": False,
    }
    try:
        if not path.exists():
            base["artifact_read_error"] = "calibration_read_model_missing"
            return base
        size = path.stat().st_size
        if size > RT_MARKET_REGIME_CALIBRATION_READ_MODEL_MAX_BYTES:
            base["artifact_present"] = True
            base["artifact_read_error"] = f"calibration_read_model_too_large:{size}"
            return base
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            base["artifact_present"] = True
            base["artifact_read_error"] = "calibration_read_model_not_object"
            return base
        current = payload.get("primary_current") if isinstance(payload.get("primary_current"), Mapping) else {}
        compatibility = payload.get("primary") if isinstance(payload.get("primary"), Mapping) else {}
        has_current_schema = isinstance(payload.get("calibration_trust"), Mapping) or "primary_current" in payload
        selected = current if current else (compatibility if not has_current_schema else {})
        counts = selected.get("counts") if isinstance(selected.get("counts"), Mapping) else {}
        reference = payload.get("latest_cards_current_reference") if isinstance(payload.get("latest_cards_current_reference"), Mapping) else {}
        score = selected.get("calibration_score")
        reference_score = reference.get("calibration_score")
        selected_source = "primary_current" if current else (str(payload.get("primary_observation_source") or selected.get("key") or "primary") if selected else "")
        read_error = "" if selected else "calibration_read_model_has_no_primary_current"
        base.update({
            "artifact_present": True,
            "artifact_used": bool(selected),
            "artifact_read_error": read_error,
            "primary_observation_source": selected_source,
            "primary_score": round(float(score), 4) if score is not None else None,
            "primary_known_total": int(selected.get("known_total") or 0),
            "primary_counts": {
                "hit": int(counts.get("hit") or 0),
                "partial": int(counts.get("partial") or 0),
                "miss": int(counts.get("miss") or 0),
                "unknown": int(counts.get("unknown") or 0),
                "invalidated": int(counts.get("invalidated") or 0),
            },
            "reference_score": round(float(reference_score), 4) if reference_score is not None else None,
            "schema_mode": "current_primary" if current else ("legacy_compatibility" if selected else "current_schema_invalid"),
        })
        return base
    except Exception as exc:  # pragma: no cover - defensive UI read path
        base["artifact_read_error"] = f"calibration_read_model_read_failed:{type(exc).__name__}"
        return base


def _read_market_regime_parameter_set_comparison_read_model_artifact() -> dict[str, Any]:
    path = _market_regime_parameter_set_comparison_read_model_path()
    base: dict[str, Any] = {
        "read_attempted": True,
        "artifact_relative_path": RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_RELATIVE_PATH,
        "artifact_path": str(path),
        "artifact_present": False,
        "artifact_used": False,
        "artifact_read_error": "",
        "active_parameter_set_id": "",
        "comparison_ready": False,
        "comparison_blockers": [],
        "trusted_row_count": 0,
        "reference_only_row_count": 0,
        "trusted_parameter_set_count": 0,
        "comparable_parameter_set_count": 0,
        "promotion_candidate_count": 0,
        "recommendation_count": 0,
        "raw_market_source_read_performed": False,
        "preview_inference_invoked": False,
        "classifier_invoked": False,
    }
    try:
        if not path.exists():
            base["artifact_read_error"] = "parameter_set_comparison_read_model_missing"
            return base
        size = path.stat().st_size
        if size > RT_MARKET_REGIME_PARAMETER_SET_COMPARISON_READ_MODEL_MAX_BYTES:
            base["artifact_present"] = True
            base["artifact_read_error"] = f"parameter_set_comparison_read_model_too_large:{size}"
            return base
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            base["artifact_present"] = True
            base["artifact_read_error"] = "parameter_set_comparison_read_model_not_object"
            return base
        trust = payload.get("calibration_trust") if isinstance(payload.get("calibration_trust"), Mapping) else {}
        blockers = payload.get("comparison_blockers") if isinstance(payload.get("comparison_blockers"), list) else []
        base.update({
            "artifact_present": True,
            "artifact_used": True,
            "artifact_read_error": "",
            "active_parameter_set_id": str(payload.get("active_parameter_set_id") or ""),
            "comparison_ready": bool(payload.get("comparison_ready")),
            "comparison_blockers": [str(item) for item in blockers if str(item)],
            "trusted_row_count": int(trust.get("trusted_row_count") or 0),
            "reference_only_row_count": int(trust.get("reference_only_row_count") or 0),
            "trusted_parameter_set_count": int(trust.get("trusted_parameter_set_count") or 0),
            "comparable_parameter_set_count": int(trust.get("comparable_parameter_set_count") or 0),
            "promotion_candidate_count": len(payload.get("promotion_candidates") or []),
            "recommendation_count": len(payload.get("recommendations") or []),
        })
        return base
    except Exception as exc:  # pragma: no cover - defensive UI read path
        base["artifact_read_error"] = f"parameter_set_comparison_read_model_read_failed:{type(exc).__name__}"
        return base


def _read_parent_scenario_guidance_read_model_artifact() -> dict[str, Any]:
    path = _parent_scenario_guidance_read_model_path()
    base: dict[str, Any] = {
        "read_attempted": True,
        "artifact_relative_path": RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_RELATIVE_PATH,
        "artifact_path": str(path),
        "artifact_present": False,
        "artifact_used": False,
        "artifact_read_error": "",
        "generated_at": "",
        "source_run_id": "",
        "horizon_count": 0,
        "family_part_count": 0,
        "rejected_part_count": 0,
        "prediction_family_ids": [],
        "scenario_states": [],
        "dominant_family_ids": [],
        "horizons": [],
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "would_send_to_broker": False,
        "raw_market_source_read_performed": False,
        "preview_inference_invoked": False,
        "classifier_invoked": False,
    }
    try:
        if not path.exists():
            base["artifact_read_error"] = "parent_scenario_guidance_read_model_missing"
            return base
        size = path.stat().st_size
        if size > RT_PARENT_SCENARIO_GUIDANCE_READ_MODEL_MAX_BYTES:
            base["artifact_present"] = True
            base["artifact_read_error"] = f"parent_scenario_guidance_read_model_too_large:{size}"
            return base
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            base["artifact_present"] = True
            base["artifact_read_error"] = "parent_scenario_guidance_read_model_not_object"
            return base
        horizons = [dict(item) for item in payload.get("horizons", []) if isinstance(item, Mapping)]
        summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
        safety = payload.get("safety") if isinstance(payload.get("safety"), Mapping) else {}
        base.update({
            "artifact_present": True,
            "artifact_used": bool(horizons),
            "artifact_read_error": "" if horizons else "parent_scenario_guidance_read_model_has_no_horizons",
            "generated_at": str(payload.get("generated_at") or ""),
            "source_run_id": str(payload.get("source_run_id") or ""),
            "horizon_count": int(payload.get("horizon_count") or len(horizons)),
            "family_part_count": int(payload.get("family_part_count") or 0),
            "rejected_part_count": int(payload.get("rejected_part_count") or 0),
            "prediction_family_ids": _as_text_list(payload.get("prediction_family_ids")),
            "scenario_states": _as_text_list(summary.get("scenario_states")),
            "dominant_family_ids": _as_text_list(summary.get("dominant_family_ids")),
            "horizons": horizons,
            "broker_private_api_allowed": bool(safety.get("broker_private_api_allowed", False)),
            "autotrade_trigger_allowed": bool(safety.get("autotrade_trigger_allowed", False)),
            "order_intent_submitted": bool(safety.get("order_intent_submitted", False)),
            "parameter_auto_promotion_allowed": bool(safety.get("parameter_auto_promotion_allowed", False)),
            "live_parameter_apply_allowed": bool(safety.get("live_parameter_apply_allowed", False)),
            "would_send_to_broker": bool(safety.get("would_send_to_broker", False)),
        })
        return base
    except Exception as exc:  # pragma: no cover - defensive UI read path
        base["artifact_read_error"] = f"parent_scenario_guidance_read_model_read_failed:{type(exc).__name__}"
        return base


def _market_regime_calibration_detail_line(calibration_packet: Mapping[str, Any]) -> str:
    if not calibration_packet.get("artifact_used"):
        return ""
    counts = calibration_packet.get("primary_counts") if isinstance(calibration_packet.get("primary_counts"), Mapping) else {}
    return (
        "地合い評価: "
        f"source={calibration_packet.get('primary_observation_source') or '-'} / "
        f"score={calibration_packet.get('primary_score')} / "
        f"known={calibration_packet.get('primary_known_total')} / "
        f"hit/partial/miss={counts.get('hit', 0)}/{counts.get('partial', 0)}/{counts.get('miss', 0)} / "
        f"reference={calibration_packet.get('reference_score')} / display_only=true"
    )


def _enrich_market_regime_cards_with_calibration_detail(cards: list[dict[str, Any]] | None, calibration_packet: Mapping[str, Any]) -> tuple[list[dict[str, Any]] | None, bool]:
    if not isinstance(cards, list):
        return cards, False
    line = _market_regime_calibration_detail_line(calibration_packet)
    if not line:
        return [dict(card) for card in cards], False
    enriched: list[dict[str, Any]] = []
    changed = False
    for card in cards:
        item = dict(card)
        detail = dict(item.get("detail")) if isinstance(item.get("detail"), Mapping) else {}
        source_lines = list(detail.get("source_lines")) if isinstance(detail.get("source_lines"), list) else []
        if line not in source_lines:
            source_lines.append(line)
            changed = True
        detail["source_lines"] = source_lines
        detail["calibration_read_model_path"] = str(calibration_packet.get("artifact_path") or "")
        detail["calibration_primary_observation_source"] = str(calibration_packet.get("primary_observation_source") or "")
        detail["calibration_primary_score"] = calibration_packet.get("primary_score")
        detail["calibration_primary_known_total"] = int(calibration_packet.get("primary_known_total") or 0)
        detail["calibration_context_display_only"] = True
        item["detail"] = detail
        enriched.append(item)
    return enriched, changed

def _render_market_regime_calibration_status(calibration_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    if not calibration_packet.get("artifact_used"):
        st_api.caption(f"地合い評価: {calibration_packet.get('artifact_read_error') or 'calibration_read_model_unavailable'} / display_only=true")
        return dict(calibration_packet)
    counts = calibration_packet.get("primary_counts") if isinstance(calibration_packet.get("primary_counts"), Mapping) else {}
    st_api.caption(
        "地合い評価: "
        f"source={calibration_packet.get('primary_observation_source') or '-'} / "
        f"score={calibration_packet.get('primary_score')} / "
        f"known={calibration_packet.get('primary_known_total')} / "
        f"hit/partial/miss={counts.get('hit', 0)}/{counts.get('partial', 0)}/{counts.get('miss', 0)} / "
        f"reference={calibration_packet.get('reference_score')} / "
        f"calibration_path={calibration_packet.get('artifact_path') or '-'} / display_only=true"
    )
    return dict(calibration_packet)

def _parent_guidance_state_label(state: Any) -> str:
    labels = {
        "bullish": "上昇",
        "bearish": "下落",
        "range": "レンジ",
        "wait": "待機",
        "unknown": "不明",
        "no_edge": "優位性なし",
        "conflicting": "矛盾あり",
        "risk_off": "リスクオフ",
        "context_only": "参考情報",
    }
    key = str(state or "").strip()
    return labels.get(key, key or "-")


def _parent_guidance_horizon_row(horizon: Mapping[str, Any]) -> dict[str, Any]:
    guidance = horizon.get("operator_guidance") if isinstance(horizon.get("operator_guidance"), Mapping) else {}
    blockers = _as_text_list(guidance.get("blockers"))
    warnings = _as_text_list(guidance.get("warnings"))
    if not blockers:
        for part_key in ("conflicting_parts", "supporting_parts"):
            parts = horizon.get(part_key) if isinstance(horizon.get(part_key), list) else []
            for part in parts:
                if isinstance(part, Mapping):
                    blockers.extend(_as_text_list(part.get("blockers")))
                    warnings.extend(_as_text_list(part.get("warnings")))
    return {
        "horizon": str(horizon.get("horizon_key") or ""),
        "group": str(horizon.get("horizon_group") or ""),
        "state": str(horizon.get("scenario_state") or ""),
        "state_label": _parent_guidance_state_label(horizon.get("scenario_state")),
        "label": str(horizon.get("scenario_label") or ""),
        "dominant": str(horizon.get("dominant_family_id") or ""),
        "parts": int(horizon.get("family_part_count") or 0),
        "supporting": len(horizon.get("supporting_parts") or []),
        "conflicting": len(horizon.get("conflicting_parts") or []),
        "blockers": _short_list(list(dict.fromkeys(blockers)), limit=3) or "-",
        "warnings": _short_list(list(dict.fromkeys(warnings)), limit=3) or "-",
        "read_only": bool(horizon.get("read_only", True)),
    }


def _parent_guidance_compact_row(horizon: Mapping[str, Any]) -> dict[str, Any]:
    row = _parent_guidance_horizon_row(horizon)
    return {
        "時間軸": row.get("horizon") or "-",
        "状態": row.get("state_label") or row.get("state") or "-",
        "ラベル": row.get("label") or "-",
        "family": row.get("dominant") or "-",
        "blockers": row.get("blockers") or "-",
        "warnings": row.get("warnings") or "-",
        "read_only": bool(row.get("read_only", True)),
    }


def _render_parent_scenario_guidance_compact_table(parent_packet: Mapping[str, Any], st_api: Any) -> None:
    horizons = [item for item in parent_packet.get("horizons", []) if isinstance(item, Mapping)]
    rows = [_parent_guidance_compact_row(horizon) for horizon in horizons]
    if rows:
        st_api.dataframe(rows, width="stretch")


def _render_parent_scenario_guidance_detail_table(parent_packet: Mapping[str, Any], st_api: Any) -> None:
    horizons = [item for item in parent_packet.get("horizons", []) if isinstance(item, Mapping)]
    rows = [_parent_guidance_horizon_row(horizon) for horizon in horizons]
    with st_api.expander("親シナリオ guidance の詳細 / read-only", expanded=False):
        st_api.dataframe(rows, width="stretch")


def _render_parent_scenario_guidance_status(parent_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    if not parent_packet.get("artifact_used"):
        st_api.caption(f"親シナリオ: {parent_packet.get('artifact_read_error') or 'parent_scenario_guidance_read_model_unavailable'} / display_only=true")
        return dict(parent_packet)
    states = _as_text_list(parent_packet.get("scenario_states"))
    state_labels = [_parent_guidance_state_label(state) for state in states]
    families = _as_text_list(parent_packet.get("prediction_family_ids"))
    dominant = _as_text_list(parent_packet.get("dominant_family_ids"))
    st_api.caption(
        "親シナリオ: "
        f"horizons={parent_packet.get('horizon_count')} / "
        f"parts={parent_packet.get('family_part_count')} / "
        f"rejected={parent_packet.get('rejected_part_count')} / "
        f"families={_short_list(families, limit=4) or '-'} / "
        f"dominant={_short_list(dominant, limit=4) or '-'} / "
        f"states={_short_list(state_labels, limit=4) or '-'} / "
        f"source_run={parent_packet.get('source_run_id') or '-'} / "
        f"path={parent_packet.get('artifact_path') or '-'} / display_only=true"
    )
    _render_parent_scenario_guidance_compact_table(parent_packet, st_api)
    _render_parent_scenario_guidance_detail_table(parent_packet, st_api)
    return dict(parent_packet)


def _parameter_set_comparison_display_state(comparison_packet: Mapping[str, Any]) -> str:
    if comparison_packet.get("comparison_ready"):
        return "比較可能"
    blockers = _as_text_list(comparison_packet.get("comparison_blockers"))
    if "fewer_than_two_parameter_sets_with_minimum_trusted_samples" in blockers:
        return "比較未準備（信頼済みparameter setが1系統のみ）"
    if blockers:
        return "比較未準備"
    return "比較待ち"


def _render_parameter_set_comparison_detail_table(comparison_packet: Mapping[str, Any], st_api: Any) -> None:
    blockers = _as_text_list(comparison_packet.get("comparison_blockers"))
    rows = [
        {
            "項目": "状態",
            "値": _parameter_set_comparison_display_state(comparison_packet),
            "補足": f"ready={comparison_packet.get('comparison_ready')}",
        },
        {
            "項目": "信頼サンプル",
            "値": str(comparison_packet.get("trusted_row_count")),
            "補足": "source=candle_summary",
        },
        {
            "項目": "参考サンプル",
            "値": str(comparison_packet.get("reference_only_row_count")),
            "補足": "source=latest_cards_current / reference-only",
        },
        {
            "項目": "比較可能parameter set",
            "値": f"{comparison_packet.get('trusted_parameter_set_count')}/{comparison_packet.get('comparable_parameter_set_count')}",
            "補足": "2系統以上で比較準備完了",
        },
        {
            "項目": "昇格候補",
            "値": str(comparison_packet.get("promotion_candidate_count")),
            "補足": "auto promotion disabled",
        },
        {
            "項目": "推奨",
            "値": str(comparison_packet.get("recommendation_count")),
            "補足": "human/GPT review only",
        },
        {
            "項目": "blockers",
            "値": _short_list(blockers, limit=3) or "-",
            "補足": "display_only=true",
        },
    ]
    with st_api.expander("パラメータ比較の詳細 / read-only", expanded=False):
        st_api.dataframe(rows, width="stretch")


def _render_market_regime_parameter_set_comparison_status(comparison_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    if not comparison_packet.get("artifact_used"):
        st_api.caption(f"パラメータ比較: {comparison_packet.get('artifact_read_error') or 'parameter_set_comparison_read_model_unavailable'} / display_only=true")
        return dict(comparison_packet)
    blockers = _as_text_list(comparison_packet.get("comparison_blockers"))
    state = _parameter_set_comparison_display_state(comparison_packet)
    st_api.caption(
        "パラメータ比較: "
        f"{state} / "
        f"ready={comparison_packet.get('comparison_ready')} / "
        f"trusted={comparison_packet.get('trusted_row_count')} / "
        f"reference={comparison_packet.get('reference_only_row_count')} / "
        f"sets={comparison_packet.get('trusted_parameter_set_count')}/{comparison_packet.get('comparable_parameter_set_count')} / "
        f"promotions={comparison_packet.get('promotion_candidate_count')} / "
        f"recommendations={comparison_packet.get('recommendation_count')} / "
        f"blockers={_short_list(blockers, limit=3) or '-'} / "
        f"comparison_path={comparison_packet.get('artifact_path') or '-'} / display_only=true"
    )
    _render_parameter_set_comparison_detail_table(comparison_packet, st_api)
    return dict(comparison_packet)


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


def _display_value(value: Any, *, suffix: str = "") -> str:
    if value is None or value == "":
        return "-"
    return f"{value}{suffix}"


def _market_regime_explanation_overview_rows(explanation_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for horizon in explanation_packet.get("horizons", []):
        if not isinstance(horizon, Mapping):
            continue
        card = horizon.get("card") if isinstance(horizon.get("card"), Mapping) else {}
        confidence = horizon.get("confidence") if isinstance(horizon.get("confidence"), Mapping) else {}
        evidence = horizon.get("evidence") if isinstance(horizon.get("evidence"), Mapping) else {}
        calibration = horizon.get("calibration") if isinstance(horizon.get("calibration"), Mapping) else {}
        parameter_set = horizon.get("parameter_set") if isinstance(horizon.get("parameter_set"), Mapping) else {}
        rows.append({
            "時間軸": str(horizon.get("horizon_key") or "-"),
            "地合い": str(card.get("label_ja") or card.get("label") or "-"),
            "表示confidence": _display_value(confidence.get("display_confidence_percent"), suffix="%"),
            "shadow": _display_value(confidence.get("shadow_confidence_percent"), suffix="%"),
            "shadow only": bool(confidence.get("shadow_only", True)),
            "cap": _display_value(confidence.get("cap_percent"), suffix="%"),
            "support": int(evidence.get("supporting_source_count") or 0),
            "conflict": int(evidence.get("contradicting_source_count") or 0),
            "blockers": _short_list(_as_text_list(horizon.get("blockers")), limit=3) or "-",
            "warnings": _short_list(_as_text_list(horizon.get("warnings")), limit=3) or "-",
            "current sample": int(calibration.get("sample_count") or 0),
            "calibration": calibration.get("score"),
            "parameter set": str(parameter_set.get("active_parameter_set_id") or "-"),
            "比較可能": bool(parameter_set.get("comparison_ready", False)),
        })
    return rows


def _market_regime_source_rows(horizon: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in horizon.get("sources", []):
        if not isinstance(source, Mapping):
            continue
        rows.append({
            "source": str(source.get("source_id") or "-"),
            "方向": str(source.get("direction") or "-"),
            "設定weight": _display_value(source.get("configured_weight_percent"), suffix="%"),
            "今回signal": _display_value(source.get("current_signal_strength_percent"), suffix="%"),
            "quality score": _display_value(source.get("current_quality_score_percent"), suffix="%"),
            "weighted numerator": _display_value(source.get("current_weighted_numerator")),
            "quality": _display_value(source.get("current_quality_percent"), suffix="%"),
            "freshness": _display_value(source.get("current_freshness_percent"), suffix="%"),
            "過去reliability": _display_value(source.get("historical_reliability_percent"), suffix="%"),
            "trusted": int(source.get("trusted_sample_count") or 0),
            "minimum": int(source.get("minimum_trusted_sample_count") or 0),
            "remaining": int(source.get("remaining_trusted_samples") or 0),
            "ready": bool(source.get("ready", False)),
            "not-ready reason": str(source.get("not_ready_reason") or "-"),
        })
    return rows


def _render_market_regime_explanation(explanation_packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    errors = [
        f"{name}:{status.get('error')}"
        for name, status in (explanation_packet.get("artifact_status") or {}).items()
        if isinstance(status, Mapping) and status.get("error")
    ]
    violations = _as_text_list(explanation_packet.get("safety_violations"))

    with st_api.expander("地合い詳細", expanded=False):
        if not explanation_packet.get("ok"):
            st_api.caption(
                "unavailable / "
                f"errors={_short_list(errors, limit=4) or '-'} / "
                f"safety={_short_list(violations, limit=4) or '-'}"
            )
            return dict(explanation_packet)

        horizons = [item for item in explanation_packet.get("horizons", []) if isinstance(item, Mapping)]
        current = next((item for item in horizons if str(item.get("horizon_key")) == "current"), horizons[0] if horizons else {})
        calibration = current.get("calibration") if isinstance(current.get("calibration"), Mapping) else {}
        parameter_set = current.get("parameter_set") if isinstance(current.get("parameter_set"), Mapping) else {}
        sources = _market_regime_source_rows(current)
        not_ready = [row for row in sources if not bool(row.get("ready"))]

        st_api.caption(
            f"current sample={calibration.get('sample_count')} / "
            f"calibration={calibration.get('score')} / "
            "not win rate / "
            f"parameter comparison={parameter_set.get('comparison_ready')} / "
            f"not-ready source={len(not_ready)}"
        )
        st_api.dataframe(_market_regime_explanation_overview_rows(explanation_packet), width="stretch")
        st_api.dataframe(sources, width="stretch")

    return dict(explanation_packet)


def render_rt_prediction_cards(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    _render_prediction_boundary(packet, st_api)
    source_packet = packet.get("market_regime_source_packet") if isinstance(packet.get("market_regime_source_packet"), Mapping) else {}
    selected_bridge_packet = build_market_regime_selected_read_model_bridge(source_packet)
    selected_read_model_used = bool(selected_bridge_packet.get("ok"))
    parent_scenario_guidance_packet = _read_parent_scenario_guidance_read_model_artifact()
    parent_scenario_guidance_packet = _render_parent_scenario_guidance_status(parent_scenario_guidance_packet, st_api)
    artifact_packet = _read_market_regime_latest_cards_artifact()
    calibration_packet = _read_market_regime_calibration_read_model_artifact()
    parameter_set_comparison_packet = _read_market_regime_parameter_set_comparison_read_model_artifact()
    explanation_packet = (
        dict(selected_bridge_packet.get("explanation_packet") or {})
        if selected_read_model_used
        else build_market_regime_explanation_packet(_market_regime_cards_artifact_root())
    )
    artifact_cards = (
        list(selected_bridge_packet.get("cards") or [])
        if selected_read_model_used
        else (artifact_packet.get("cards") if artifact_packet.get("artifact_cards_used") else None)
    )
    artifact_cards, calibration_detail_enriched = _enrich_market_regime_cards_with_calibration_detail(
        artifact_cards if isinstance(artifact_cards, list) else None,
        calibration_packet,
    )
    market_regime_packet_raw = render_warroom_market_regime_card_shell(
        cards=artifact_cards if isinstance(artifact_cards, list) else None,
    )
    market_regime_packet = dict(market_regime_packet_raw) if isinstance(market_regime_packet_raw, Mapping) else {}
    market_regime_packet.update({
        "artifact_read_model_only": not selected_read_model_used,
        "selected_read_model_used": selected_read_model_used,
        "selected_source": str(selected_bridge_packet.get("selected_source") or "unavailable"),
        "selected_prediction_generated_at": str(selected_bridge_packet.get("prediction_generated_at") or ""),
        "selected_transport_received_at_ms": int(selected_bridge_packet.get("transport_received_at_ms") or 0),
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
    calibration_packet = _render_market_regime_calibration_status(calibration_packet, st_api)
    parameter_set_comparison_packet = _render_market_regime_parameter_set_comparison_status(parameter_set_comparison_packet, st_api)
    explanation_packet = _render_market_regime_explanation(explanation_packet, st_api)
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
        "market_regime_artifact_read_model_only": not selected_read_model_used,
        "market_regime_selected_read_model_used": selected_read_model_used,
        "market_regime_selected_source": str(selected_bridge_packet.get("selected_source") or "unavailable"),
        "market_regime_selected_prediction_generated_at": str(selected_bridge_packet.get("prediction_generated_at") or ""),
        "market_regime_selected_transport_received_at_ms": int(selected_bridge_packet.get("transport_received_at_ms") or 0),
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
        "parent_scenario_guidance_read_model_used": bool(parent_scenario_guidance_packet.get("artifact_used")),
        "parent_scenario_guidance_artifact_path": str(parent_scenario_guidance_packet.get("artifact_path") or ""),
        "parent_scenario_guidance_read_error": str(parent_scenario_guidance_packet.get("artifact_read_error") or ""),
        "parent_scenario_guidance_generated_at": str(parent_scenario_guidance_packet.get("generated_at") or ""),
        "parent_scenario_guidance_source_run_id": str(parent_scenario_guidance_packet.get("source_run_id") or ""),
        "parent_scenario_guidance_horizon_count": int(parent_scenario_guidance_packet.get("horizon_count") or 0),
        "parent_scenario_guidance_family_part_count": int(parent_scenario_guidance_packet.get("family_part_count") or 0),
        "parent_scenario_guidance_rejected_part_count": int(parent_scenario_guidance_packet.get("rejected_part_count") or 0),
        "parent_scenario_guidance_prediction_family_ids": list(parent_scenario_guidance_packet.get("prediction_family_ids") or []),
        "parent_scenario_guidance_scenario_states": list(parent_scenario_guidance_packet.get("scenario_states") or []),
        "parent_scenario_guidance_dominant_family_ids": list(parent_scenario_guidance_packet.get("dominant_family_ids") or []),
        "parent_scenario_guidance_broker_private_api_allowed": bool(parent_scenario_guidance_packet.get("broker_private_api_allowed")),
        "parent_scenario_guidance_autotrade_trigger_allowed": bool(parent_scenario_guidance_packet.get("autotrade_trigger_allowed")),
        "parent_scenario_guidance_order_intent_submitted": bool(parent_scenario_guidance_packet.get("order_intent_submitted")),
        "parent_scenario_guidance_parameter_auto_promotion_allowed": bool(parent_scenario_guidance_packet.get("parameter_auto_promotion_allowed")),
        "parent_scenario_guidance_live_parameter_apply_allowed": bool(parent_scenario_guidance_packet.get("live_parameter_apply_allowed")),
        "parent_scenario_guidance_would_send_to_broker": bool(parent_scenario_guidance_packet.get("would_send_to_broker")),
        "market_regime_first_card_label": str(market_regime_summary["first_card_label"]),
        "market_regime_first_card_confidence": market_regime_summary["first_card_confidence"],
        "market_regime_first_card_freshness": str(market_regime_summary["first_card_freshness"]),
        "market_regime_calibration_read_model_used": bool(calibration_packet.get("artifact_used")),
        "market_regime_calibration_artifact_path": str(calibration_packet.get("artifact_path") or ""),
        "market_regime_calibration_read_error": str(calibration_packet.get("artifact_read_error") or ""),
        "market_regime_calibration_primary_observation_source": str(calibration_packet.get("primary_observation_source") or ""),
        "market_regime_calibration_primary_score": calibration_packet.get("primary_score"),
        "market_regime_calibration_primary_known_total": int(calibration_packet.get("primary_known_total") or 0),
        "market_regime_calibration_primary_counts": dict(calibration_packet.get("primary_counts") or {}),
        "market_regime_calibration_reference_score": calibration_packet.get("reference_score"),
        "market_regime_calibration_detail_enriched": bool(calibration_detail_enriched),
        "market_regime_parameter_set_comparison_read_model_used": bool(parameter_set_comparison_packet.get("artifact_used")),
        "market_regime_parameter_set_comparison_artifact_path": str(parameter_set_comparison_packet.get("artifact_path") or ""),
        "market_regime_parameter_set_comparison_read_error": str(parameter_set_comparison_packet.get("artifact_read_error") or ""),
        "market_regime_parameter_set_comparison_active_parameter_set_id": str(parameter_set_comparison_packet.get("active_parameter_set_id") or ""),
        "market_regime_parameter_set_comparison_ready": bool(parameter_set_comparison_packet.get("comparison_ready")),
        "market_regime_parameter_set_comparison_blockers": list(parameter_set_comparison_packet.get("comparison_blockers") or []),
        "market_regime_parameter_set_comparison_trusted_row_count": int(parameter_set_comparison_packet.get("trusted_row_count") or 0),
        "market_regime_parameter_set_comparison_reference_only_row_count": int(parameter_set_comparison_packet.get("reference_only_row_count") or 0),
        "market_regime_parameter_set_comparison_trusted_parameter_set_count": int(parameter_set_comparison_packet.get("trusted_parameter_set_count") or 0),
        "market_regime_parameter_set_comparison_comparable_parameter_set_count": int(parameter_set_comparison_packet.get("comparable_parameter_set_count") or 0),
        "market_regime_parameter_set_comparison_promotion_candidate_count": int(parameter_set_comparison_packet.get("promotion_candidate_count") or 0),
        "market_regime_parameter_set_comparison_recommendation_count": int(parameter_set_comparison_packet.get("recommendation_count") or 0),
        "market_regime_explanation_adapter_version": str(explanation_packet.get("adapter_version") or MARKET_REGIME_EXPLANATION_ADAPTER_VERSION),
        "market_regime_explanation_packet_ok": bool(explanation_packet.get("ok")),
        "market_regime_explanation_horizon_count": int(explanation_packet.get("horizon_count") or 0),
        "market_regime_explanation_safety_violations": list(explanation_packet.get("safety_violations") or []),
        "market_regime_explanation_read_only": bool((explanation_packet.get("safety") or {}).get("read_only", True)),
        "market_regime_explanation_prediction_invoked": bool((explanation_packet.get("safety") or {}).get("prediction_invoked", False)),
        "market_regime_explanation_classifier_invoked": bool((explanation_packet.get("safety") or {}).get("classifier_invoked", False)),
        "market_regime_explanation_confidence_recalculated": bool((explanation_packet.get("safety") or {}).get("confidence_recalculated", False)),
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
