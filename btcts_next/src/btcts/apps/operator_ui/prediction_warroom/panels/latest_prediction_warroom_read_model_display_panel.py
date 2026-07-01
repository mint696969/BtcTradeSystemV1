# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py
# desc: PS-Q19J display-only WarRoom panel using split bilingual text catalog for the PS-Q19C latest prediction read model. Streamlit presentation only; no runtime/status/prediction writes, scheduler, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    load_latest_prediction_warroom_read_model_manifest_first,
)
from btcts.apps.operator_ui.prediction_warroom.texts.latest_prediction_display_texts import (
    COLUMN_LABELS,
    DISPLAY_TEXTS,
    DRIVER_LABELS,
    FAMILY_LABELS,
    VALUE_LABELS,
    WARNING_LABELS,
)

LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION = "prediction_warroom.latest_prediction_warroom_display_panel.ps_q19d.v1"
WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION = "prediction_warroom.warroom_prediction_display_auto_refresh.ps_q21a.v1"
WARROOM_PREDICTION_REFRESH_STATUS_STRIP_VERSION = "prediction_warroom.warroom_prediction_refresh_status_strip.ps_q21c.v1"
WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION = "prediction_warroom.warroom_prediction_refresh_live_badge.ps_q21d.v1"
WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION = "prediction_warroom.warroom_prediction_data_freshness_badge.ps_q21e.v1"
WARROOM_PREDICTION_UPDATE_VISIBILITY_VERSION = "prediction_warroom.warroom_prediction_refresh_visibility.ps_q25a.v1"
WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION = "prediction_warroom.prediction_artifact_horizon_freshness_expiry.ps_q25g.v1"
WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION = "prediction_warroom.prediction_data_age_severity_operator_action_guidance.ps_q25h.v1"
WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION = "prediction_warroom.prediction_panel_section_order_compact_layout.ps_q25i.v1"
WARROOM_PREDICTION_DENSITY_TUNING_VERSION = "prediction_warroom.prediction_panel_visual_review_density_tuning.ps_q25j.v1"
WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION = "prediction_warroom.prediction_display_japanese_reading_layer.ps_q26a.v1"
WARROOM_PREDICTION_JAPANESE_READING_DENSITY_POLISH_VERSION = "prediction_warroom.prediction_display_japanese_reading_density_polish.ps_q26b.v1"
WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION = "prediction_warroom.prediction_display_japanese_remaining_token_localization.ps_q26c.v1"
WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION = "prediction_warroom.telemetry_footer_detail_note_localization.ps_q26e.v1"
LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE = "warroom_realtime_prediction_display_only_panel_mounted"
Q19D_PAGE_ID = "warroom"
Q19D_ZONE_ID = "prediction_overview_zone"
Q19D_WIDGET_ID = "latest_prediction_warroom_read_model_display_panel"
Q19D_REFRESH_MODE = "poll_normal"
Q19D_REFRESH_SEC = 5
# Legacy guard marker kept in the panel after PS-Q19J text-catalog split.
# The footer token text itself is supplied by prediction_warroom.texts.latest_prediction_display_texts.
Q19I_BILINGUAL_EXPLANATION_LEGACY_GUARD_TOKEN = "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION"
Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT = r"D:\btc_ts_hot"


def _prediction_display_hot_root_hint() -> str:
    """Return the live D-hot root used by the scheduled prediction producer."""
    return Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "warroom_realtime_prediction_widget_display_only",
    "ps_q19c_read_model_consumed",
    "streamlit_display_panel_render_allowed",
    "warroom_display_panel_mounted",
    "fragment_slot_refresh_path_enabled",
    "operator_visible_prediction_rows",
    "operator_visible_market_snapshot",
    "operator_visible_safety_flags",
    "operator_visible_bilingual_explanation",
    "ui_language_switch_consumed",
)

FALSE_BOUNDARIES = (
    "component_runtime_binding_allowed",
    "real_prediction_component_render_invoked",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "prediction_artifact_write_allowed",
    "view_artifact_write_allowed",
    "scheduler_enabled",
    "producer_enabled",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_write_status_artifact",
    "would_write_prediction_artifact",
    "would_write_warroom_view_artifact",
    "would_send_to_broker",
)

def _lang() -> str:
    return "ja" if st.session_state.get("ui_lang", "en") == "ja" else "en"


def _t(lang: str, key: str) -> str:
    return DISPLAY_TEXTS.get(lang, DISPLAY_TEXTS["en"]).get(key, DISPLAY_TEXTS["en"].get(key, key))


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _format_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except Exception:
        return "-"


def _bool_text(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _clean(value) or "-"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _value_label(value: Any, *, lang: str) -> str:
    raw = _clean(value)
    if not raw:
        return "-"
    return VALUE_LABELS.get(lang, {}).get(raw, raw)


def _map_tokens(value: Any, *, lang: str, mapping: Mapping[str, str], limit: int = 2) -> tuple[str, str]:
    tokens = [str(v) for v in (value or [])[:limit]] if isinstance(value, list) else []
    raw = ",".join(tokens)
    translated = ", ".join(mapping.get(token, token) for token in tokens)
    return raw, translated


def _column_labels(rows: list[dict[str, Any]], *, lang: str) -> list[dict[str, Any]]:
    labels = COLUMN_LABELS.get(lang, COLUMN_LABELS["en"])
    return [{labels.get(k, k): v for k, v in row.items()} for row in rows]


def latest_prediction_warroom_display_rows(read_model: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    selected = _as_mapping(model.get("selected_records_by_horizon"))
    rows: list[dict[str, Any]] = []
    for horizon_key in [str(item) for item in model.get("selected_horizon_sec") or []]:
        horizon_rows = selected.get(horizon_key) or []
        if not isinstance(horizon_rows, list):
            continue
        for item in horizon_rows:
            row = _as_mapping(item)
            family = _clean(row.get("family")) or "-"
            label = _clean(row.get("primary_label")) or "-"
            warnings_raw, warnings_ja = _map_tokens(row.get("warnings"), lang=lang, mapping=WARNING_LABELS.get(lang, {}), limit=2)
            drivers_raw, drivers_ja = _map_tokens(row.get("drivers"), lang=lang, mapping=DRIVER_LABELS.get(lang, {}), limit=2)
            rows.append(
                {
                    "horizon": f"{horizon_key}s",
                    "family": family,
                    "family_meaning": FAMILY_LABELS.get(lang, {}).get(family, family),
                    "label": label,
                    "label_meaning": _value_label(label, lang=lang),
                    "confidence": _value_label(row.get("confidence"), lang=lang),
                    "score": _format_score(row.get("score")),
                    "usable": _value_label(_bool_text(row.get("usable")), lang=lang),
                    "warnings": warnings_raw,
                    "warning_meaning": warnings_ja,
                    "drivers": drivers_raw,
                    "driver_meaning": drivers_ja,
                }
            )
    return rows


def latest_prediction_warroom_safety_rows(read_model: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    safety = _as_mapping(model.get("safety_flags"))
    rows = [
        {"item": "read_model_ok", "value": _value_label(_bool_text(model.get("ok")), lang=lang), "note": "PS-Q19C read model status." if lang == "en" else "PS-Q19C 読み取りモデルの状態。"},
        {"item": "freshness_state", "value": _value_label(model.get("freshness_state"), lang=lang), "note": "fresh / delayed / stale / unknown." if lang == "en" else "新鮮 / やや遅延 / 古い / 不明。"},
        {"item": "age_sec", "value": _clean(model.get("age_sec")) or "-", "note": "Age of latest prediction artifact." if lang == "en" else "最新予測 artifact の経過秒。"},
        {"item": "record_count", "value": _clean(model.get("record_count")) or "0", "note": "forecast_batch record count." if lang == "en" else "予測バッチ全体のレコード数。"},
        {"item": "records_all_safe", "value": _value_label(_bool_text(safety.get("records_all_safe")), lang=lang), "note": "All displayed records remain read-only/non-executing/no broker/no writes." if lang == "en" else "表示レコードがすべて read-only / 非実行 / brokerなし / 書込なし。"},
        {"item": "view_artifact_write_allowed", "value": _value_label("false", lang=lang), "note": "Declared WarRoom view artifact is not written in PS-Q19D." if lang == "en" else "PS-Q19D では WarRoom view artifact を書き込みません。"},
        {"item": "autotrade_broker", "value": _value_label("false", lang=lang), "note": "No AutoTrade trigger and no broker/private API." if lang == "en" else "AutoTrade trigger も broker/private API もありません。"},
    ]
    return rows


def latest_prediction_warroom_market_rows(read_model: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    market = _as_mapping(model.get("market_snapshot"))
    return [
        {"item": "market_uid", "value": _clean(market.get("market_uid")) or "-"},
        {"item": "freshness", "value": _value_label(_clean(market.get("freshness")) or "UNKNOWN", lang=lang)},
        {"item": "trust_state", "value": _value_label(market.get("trust_state"), lang=lang)},
        {"item": "continuity_state", "value": _value_label(market.get("continuity_state"), lang=lang)},
        {"item": "interpretation_bucket", "value": _value_label(market.get("interpretation_bucket"), lang=lang)},
        {"item": "best_bid", "value": _clean(market.get("best_bid")) or "-"},
        {"item": "best_ask", "value": _clean(market.get("best_ask")) or "-"},
        {"item": "spread", "value": _clean(market.get("spread")) or "-"},
    ]


def latest_prediction_warroom_field_guide_rows(*, lang: str = "en") -> list[dict[str, str]]:
    rows = [
        {"item": "horizon", "value": _t(lang, "meaning_horizon")},
        {"item": "family", "value": _t(lang, "meaning_family")},
        {"item": "label", "value": _t(lang, "meaning_label")},
        {"item": "score", "value": _t(lang, "meaning_score")},
        {"item": "warnings", "value": _t(lang, "meaning_warnings")},
        {"item": "drivers", "value": _t(lang, "meaning_drivers")},
    ]
    return rows



def _q26a_prediction_first_row(rows: list[Any], horizon: int) -> Mapping[str, Any]:
    for item in rows:
        row = _as_mapping(item)
        if _clean(row.get("horizon")) == f"{horizon}s":
            return row
    return {}


def _q26a_prediction_row_summary(row: Mapping[str, Any]) -> str:
    if not row:
        return "表示候補なし"
    family = _clean(row.get("family_meaning") or row.get("family")) or "-"
    label = _clean(row.get("label_meaning") or row.get("label")) or "-"
    confidence = _clean(row.get("confidence")) or "-"
    score = _clean(row.get("score")) or "-"
    return f"{family} / {label} / confidence={confidence} / score={score}"


def latest_prediction_warroom_japanese_reading_rows(
    read_model: Mapping[str, Any] | Any,
    *,
    prediction_rows: list[dict[str, Any]] | None = None,
    horizon_expiry_packet: Mapping[str, Any] | Any | None = None,
    operator_action_guidance_packet: Mapping[str, Any] | Any | None = None,
) -> list[dict[str, Any]]:
    """Return compact Japanese reading rows for the WarRoom prediction display.

    PS-Q26A explains what the existing read-only prediction panel means. It does
    not change producer cadence, refresh prediction artifacts, or provide trade
    instructions.
    """
    model = _as_mapping(read_model)
    expiry = _as_mapping(horizon_expiry_packet)
    guidance = _as_mapping(operator_action_guidance_packet)
    rows = list(prediction_rows if prediction_rows is not None else latest_prediction_warroom_display_rows(model, lang="ja"))
    short_15 = _q26a_prediction_first_row(rows, 15)
    short_60 = _q26a_prediction_first_row(rows, 60)
    mid_300 = _q26a_prediction_first_row(rows, 300)
    long_900 = _q26a_prediction_first_row(rows, 900)
    age = _clean(model.get("age_sec")) or "-"
    freshness = _clean(model.get("freshness_state")) or "unknown"
    generated = _clean(model.get("generated_at")) or "-"
    expiry_state = _clean(expiry.get("overall_horizon_expiry_state")) or "unknown"
    action = _clean(guidance.get("operator_action_text") or guidance.get("operator_summary_text")) or "鮮度と horizon expiry を先に確認します。"
    return [
        {
            "読む順番": 1,
            "見る場所": "予測データ鮮度",
            "現在の値": f"generated_at={generated} / age={age}s / freshness={freshness}",
            "日本語での読み方": "generated_at が変わった時だけ予測結果そのものが新しくなります。UI heartbeat だけでは予測更新とは限りません。",
            "注意": "古い予測は短期判断に使わず、現在状態 nowcast を優先します。",
        },
        {
            "読む順番": 2,
            "見る場所": "horizon expiry",
            "現在の値": expiry_state,
            "日本語での読み方": _clean(expiry.get("operator_summary_text")) or "各 horizon が artifact age 上まだ読めるかを確認します。",
            "注意": "15s/60s が stale/expired の場合は短期の読みを弱めます。",
        },
        {
            "読む順番": 3,
            "見る場所": "短期 15s / 60s",
            "現在の値": f"15s={_q26a_prediction_row_summary(short_15)} / 60s={_q26a_prediction_row_summary(short_60)}",
            "日本語での読み方": "短期の方向感・警戒テーマを読む欄です。現在状態が live でない場合は重みを下げます。",
            "注意": "売買指示ではなく、operator review の材料です。",
        },
        {
            "読む順番": 4,
            "見る場所": "中期 300s / 900s",
            "現在の値": f"300s={_q26a_prediction_row_summary(mid_300)} / 900s={_q26a_prediction_row_summary(long_900)}",
            "日本語での読み方": "短期ノイズより少し長い文脈です。短期と矛盾する場合は、現在状態と鮮度を先に見ます。",
            "注意": "取引判断ではなく、背景理解として読みます。",
        },
        {
            "読む順番": 5,
            "見る場所": "operator action guidance",
            "現在の値": _clean(guidance.get("prediction_tactical_readiness") or guidance.get("operator_action_severity")) or "-",
            "日本語での読み方": action,
            "注意": "AutoTrade・broker・ledger・parameter apply には接続しません。",
        },
    ]



_Q26C_COLUMN_LABELS = {
    "item": "項目",
    "value": "値",
    "note": "メモ",
    "status_item": "状態項目",
    "operator_note": "見るポイント",
    "horizon": "時間軸",
    "family": "分類",
    "family_meaning": "分類の意味",
    "label": "ラベル",
    "label_meaning": "ラベルの意味",
    "confidence": "信頼度",
    "score": "スコア",
    "usable": "利用可",
    "warnings": "注意",
    "warning_meaning": "注意の意味",
    "drivers": "根拠",
    "driver_meaning": "根拠の意味",
}

_Q26C_VALUE_LABELS = {
    "prediction_rows_readable_as_current_artifact": "予測表示: 現在artifactとして読める",
    "prediction_rows_readable_as_context_only": "予測表示: 背景としてのみ読む",
    "tactical_predictions_ready": "予測表示: 読める",
    "tactical_predictions_not_ready": "予測表示: 弱い/未準備",
    "short_horizon_expired_or_stale": "短期は古い/弱い",
    "all_selected_horizons_within_ttl": "全horizon期限内",
    "some_horizons_stale": "一部horizonが古い",
    "some_horizons_expired": "一部horizonが期限切れ",
    "horizon_expiry_unknown": "horizon期限は不明",
    "fresh": "新しい",
    "delayed": "やや遅延",
    "stale": "古い",
    "unknown": "不明",
    "trend_bias": "トレンド方向",
    "cross_venue_confirmation": "他市場との整合",
    "market_regime": "地合い・レンジ/トレンド",
    "volatility_risk": "ボラティリティリスク",
    "short_bias": "短期バイアス",
    "confirmed": "整合あり",
    "range_candidate": "レンジ候補",
    "compression_watch": "圧縮警戒",
    "true": "はい",
    "false": "いいえ",
    "ok": "OK",
    "warning": "注意",
    "critical": "強い注意",
}


def _q26c_token_text(value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if text in _Q26C_VALUE_LABELS:
        return _Q26C_VALUE_LABELS[text]
    for token, label in sorted(_Q26C_VALUE_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(token, label)
    return text


def latest_prediction_warroom_q26c_localize_display_rows(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    localized: list[dict[str, Any]] = []
    for item in rows:
        if not isinstance(item, Mapping):
            localized.append({"値": _q26c_token_text(item)})
            continue
        localized.append({_Q26C_COLUMN_LABELS.get(str(key), str(key)): _q26c_token_text(value) for key, value in item.items()})
    return localized


def build_latest_prediction_warroom_q26c_remaining_token_localization_packet() -> dict[str, Any]:
    return {
        "ok": True,
        "remaining_token_localization_version": WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION,
        "operator_visible_localized_detail_tables": True,
        "localized_columns": dict(_Q26C_COLUMN_LABELS),
        "localized_token_count": len(_Q26C_VALUE_LABELS),
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "trade_guidance_added": False,
        "trade_signal_added": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }

_Q26E_TELEMETRY_TOKEN_LABELS = {
    "display-only": "表示専用",
    "Display-only": "表示専用",
    "Layout-only": "レイアウトのみ",
    "view_artifact_write_allowed=false": "view artifact書込=なし",
    "view_write=false": "表示書込=なし",
    "autotrade=false": "AutoTrade=なし",
    "AutoTrade=false": "AutoTrade=なし",
    "broker=false": "broker=なし",
    "broker": "broker",
    "scheduler": "scheduler",
    "parameter apply": "parameter apply",
    "parameter_apply": "parameter apply",
    "no artifact writes": "artifact書込なし",
    "no AutoTrade": "AutoTradeなし",
    "no broker": "brokerなし",
    "prediction_tactical_readiness": "予測の扱い",
    "compact_layout_rendered=True": "compact表示=あり",
    "density_tuning_rendered=True": "密度調整=あり",
    "detail_checks_folded_default=True": "詳細チェック=通常は折りたたみ",
    "refresh_heartbeat_utc": "画面heartbeat UTC",
    "source_generated_at": "予測生成時刻",
    "generated_at": "予測生成時刻",
    "freshness_state": "鮮度",
    "prediction_row_count": "予測行数",
    "short_horizon_expired_or_stale": "短期horizonは古い/弱い",
    "short_horizon_expired_or_stale=True": "短期horizonは古い/弱い=はい",
}


def _q26e_localize_telemetry_text(value: Any) -> str:
    text = _clean(value)
    for token, label in sorted(_Q26E_TELEMETRY_TOKEN_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(token, label)
    text = text.replace("=true", "=はい").replace("=false", "=いいえ")
    return text


def _q26e_safe_value(packet: Mapping[str, Any], *keys: str, default: str = "-") -> str:
    for key in keys:
        value = packet.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def latest_prediction_warroom_q26e_telemetry_footer_text(packet: Mapping[str, Any] | Any, *, lang: str = "ja") -> str:
    data = _as_mapping(packet)
    if lang != "ja":
        return _q26e_localize_telemetry_text(
            f"{_t('en', 'footer_token')} display_language={lang} "
            f"freshness_state={_q26e_safe_value(data, 'freshness_state')} "
            f"prediction_row_count={_q26e_safe_value(data, 'prediction_row_count', 'row_count')} "
            f"generated_at={_q26e_safe_value(data, 'generated_at', 'prediction_data_generated_at_utc')} "
            "view_artifact_write_allowed=false autotrade=false broker=false"
        )
    return (
        "PS-Q26E telemetry: "
        f"表示言語={lang} / "
        f"鮮度={_q26c_token_text(_q26e_safe_value(data, 'freshness_state'))} / "
        f"表示行数={_q26e_safe_value(data, 'prediction_row_count', 'row_count', default='-')} / "
        f"生成時刻={_q26e_safe_value(data, 'generated_at', 'prediction_data_generated_at_utc', default='-')} / "
        "表示専用 / view artifact書込=なし / AutoTrade=なし / broker=なし"
    )


def build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet() -> dict[str, Any]:
    sample = latest_prediction_warroom_q26e_telemetry_footer_text({"freshness_state": "fresh", "prediction_row_count": 24, "generated_at": "2026-07-01T00:00:00Z"}, lang="ja")
    return {
        "ok": True,
        "localization_version": WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION,
        "telemetry_footer_japanese_localized": True,
        "detail_note_token_fragments_localized": True,
        "sample_footer": sample,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "trade_guidance_added": False,
        "trade_signal_added": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }

def _q26b_prediction_label(value: Any) -> str:
    raw = _clean(value)
    mapping = {
        "fresh": "鮮度: 新しい",
        "delayed": "鮮度: やや遅延",
        "stale": "鮮度: 古い",
        "unknown": "鮮度: 不明",
        "all_selected_horizons_within_ttl": "全horizon期限内",
        "short_horizon_expired_or_stale": "短期は古い/弱い",
        "some_horizons_stale": "一部は古い",
        "some_horizons_expired": "一部は期限切れ",
        "horizon_expiry_unknown": "期限判定不明",
        "tactical_predictions_ready": "予測表示: 読める",
        "tactical_predictions_not_ready": "予測表示: 弱い",
        "prediction_rows_readable_as_current_artifact": "予測表示: 現在artifactとして読める",
        "warning": "注意",
        "critical": "強い注意",
        "ok": "OK",
    }
    return mapping.get(raw, raw or "-")


def latest_prediction_warroom_japanese_density_polish_rows(
    read_model: Mapping[str, Any] | Any,
    *,
    prediction_rows: list[dict[str, Any]] | None = None,
    horizon_expiry_packet: Mapping[str, Any] | Any | None = None,
    operator_action_guidance_packet: Mapping[str, Any] | Any | None = None,
) -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    expiry = _as_mapping(horizon_expiry_packet)
    guidance = _as_mapping(operator_action_guidance_packet)
    rows = list(prediction_rows if prediction_rows is not None else latest_prediction_warroom_display_rows(model, lang="ja"))
    short_15 = _q26a_prediction_first_row(rows, 15)
    short_60 = _q26a_prediction_first_row(rows, 60)
    mid_300 = _q26a_prediction_first_row(rows, 300)
    long_900 = _q26a_prediction_first_row(rows, 900)
    generated = _clean(model.get("generated_at")) or "-"
    age = _clean(model.get("age_sec")) or "-"
    freshness = _q26b_prediction_label(model.get("freshness_state"))
    expiry_state = _q26b_prediction_label(expiry.get("overall_horizon_expiry_state"))
    readiness = _q26b_prediction_label(guidance.get("prediction_tactical_readiness") or guidance.get("operator_action_severity"))
    guidance_text = _clean(guidance.get("operator_action_text") or guidance.get("operator_summary_text")) or "鮮度と期限を先に確認します。"
    return [
        {
            "要点": "予測を読めるか",
            "状態": f"{freshness} / age={age}s / {expiry_state}",
            "見る順番": "generated_at → horizon期限 → 15s/60s",
            "読み方": "generated_at が変わった時だけ予測そのものが更新です。UI更新とは別です。",
        },
        {
            "要点": "短期 15s/60s",
            "状態": f"15s={_q26a_prediction_row_summary(short_15)} / 60s={_q26a_prediction_row_summary(short_60)}",
            "見る順番": "現在状態がliveの時だけ強めに読む",
            "読み方": "短期の警戒テーマです。売買指示ではありません。古ければ読まない/弱めます。",
        },
        {
            "要点": "中期 300s/900s",
            "状態": f"300s={_q26a_prediction_row_summary(mid_300)} / 900s={_q26a_prediction_row_summary(long_900)}",
            "見る順番": "短期と矛盾したら鮮度を優先",
            "読み方": "地合い・背景理解です。短期エントリー判断には変換しません。",
        },
        {
            "要点": "今の扱い",
            "状態": readiness,
            "見る順番": "注意表示があれば待つ/弱める",
            "読み方": guidance_text,
        },
        {
            "要点": "安全境界",
            "状態": f"generated_at={generated}",
            "見る順番": "確認のみ",
            "読み方": "表示専用です。AutoTrade・broker・ledger・parameter apply には接続しません。",
        },
    ]


def build_latest_prediction_warroom_japanese_density_polish_packet(
    read_model: Mapping[str, Any] | Any,
    *,
    prediction_rows: list[dict[str, Any]] | None = None,
    horizon_expiry_packet: Mapping[str, Any] | Any | None = None,
    operator_action_guidance_packet: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    compact_rows = latest_prediction_warroom_japanese_density_polish_rows(
        read_model,
        prediction_rows=prediction_rows,
        horizon_expiry_packet=horizon_expiry_packet,
        operator_action_guidance_packet=operator_action_guidance_packet,
    )
    return {
        "ok": True,
        "density_polish_version": WARROOM_PREDICTION_JAPANESE_READING_DENSITY_POLISH_VERSION,
        "density_polish_role": "compact_japanese_prediction_reading_not_trade_instruction",
        "operator_visible_compact_japanese_rows": True,
        "compact_row_count": len(compact_rows),
        "compact_rows": compact_rows,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "trade_guidance_added": False,
        "trade_signal_added": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }

def build_latest_prediction_warroom_japanese_reading_layer_packet(
    read_model: Mapping[str, Any] | Any,
    *,
    prediction_rows: list[dict[str, Any]] | None = None,
    horizon_expiry_packet: Mapping[str, Any] | Any | None = None,
    operator_action_guidance_packet: Mapping[str, Any] | Any | None = None,
) -> dict[str, Any]:
    rows = latest_prediction_warroom_japanese_reading_rows(
        read_model,
        prediction_rows=prediction_rows,
        horizon_expiry_packet=horizon_expiry_packet,
        operator_action_guidance_packet=operator_action_guidance_packet,
    )
    return {
        "ok": True,
        "japanese_reading_layer_version": WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION,
        "japanese_reading_layer_role": "prediction_display_reading_support_not_trade_instruction",
        "operator_visible_japanese_rows": True,
        "row_count": len(rows),
        "rows": rows,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _format_jst_from_utc(value: Any) -> str:
    text = _clean(value).strip()
    if not text:
        return "-"
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S JST")
    except Exception:
        return text


def latest_prediction_warroom_update_visibility_rows(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, str]]:
    data = _as_mapping(packet)
    data_generated_utc = _clean(data.get("prediction_data_generated_at_utc") or data.get("generated_at")) or "-"
    data_generated_jst = _clean(data.get("prediction_data_generated_at_jst")) or _format_jst_from_utc(data_generated_utc)
    heartbeat_utc = _clean(data.get("refresh_heartbeat_utc")) or "-"
    heartbeat_jst = _clean(data.get("refresh_heartbeat_jst")) or _format_jst_from_utc(heartbeat_utc)
    auto_refresh = data.get("warroom_prediction_display_auto_refresh_enabled") is True
    fragment_enabled = data.get("fragment_enabled") is True
    interval = _clean(data.get("refresh_interval_sec")) or "-"
    source_mode = _clean(data.get("source_artifact_mode")) or "-"
    if lang == "ja":
        return [
            {"status_item": "予測データ生成 UTC", "value": data_generated_utc, "operator_note": "この値が変わった時だけ、予測結果そのものが新しくなっています。"},
            {"status_item": "予測データ生成 JST", "value": data_generated_jst, "operator_note": "画面で確認しやすい日本時間です。"},
            {"status_item": "パネル heartbeat JST", "value": heartbeat_jst, "operator_note": "この値が動くなら UI パネルの再描画は動いています。"},
            {"status_item": "UI更新間隔", "value": f"{interval}s", "operator_note": "UI heartbeat の間隔。予測データ生成間隔とは別です。"},
            {"status_item": "自動更新経路", "value": "ON" if auto_refresh and fragment_enabled else "OFF", "operator_note": "Streamlit fragment による部分更新です。"},
            {"status_item": "読込元", "value": source_mode, "operator_note": "distributed なら latest_manifest/sidecars 優先です。"},
        ]
    return [
        {"status_item": "prediction data generated UTC", "value": data_generated_utc, "operator_note": "Prediction results changed only when this value changes."},
        {"status_item": "prediction data generated JST", "value": data_generated_jst, "operator_note": "Local display time for operator review."},
        {"status_item": "panel heartbeat JST", "value": heartbeat_jst, "operator_note": "If this moves, the UI panel is rerendering."},
        {"status_item": "UI interval", "value": f"{interval}s", "operator_note": "UI heartbeat interval, separate from prediction production cadence."},
        {"status_item": "auto-refresh path", "value": "ON" if auto_refresh and fragment_enabled else "OFF", "operator_note": "Streamlit fragment partial refresh."},
        {"status_item": "source mode", "value": source_mode, "operator_note": "distributed means latest_manifest/sidecars first."},
    ]


def _render_prediction_update_visibility_strip(packet: Mapping[str, Any], *, lang: str) -> None:
    rows = latest_prediction_warroom_update_visibility_rows(packet, lang=lang)
    if lang == "ja":
        st.caption(
            "PS-Q25A update visibility: 予測データ生成時刻と UI heartbeat は別です。"
            "生成時刻が変わると予測そのものが更新、heartbeat が変わるとパネル再描画が生きています。"
        )
    else:
        st.caption(
            "PS-Q25A update visibility: prediction data generation and UI heartbeat are separate. "
            "Data changes when generated_at changes; the panel is alive when heartbeat changes."
        )
    st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(rows), width="stretch", hide_index=True)



def _int_or_none(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except Exception:
        return None


def _horizon_expiry_state(*, age_sec: int | None, horizon_sec: int) -> tuple[str, int | None, int | None, str]:
    if age_sec is None or horizon_sec <= 0:
        return "unknown", None, None, "prediction artifact age or horizon is unknown"
    time_to_expiry = int(horizon_sec) - int(age_sec)
    if age_sec <= horizon_sec:
        return "usable", max(0, time_to_expiry), 0, "prediction artifact is within this horizon TTL"
    expired_by = int(age_sec) - int(horizon_sec)
    if age_sec <= horizon_sec * 2:
        return "stale", 0, expired_by, "prediction artifact is older than horizon TTL; read with caution only"
    return "expired", 0, expired_by, "prediction artifact is expired for this horizon; do not use as live tactical guidance"


def latest_prediction_warroom_horizon_expiry_rows(read_model: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, Any]]:
    model = _as_mapping(read_model)
    age_sec = _int_or_none(model.get("age_sec"))
    selected = _as_mapping(model.get("selected_records_by_horizon"))
    horizons = [_int_or_none(item) for item in (model.get("selected_horizon_sec") or [])]
    rows: list[dict[str, Any]] = []
    for horizon in [item for item in horizons if item is not None]:
        state, time_to_expiry, expired_by, note = _horizon_expiry_state(age_sec=age_sec, horizon_sec=int(horizon))
        record_count = len(selected.get(str(horizon)) or []) if isinstance(selected.get(str(horizon)) or [], list) else 0
        if lang == "ja":
            if state == "usable":
                operator_note = "この horizon では予測 artifact はまだ期限内です。"
            elif state == "stale":
                operator_note = "この horizon では期限切れ直後です。参考程度に弱めて読んでください。"
            elif state == "expired":
                operator_note = "この horizon では期限切れです。現在の短期判断には使わないでください。"
            else:
                operator_note = "age または horizon が不明です。"
        else:
            operator_note = note
        rows.append({
            "horizon": f"{int(horizon)}s",
            "horizon_sec": int(horizon),
            "artifact_age_sec": age_sec,
            "horizon_expiry_state": state,
            "time_to_expiry_sec": time_to_expiry,
            "expired_by_sec": expired_by,
            "selected_record_count": record_count,
            "operator_note": operator_note,
        })
    return rows


def latest_prediction_warroom_horizon_expiry_packet(read_model: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    rows = latest_prediction_warroom_horizon_expiry_rows(read_model, lang=lang)
    order = {"usable": 0, "unknown": 1, "stale": 2, "expired": 3}
    worst = max((str(row.get("horizon_expiry_state")) for row in rows), key=lambda item: order.get(item, 4), default="unknown")
    short_expired = any(row.get("horizon_sec") in {15, 30, 60} and row.get("horizon_expiry_state") in {"stale", "expired"} for row in rows)
    if worst == "usable":
        overall = "all_selected_horizons_within_ttl"
        summary = "すべての表示 horizon は artifact age 上の期限内です。" if lang == "ja" else "All displayed horizons are within artifact TTL."
    elif short_expired:
        overall = "short_horizon_expired_or_stale"
        summary = "短期 horizon の予測は古い可能性があります。現在の短期判断には使わないでください。" if lang == "ja" else "Short-horizon predictions may be old; do not treat them as live tactical guidance."
    elif worst == "stale":
        overall = "some_horizons_stale"
        summary = "一部 horizon は期限切れ直後です。予測の重みを下げて読んでください。" if lang == "ja" else "Some horizons are stale; de-weight prediction interpretation."
    elif worst == "expired":
        overall = "some_horizons_expired"
        summary = "一部 horizon は期限切れです。live tactical guidance として読まないでください。" if lang == "ja" else "Some horizons are expired; do not read as live tactical guidance."
    else:
        overall = "horizon_expiry_unknown"
        summary = "horizon expiry を判定できません。generated_at と age を確認してください。" if lang == "ja" else "Horizon expiry cannot be determined; check generated_at and age."
    return {
        "horizon_expiry_version": WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION,
        "operator_visible_horizon_expiry": True,
        "horizon_expiry_rows": rows,
        "horizon_expiry_row_count": len(rows),
        "overall_horizon_expiry_state": overall,
        "short_horizon_expired_or_stale": short_expired,
        "operator_summary_text": summary,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "producer_cadence_changed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _render_prediction_horizon_expiry(packet: Mapping[str, Any], *, lang: str) -> None:
    expiry = _as_mapping(packet.get("horizon_expiry_packet"))
    message = str(expiry.get("operator_summary_text") or "")
    if expiry.get("overall_horizon_expiry_state") == "all_selected_horizons_within_ttl":
        st.success(message)
    elif expiry.get("short_horizon_expired_or_stale") is True:
        st.warning(message)
    else:
        st.info(message)
    st.caption("PS-Q25G horizon freshness/expiry: 表示専用です。予測producer cadenceやschedulerは変更しません。")
    rows = list(expiry.get("horizon_expiry_rows") or [])
    if rows:
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(rows), width="stretch", hide_index=True)



def _prediction_action_horizon_lists(expiry_rows: list[Mapping[str, Any]]) -> tuple[list[str], list[str], list[str]]:
    ignore: list[str] = []
    context_only: list[str] = []
    usable: list[str] = []
    for row in expiry_rows:
        horizon = _clean(row.get("horizon")) or f"{row.get('horizon_sec')}s"
        state = _clean(row.get("horizon_expiry_state"))
        sec = _int_or_none(row.get("horizon_sec")) or 0
        if state in {"stale", "expired"} and sec in {15, 30, 60}:
            ignore.append(horizon)
        elif state in {"stale", "expired"}:
            context_only.append(horizon)
        elif state == "usable":
            usable.append(horizon)
        else:
            context_only.append(horizon)
    return ignore, context_only, usable


def latest_prediction_warroom_operator_action_guidance_packet(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    data = _as_mapping(packet)
    expiry = _as_mapping(data.get("horizon_expiry_packet"))
    rows = [row for row in (expiry.get("horizon_expiry_rows") or []) if isinstance(row, Mapping)]
    ignore_horizons, context_only_horizons, usable_horizons = _prediction_action_horizon_lists(rows)
    freshness_state = (_clean(data.get("freshness_state")) or "unknown").lower()
    age_sec = _int_or_none(data.get("age_sec"))
    short_expired = expiry.get("short_horizon_expired_or_stale") is True
    overall_expiry = _clean(expiry.get("overall_horizon_expiry_state")) or "horizon_expiry_unknown"
    if short_expired:
        severity = "critical"
        tactical_readiness = "tactical_predictions_not_ready"
    elif overall_expiry in {"some_horizons_stale", "some_horizons_expired", "horizon_expiry_unknown"} or freshness_state in {"delayed", "stale", "unknown"}:
        severity = "warning"
        tactical_readiness = "read_predictions_with_caution"
    else:
        severity = "ok"
        tactical_readiness = "prediction_rows_readable_as_current_artifact"
    wait_for_new = bool(short_expired or severity == "warning")
    if lang == "ja":
        if severity == "critical":
            summary = "短期予測は live tactical guidance として読まないでください。新しい予測 artifact を待ち、現在状態 nowcast を優先してください。"
        elif severity == "warning":
            summary = "予測データは注意付きです。期限切れ horizon を弱め、使う場合は context-only にしてください。"
        else:
            summary = "予測 artifact は表示 horizon の範囲で読めます。ただし売買指示ではありません。"
        wait_note = "generated_at が更新されるまで短期予測を tactical に扱わないでください。"
        nowcast_note = "現在判断は Live Market Nowcast / current-state score を優先してください。"
        heartbeat_note = "UI heartbeat は画面更新の確認であり、予測データ生成の更新ではありません。"
    else:
        if severity == "critical":
            summary = "Do not read short-horizon predictions as live tactical guidance. Wait for a new artifact and prioritize current-state nowcast."
        elif severity == "warning":
            summary = "Prediction data needs caution; de-weight expired horizons and read as context-only where applicable."
        else:
            summary = "Prediction artifact is readable within displayed horizon TTL. Not a trade instruction."
        wait_note = "Do not treat short predictions as tactical until generated_at changes."
        nowcast_note = "Prioritize Live Market Nowcast / current-state score for current decisions."
        heartbeat_note = "UI heartbeat confirms panel refresh, not prediction data generation."
    action_rows = [
        {"action": "ignore_live_tactical_horizons", "target": ",".join(ignore_horizons) or "none", "severity": severity if ignore_horizons else "ok", "operator_note": summary if ignore_horizons else ("期限切れ短期 horizon はありません。" if lang == "ja" else "No expired short horizon.")},
        {"action": "context_only_horizons", "target": ",".join(context_only_horizons) or "none", "severity": "warning" if context_only_horizons else "ok", "operator_note": "文脈参考に留め、entry/exit 判断には使わないでください。" if lang == "ja" else "Use only as context; do not use for entry/exit."},
        {"action": "wait_for_new_prediction_artifact", "target": "generated_at", "severity": severity if wait_for_new else "ok", "operator_note": wait_note if wait_for_new else ("generated_at は horizon TTL 上で利用可能です。" if lang == "ja" else "generated_at is usable for displayed horizon TTL.")},
        {"action": "prioritize_current_state_nowcast", "target": "Live Market Nowcast", "severity": "info" if wait_for_new else "ok", "operator_note": nowcast_note},
        {"action": "do_not_confuse_ui_heartbeat_with_prediction_update", "target": "panel heartbeat", "severity": "info", "operator_note": heartbeat_note},
    ]
    return {
        "operator_action_guidance_version": WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION,
        "operator_visible_action_guidance": True,
        "operator_action_severity": severity,
        "prediction_tactical_readiness": tactical_readiness,
        "operator_action_summary_text": summary,
        "ignore_live_tactical_horizons": ignore_horizons,
        "context_only_horizons": context_only_horizons,
        "usable_horizons": usable_horizons,
        "wait_for_new_prediction_artifact": wait_for_new,
        "action_rows": action_rows,
        "action_row_count": len(action_rows),
        "artifact_age_sec": age_sec,
        "freshness_state": freshness_state,
        "overall_horizon_expiry_state": overall_expiry,
        "short_horizon_expired_or_stale": short_expired,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "producer_cadence_changed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _render_prediction_operator_action_guidance(packet: Mapping[str, Any], *, lang: str) -> None:
    guidance = _as_mapping(packet.get("operator_action_guidance_packet"))
    message = str(guidance.get("operator_action_summary_text") or "")
    if guidance.get("operator_action_severity") == "critical":
        st.error(message)
    elif guidance.get("operator_action_severity") == "warning":
        st.warning(message)
    else:
        st.success(message)
    st.caption("PS-Q25H operator action guidance: 表示専用です。producer cadence、scheduler、AutoTrade、brokerは変更しません。")
    rows = list(guidance.get("action_rows") or [])
    if rows:
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(rows), width="stretch", hide_index=True)



def latest_prediction_warroom_compact_layout_rows(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    guidance = _as_mapping(data.get("operator_action_guidance_packet"))
    expiry = _as_mapping(data.get("horizon_expiry_packet"))
    if lang == "ja":
        return [
            {"item": "operator_action", "value": _clean(guidance.get("operator_action_severity")) or "-", "note": _clean(guidance.get("prediction_tactical_readiness")) or "-"},
            {"item": "prediction_data_age", "value": _clean(data.get("age_sec")) or "-", "note": _clean(data.get("freshness_state")) or "unknown"},
            {"item": "horizon_expiry", "value": _clean(expiry.get("overall_horizon_expiry_state")) or "-", "note": "short_expired=" + _bool_text(expiry.get("short_horizon_expired_or_stale"))},
            {"item": "generated_at", "value": _clean(data.get("generated_at")) or "-", "note": "この値が変わると予測データが更新されます。"},
            {"item": "panel_heartbeat", "value": _clean(data.get("refresh_heartbeat_utc")) or "-", "note": "画面更新の確認。予測生成更新ではありません。"},
        ]
    return [
        {"item": "operator_action", "value": _clean(guidance.get("operator_action_severity")) or "-", "note": _clean(guidance.get("prediction_tactical_readiness")) or "-"},
        {"item": "prediction_data_age", "value": _clean(data.get("age_sec")) or "-", "note": _clean(data.get("freshness_state")) or "unknown"},
        {"item": "horizon_expiry", "value": _clean(expiry.get("overall_horizon_expiry_state")) or "-", "note": "short_expired=" + _bool_text(expiry.get("short_horizon_expired_or_stale"))},
        {"item": "generated_at", "value": _clean(data.get("generated_at")) or "-", "note": "Prediction data updates when this changes."},
        {"item": "panel_heartbeat", "value": _clean(data.get("refresh_heartbeat_utc")) or "-", "note": "UI refresh check, not producer generation."},
    ]


def latest_prediction_warroom_compact_layout_packet(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    data = _as_mapping(packet)
    rows = latest_prediction_warroom_compact_layout_rows(data, lang=lang)
    guidance = _as_mapping(data.get("operator_action_guidance_packet"))
    severity = _clean(guidance.get("operator_action_severity")) or "unknown"
    summary = _clean(guidance.get("operator_action_summary_text")) or ("Prediction panel compact summary." if lang != "ja" else "予測パネル compact summary。")
    return {
        "compact_layout_version": WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION,
        "operator_visible_compact_layout": True,
        "compact_layout_rows": rows,
        "compact_layout_row_count": len(rows),
        "compact_layout_top_priority": "operator_action_guidance_first",
        "compact_layout_detail_tables_still_visible": True,
        "operator_action_severity": severity,
        "prediction_tactical_readiness": guidance.get("prediction_tactical_readiness"),
        "operator_summary_text": summary,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "layout_only_change": True,
        "producer_cadence_changed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _render_prediction_compact_operator_header(packet: Mapping[str, Any], *, lang: str) -> None:
    compact = _as_mapping(packet.get("compact_layout_packet"))
    severity = _clean(compact.get("operator_action_severity"))
    message = str(compact.get("operator_summary_text") or "")
    if severity == "critical":
        st.error(message)
    elif severity == "warning":
        st.warning(message)
    else:
        st.success(message)
    st.caption("PS-Q25I compact top summary: action → data age → horizon expiry → generated_at/heartbeat の順で確認します。レイアウトのみ・表示専用です。")
    rows = list(compact.get("compact_layout_rows") or [])
    if rows:
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(rows), width="stretch", hide_index=True)



def latest_prediction_warroom_density_tuning_packet(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    data = _as_mapping(packet)
    return {
        "density_tuning_version": WARROOM_PREDICTION_DENSITY_TUNING_VERSION,
        "operator_visible_density_tuning": True,
        "compact_header_kept_top": True,
        "detail_checks_folded_default": True,
        "detail_checks_still_available": True,
        "detail_sections_folded": [
            "refresh_status",
            "prediction_data_freshness",
            "horizon_expiry",
            "operator_action_guidance",
            "prediction_update_visibility",
        ],
        "detail_sections_folded_count": 5,
        "reading_guide_folded_default": True,
        "metrics_still_visible": True,
        "prediction_rows_still_visible": True,
        "operator_action_severity": data.get("operator_action_severity"),
        "prediction_tactical_readiness": data.get("prediction_tactical_readiness"),
        "layout_only_change": True,
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "producer_cadence_changed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def _render_prediction_detail_checks_foldout(packet: Mapping[str, Any], *, lang: str) -> None:
    label = "PS-Q25J prediction detail checks / freshness, expiry, action, heartbeat"
    help_text = "Compact header is shown above. Open this for detailed refresh/freshness/expiry/action tables."
    if lang == "ja":
        label = "PS-Q25J 予測詳細チェック / freshness・expiry・action・heartbeat"
        help_text = "上部 compact header を優先表示。詳細な更新・期限・action・heartbeat 表はここを開いて確認します。"
    st.caption("PS-Q25J density tuning: compact headerを先に表示し、詳細チェックは通常折りたたみます。レイアウトのみ・表示専用です。")
    with st.expander(label, expanded=False):
        st.caption(help_text)
        _render_refresh_status_strip(packet, lang=lang)
        _render_prediction_data_freshness_badge(packet, lang=lang)
        _render_prediction_horizon_expiry(packet, lang=lang)
        _render_prediction_operator_action_guidance(packet, lang=lang)
        _render_prediction_update_visibility_strip(packet, lang=lang)


def latest_prediction_warroom_refresh_live_badge_packet(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    """Return a compact live badge packet for the WarRoom prediction refresh status."""
    data = _as_mapping(packet)
    auto_refresh = data.get("warroom_prediction_display_auto_refresh_enabled") is True
    heartbeat = _clean(data.get("refresh_heartbeat_utc")) or "-"
    interval = _clean(data.get("refresh_interval_sec")) or "-"
    broad_reload_disabled = data.get("broad_page_reload_disabled") is True
    active = bool(auto_refresh and heartbeat != "-" and broad_reload_disabled)
    if lang == "ja":
        message = (
            f"🟢 予測パネル更新中 | heartbeat UTC={heartbeat} | 更新間隔={interval}s | 全体再読込なし"
            if active
            else f"🟡 予測パネル更新注意 | heartbeat UTC={heartbeat} | 更新間隔={interval}s"
        )
        inactive_note = "自動更新または全体再読込境界を確認してください。"
    else:
        message = (
            f"🟢 Prediction panel live | heartbeat UTC={heartbeat} | interval={interval}s | broad reload disabled"
            if active
            else f"🟡 Prediction panel attention | heartbeat UTC={heartbeat} | interval={interval}s"
        )
        inactive_note = "Check auto-refresh or broad reload boundary."
    return {
        "refresh_live_badge_version": WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION,
        "refresh_live_badge_active": active,
        "refresh_live_badge_state": "prediction_refresh_live" if active else "prediction_refresh_attention",
        "refresh_live_badge_message": message,
        "refresh_live_badge_inactive_note": inactive_note,
        "refresh_live_badge_heartbeat_utc": heartbeat,
        "refresh_live_badge_interval_sec": interval,
        "refresh_live_badge_broad_reload_disabled": broad_reload_disabled,
        "refresh_live_badge_auto_refresh_enabled": auto_refresh,
        "operator_visible_refresh_live_badge": True,
        "runtime_enablement_allowed": False,
        "view_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def _render_refresh_live_badge(packet: Mapping[str, Any], *, lang: str) -> None:
    """Render a visible live badge above the refresh status strip; display-only."""
    badge = latest_prediction_warroom_refresh_live_badge_packet(packet, lang=lang)
    if badge.get("refresh_live_badge_active") is True:
        st.success(str(badge.get("refresh_live_badge_message") or ""))
    else:
        st.warning(str(badge.get("refresh_live_badge_message") or badge.get("refresh_live_badge_inactive_note") or ""))


def latest_prediction_warroom_data_freshness_badge_packet(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> dict[str, Any]:
    """Return a compact badge that separates prediction data freshness from panel refresh liveness."""
    data = _as_mapping(packet)
    freshness_state = (_clean(data.get("freshness_state")) or "unknown").lower()
    freshness_label = _clean(data.get("freshness_label")) or freshness_state
    age = _clean(data.get("age_sec")) or "-"
    row_count = _clean(data.get("prediction_row_count")) or "0"
    generated_at = _clean(data.get("generated_at")) or "-"
    ok = data.get("ok") is True
    row_count_ok = False
    try:
        row_count_ok = int(row_count) > 0
    except Exception:
        row_count_ok = False
    fresh = bool(ok and row_count_ok and freshness_state == "fresh")
    delayed = bool(ok and row_count_ok and freshness_state in {"delayed", "late"})
    stale = bool((not ok) or (not row_count_ok) or freshness_state in {"stale", "unknown", "missing", "blocked"})
    if lang == "ja":
        if fresh:
            message = f"🟢 予測データ fresh | age={age}s | rows={row_count} | generated_at={generated_at}"
        elif delayed:
            message = f"🟡 予測データ delayed | age={age}s | rows={row_count} | generated_at={generated_at}"
        else:
            message = f"🟠 予測データ freshness注意 | state={freshness_state} | age={age}s | rows={row_count} | generated_at={generated_at}"
        note = "パネル更新中でも、ここが stale なら予測データ自体は古い可能性があります。"
    else:
        if fresh:
            message = f"🟢 Prediction data fresh | age={age}s | rows={row_count} | generated_at={generated_at}"
        elif delayed:
            message = f"🟡 Prediction data delayed | age={age}s | rows={row_count} | generated_at={generated_at}"
        else:
            message = f"🟠 Prediction data freshness attention | state={freshness_state} | age={age}s | rows={row_count} | generated_at={generated_at}"
        note = "Panel refresh can be live while prediction data is stale; check this badge separately."
    return {
        "data_freshness_badge_version": WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION,
        "operator_visible_data_freshness_badge": True,
        "data_freshness_badge_state": "prediction_data_fresh" if fresh else "prediction_data_delayed" if delayed else "prediction_data_attention",
        "data_freshness_badge_fresh": fresh,
        "data_freshness_badge_delayed": delayed,
        "data_freshness_badge_attention": stale,
        "data_freshness_badge_message": message,
        "data_freshness_badge_note": note,
        "data_freshness_badge_freshness_state": freshness_state,
        "data_freshness_badge_freshness_label": freshness_label,
        "data_freshness_badge_age_sec": age,
        "data_freshness_badge_prediction_row_count": row_count,
        "data_freshness_badge_generated_at": generated_at,
        "runtime_enablement_allowed": False,
        "view_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def _render_prediction_data_freshness_badge(packet: Mapping[str, Any], *, lang: str) -> None:
    """Render a visible prediction-data freshness badge; display-only."""
    badge = latest_prediction_warroom_data_freshness_badge_packet(packet, lang=lang)
    message = str(badge.get("data_freshness_badge_message") or "")
    if badge.get("data_freshness_badge_fresh") is True:
        st.success(message)
    elif badge.get("data_freshness_badge_delayed") is True:
        st.warning(message)
    else:
        st.warning(message)


def latest_prediction_warroom_refresh_status_rows(packet: Mapping[str, Any] | Any, *, lang: str = "en") -> list[dict[str, str]]:
    """Return compact operator-visible refresh status rows for the WarRoom prediction panel."""
    data = _as_mapping(packet)
    auto_refresh = data.get("warroom_prediction_display_auto_refresh_enabled") is True
    heartbeat = _clean(data.get("refresh_heartbeat_utc")) or "-"
    interval = _clean(data.get("refresh_interval_sec")) or "-"
    broad_reload = data.get("broad_page_reload_disabled") is True
    if lang == "ja":
        return [
            {"status_item": "自動更新", "value": "ON" if auto_refresh else "OFF", "operator_note": "予測パネルの bounded fragment 更新。"},
            {"status_item": "heartbeat UTC", "value": heartbeat, "operator_note": "この値が更新されていれば予測パネルは生きています。"},
            {"status_item": "更新間隔", "value": f"{interval}s", "operator_note": "PS-Q19D prediction panel refresh cadence."},
            {"status_item": "対象", "value": _clean(data.get("refresh_target")) or "-", "operator_note": "更新対象の表示パネル。"},
            {"status_item": "全体再読込", "value": "なし" if broad_reload else "あり", "operator_note": "ページ全体の白化を避ける境界。"},
        ]
    return [
        {"status_item": "auto refresh", "value": "ON" if auto_refresh else "OFF", "operator_note": "Bounded fragment refresh for the prediction panel."},
        {"status_item": "heartbeat UTC", "value": heartbeat, "operator_note": "If this changes, the prediction panel is alive."},
        {"status_item": "interval", "value": f"{interval}s", "operator_note": "PS-Q19D prediction panel refresh cadence."},
        {"status_item": "target", "value": _clean(data.get("refresh_target")) or "-", "operator_note": "Refresh target display panel."},
        {"status_item": "broad reload", "value": "disabled" if broad_reload else "enabled", "operator_note": "Boundary to avoid whole-page whiteout."},
    ]


def _render_refresh_status_strip(packet: Mapping[str, Any], *, lang: str) -> None:
    """Render a compact top-of-panel auto-refresh status strip; display-only."""
    rows = latest_prediction_warroom_refresh_status_rows(packet, lang=lang)
    _render_refresh_live_badge(packet, lang=lang)
    st.caption(
        "PS-Q21C refresh status strip: auto-refresh heartbeat is visible here; "
        "表示専用です。artifact書込、AutoTrade、brokerはありません。"
    )
    columns = st.columns(5)
    for column, row in zip(columns, rows):
        column.metric(str(row.get("status_item") or "-"), str(row.get("value") or "-"))
    with st.expander("PS-Q21C refresh status details", expanded=False):
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(rows), width="stretch", hide_index=True)


def _dominant_summary(read_model: Mapping[str, Any], *, lang: str) -> str:
    rows = latest_prediction_warroom_display_rows(read_model, lang=lang)
    labels = [str(row.get("label_meaning") or row.get("label") or "") for row in rows[:8] if row.get("label")]
    unique = []
    for label in labels:
        if label and label not in unique:
            unique.append(label)
    if not unique:
        return "No prediction rows available." if lang == "en" else "表示できる予測行がありません。"
    prefix = _t(lang, "current_summary_prefix")
    if lang == "ja":
        return f"{prefix}: " + " / ".join(unique[:5]) + "。売買指示ではなく、相場観測用の見立てです。"
    return f"{prefix}: " + " / ".join(unique[:5]) + ". This is observation support, not a trade instruction."


def build_latest_prediction_warroom_display_panel_packet(
    *,
    read_model: Mapping[str, Any] | Any | None = None,
    fragment_enabled: bool = True,
    lang: str = "en",
) -> dict[str, Any]:
    lang = "ja" if lang == "ja" else "en"
    model = dict(_as_mapping(read_model)) if read_model is not None else load_latest_prediction_warroom_read_model_manifest_first(hot_latest_root_hint=_prediction_display_hot_root_hint())
    prediction_rows = latest_prediction_warroom_display_rows(model, lang=lang)
    safety_rows = latest_prediction_warroom_safety_rows(model, lang=lang)
    market_rows = latest_prediction_warroom_market_rows(model, lang=lang)
    field_guide_rows = latest_prediction_warroom_field_guide_rows(lang=lang)
    horizon_expiry_packet = latest_prediction_warroom_horizon_expiry_packet(model, lang=lang)
    action_guidance_source_packet = {"horizon_expiry_packet": horizon_expiry_packet, "freshness_state": model.get("freshness_state"), "age_sec": model.get("age_sec")}
    operator_action_guidance_packet = latest_prediction_warroom_operator_action_guidance_packet(action_guidance_source_packet, lang=lang)
    q26a_japanese_reading_layer = build_latest_prediction_warroom_japanese_reading_layer_packet(model, prediction_rows=prediction_rows, horizon_expiry_packet=horizon_expiry_packet, operator_action_guidance_packet=operator_action_guidance_packet)
    q26b_density_polish = build_latest_prediction_warroom_japanese_density_polish_packet(model, prediction_rows=prediction_rows, horizon_expiry_packet=horizon_expiry_packet, operator_action_guidance_packet=operator_action_guidance_packet)
    failures: list[str] = []
    if not model:
        failures.append("read_model_missing")
    if model.get("read_model_version") != LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION:
        failures.append("read_model_version_mismatch")
    if model.get("read_only") is not True:
        failures.append("read_model_not_read_only")
    if model.get("non_executing") is not True:
        failures.append("read_model_not_non_executing")
    if model.get("display_only") is not True:
        failures.append("read_model_not_display_only")
    for key in (
        "view_artifact_write_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        if model.get(key) is not False:
            failures.append(f"read_model_boundary_not_false:{key}")
    ok = bool(model and not failures)
    refresh_heartbeat_utc = _utc_now_iso()
    prediction_data_generated_at_utc = _clean(model.get("generated_at"))
    packet: dict[str, Any] = {
        "ok": ok,
        "display_panel_version": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION,
        "display_panel_state": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE if ok else "warroom_realtime_prediction_display_panel_blocked",
        "display_language": lang,
        "read_model_version": _clean(model.get("read_model_version")),
        "read_model_ok": model.get("ok") is True,
        "source_artifact_mode": _clean(model.get("source_artifact_mode")) or "legacy",
        "source_artifact_relative_path": _clean(model.get("source_artifact_relative_path")),
        "distributed_reader_ready": model.get("distributed_reader_ready") is True,
        "distributed_stale_vs_legacy": model.get("distributed_stale_vs_legacy") is True,
        "legacy_fallback_ready": model.get("legacy_fallback_ready") is True,
        "generated_at": _clean(model.get("generated_at")),
        "age_sec": model.get("age_sec"),
        "freshness_state": _clean(model.get("freshness_state")),
        "freshness_label": _value_label(model.get("freshness_state"), lang=lang),
        "warning_reason_codes": list(model.get("warning_reason_codes") or []),
        "blocker_reason_codes": list(model.get("blocker_reason_codes") or []),
        "prediction_row_count": len(prediction_rows),
        "prediction_rows": prediction_rows,
        "prediction_rows_display": _column_labels(prediction_rows, lang=lang),
        "market_rows": market_rows,
        "market_rows_display": _column_labels(market_rows, lang=lang),
        "safety_rows": safety_rows,
        "safety_rows_display": _column_labels(safety_rows, lang=lang),
        "field_guide_rows": field_guide_rows,
        "field_guide_rows_display": _column_labels(field_guide_rows, lang=lang),
        "operator_reading_summary": _dominant_summary(model, lang=lang),
        "auto_refresh_version": WARROOM_PREDICTION_DISPLAY_AUTO_REFRESH_VERSION,
        "refresh_status_strip_version": WARROOM_PREDICTION_REFRESH_STATUS_STRIP_VERSION,
        "refresh_live_badge_version": WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION,
        "data_freshness_badge_version": WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION,
        "operator_visible_data_freshness_badge": True,
        "data_freshness_badge_rendered": True,
        "prediction_horizon_expiry_version": WARROOM_PREDICTION_HORIZON_EXPIRY_VERSION,
        "operator_visible_horizon_expiry": True,
        "horizon_expiry_rendered": True,
        "horizon_expiry_packet": horizon_expiry_packet,
        "overall_horizon_expiry_state": horizon_expiry_packet.get("overall_horizon_expiry_state"),
        "short_horizon_expired_or_stale": horizon_expiry_packet.get("short_horizon_expired_or_stale"),
        "prediction_operator_action_guidance_version": WARROOM_PREDICTION_OPERATOR_ACTION_GUIDANCE_VERSION,
        "operator_visible_action_guidance": True,
        "operator_action_guidance_rendered": True,
        "operator_action_guidance_packet": operator_action_guidance_packet,
        "q26a_japanese_reading_layer_packet": q26a_japanese_reading_layer,
        "q26a_japanese_reading_rows": q26a_japanese_reading_layer.get("rows"),
        "q26b_density_polish_packet": q26b_density_polish,
        "q26b_compact_japanese_rows": q26b_density_polish.get("compact_rows"),
        "operator_action_severity": operator_action_guidance_packet.get("operator_action_severity"),
        "prediction_tactical_readiness": operator_action_guidance_packet.get("prediction_tactical_readiness"),
        "wait_for_new_prediction_artifact": operator_action_guidance_packet.get("wait_for_new_prediction_artifact"),
        "prediction_compact_layout_version": WARROOM_PREDICTION_COMPACT_LAYOUT_VERSION,
        "operator_visible_compact_layout": True,
        "compact_layout_rendered": True,
        "compact_layout_packet": latest_prediction_warroom_compact_layout_packet({"operator_action_guidance_packet": operator_action_guidance_packet, "horizon_expiry_packet": horizon_expiry_packet, "age_sec": model.get("age_sec"), "freshness_state": model.get("freshness_state"), "generated_at": model.get("generated_at"), "refresh_heartbeat_utc": refresh_heartbeat_utc}, lang=lang),
        "prediction_density_tuning_version": WARROOM_PREDICTION_DENSITY_TUNING_VERSION,
        "operator_visible_density_tuning": True,
        "density_tuning_rendered": True,
        "density_tuning_packet": latest_prediction_warroom_density_tuning_packet({"operator_action_severity": operator_action_guidance_packet.get("operator_action_severity"), "prediction_tactical_readiness": operator_action_guidance_packet.get("prediction_tactical_readiness")}, lang=lang),
        "operator_visible_refresh_live_badge": True,
        "refresh_live_badge_rendered": True,
        "operator_visible_refresh_status_strip": True,
        "refresh_status_strip_rendered": True,
        "warroom_prediction_display_auto_refresh_enabled": bool(fragment_enabled),
        "operator_visible_refresh_heartbeat": bool(fragment_enabled),
        "refresh_heartbeat_utc": refresh_heartbeat_utc,
        "refresh_heartbeat_jst": _format_jst_from_utc(refresh_heartbeat_utc),
        "prediction_update_visibility_version": WARROOM_PREDICTION_UPDATE_VISIBILITY_VERSION,
        "operator_visible_prediction_update_visibility": True,
        "prediction_update_visibility_rendered": True,
        "prediction_data_generated_at_utc": prediction_data_generated_at_utc,
        "prediction_data_generated_at_jst": _format_jst_from_utc(prediction_data_generated_at_utc),
        "prediction_update_visibility_note": "prediction_data_generated_at_changes_only_when_producer_writes_new_artifact; panel_heartbeat_changes_when_ui_rerenders",
        "refresh_target": "latest_prediction_warroom_read_model_display_panel",
        "auto_refresh_source": "streamlit_fragment_run_every" if fragment_enabled else "disabled_by_fragment_flag",
        "broad_page_reload_disabled": True,
        "fragment_enabled": bool(fragment_enabled),
        "refresh_mode": Q19D_REFRESH_MODE,
        "refresh_interval_sec": Q19D_REFRESH_SEC,
        "page_id": Q19D_PAGE_ID,
        "zone_id": Q19D_ZONE_ID,
        "widget_id": Q19D_WIDGET_ID,
        "panel_failures": failures,
        "operator_caption": _t(lang, "caption"),
        "bilingual_explanation_enabled": True,
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["streamlit_display_panel_render_allowed"] = True
    packet["warroom_display_panel_mounted"] = ok
    packet["fragment_slot_refresh_path_enabled"] = bool(fragment_enabled)
    return packet


def _render_panel_body(*, fragment_enabled: bool = True) -> dict[str, Any]:
    lang = _lang()
    packet = build_latest_prediction_warroom_display_panel_packet(
        fragment_enabled=bool(fragment_enabled),
        lang=lang,
    )
    st.caption(str(packet.get("operator_caption") or "Latest prediction WarRoom display"))
    _render_prediction_compact_operator_header(packet, lang=lang)
    _render_prediction_detail_checks_foldout(packet, lang=lang)
    with st.expander(_t(lang, "reading_title"), expanded=False):
        st.write(_t(lang, "reading_summary"))
        st.info(str(packet.get("operator_reading_summary") or ""))
        guide_rows = list(packet.get("field_guide_rows_display") or [])
        if guide_rows:
            st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(guide_rows), width="stretch", hide_index=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(_t(lang, "metric_freshness"), _clean(packet.get("freshness_label")) or _clean(packet.get("freshness_state")) or "unknown")
    c2.metric(_t(lang, "metric_age"), "-" if packet.get("age_sec") is None else str(packet.get("age_sec")))
    c3.metric(_t(lang, "metric_rows"), str(packet.get("prediction_row_count") or 0))
    c4.metric(_t(lang, "metric_safe"), _value_label("true" if packet.get("ok") is True else "false", lang=lang))
    st.caption(
        _t(lang, "caption_line").format(
            generated_at=packet.get("generated_at") or "-",
            warnings=packet.get("warning_reason_codes") or [],
            blockers=packet.get("blocker_reason_codes") or [],
        )
    )
    q26b_rows = list(packet.get("q26b_compact_japanese_rows") or [])
    if q26b_rows:
        st.caption("PS-Q26B 日本語要点: 予測表示は要点→短期→中期→安全境界の順で読みます。")
        st.caption("PS-Q26C 日本語化: 残っていた状態 token と詳細表の列名を日本語化しています。")
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(q26b_rows), width="stretch", hide_index=True)

    q26a_rows = list(packet.get("q26a_japanese_reading_rows") or [])
    if q26a_rows:
        st.caption("PS-Q26A 日本語読み方: 予測表示は、現在状態と鮮度を確認してから読む operator review 材料です。売買指示ではありません。")
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(q26a_rows), width="stretch", hide_index=True)

    prediction_rows = list(packet.get("prediction_rows_display") or [])
    if prediction_rows:
        st.markdown(f"**{_t(lang, 'prediction_table_title')}**")
        st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(prediction_rows), width="stretch", hide_index=True)
    else:
        st.info(_t(lang, "no_rows"))
    with st.expander(_t(lang, "market_safety_title"), expanded=False):
        market_rows = list(packet.get("market_rows_display") or [])
        if market_rows:
            st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(market_rows), width="stretch", hide_index=True)
        safety_rows = list(packet.get("safety_rows_display") or [])
        if safety_rows:
            st.dataframe(latest_prediction_warroom_q26c_localize_display_rows(safety_rows), width="stretch", hide_index=True)
    st.caption(latest_prediction_warroom_q26e_telemetry_footer_text(packet, lang=lang))
    return packet


def render_latest_prediction_warroom_display_panel(*, fragment_enabled: bool = True) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_panel_body(fragment_enabled=bool(fragment_enabled)))

    lang = _lang()
    meta = live_shell.make_slot_meta(
        Q19D_PAGE_ID,
        Q19D_ZONE_ID,
        Q19D_WIDGET_ID,
        label=_t(lang, "slot_label"),
        tone="primary",
        help_text=_t(lang, "slot_help"),
        refresh_mode=Q19D_REFRESH_MODE,
        priority=17,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=Q19D_REFRESH_SEC,
    )
    return packet_holder or build_latest_prediction_warroom_display_panel_packet(
        fragment_enabled=bool(fragment_enabled),
        lang=lang,
    )
