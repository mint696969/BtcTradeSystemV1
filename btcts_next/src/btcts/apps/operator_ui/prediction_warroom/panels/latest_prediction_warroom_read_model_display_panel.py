# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py
# desc: PS-Q19J display-only WarRoom panel using split bilingual text catalog for the PS-Q19C latest prediction read model. Streamlit presentation only; no runtime/status/prediction writes, scheduler, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    load_latest_prediction_warroom_read_model,
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
LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE = "warroom_realtime_prediction_display_only_panel_mounted"
Q19D_PAGE_ID = "warroom"
Q19D_ZONE_ID = "prediction_overview_zone"
Q19D_WIDGET_ID = "latest_prediction_warroom_read_model_display_panel"
Q19D_REFRESH_MODE = "poll_normal"
Q19D_REFRESH_SEC = 5
# Legacy guard marker kept in the panel after PS-Q19J text-catalog split.
# The footer token text itself is supplied by prediction_warroom.texts.latest_prediction_display_texts.
Q19I_BILINGUAL_EXPLANATION_LEGACY_GUARD_TOKEN = "PS_Q19I_WARROOM_PREDICTION_BILINGUAL_EXPLANATION"

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
    model = dict(_as_mapping(read_model)) if read_model is not None else load_latest_prediction_warroom_read_model()
    prediction_rows = latest_prediction_warroom_display_rows(model, lang=lang)
    safety_rows = latest_prediction_warroom_safety_rows(model, lang=lang)
    market_rows = latest_prediction_warroom_market_rows(model, lang=lang)
    field_guide_rows = latest_prediction_warroom_field_guide_rows(lang=lang)
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
    packet: dict[str, Any] = {
        "ok": ok,
        "display_panel_version": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_VERSION,
        "display_panel_state": LATEST_PREDICTION_WARROOM_DISPLAY_PANEL_STATE if ok else "warroom_realtime_prediction_display_panel_blocked",
        "display_language": lang,
        "read_model_version": _clean(model.get("read_model_version")),
        "read_model_ok": model.get("ok") is True,
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


def _render_panel_body() -> dict[str, Any]:
    lang = _lang()
    packet = build_latest_prediction_warroom_display_panel_packet(
        fragment_enabled=live_shell.supports_streamlit_fragment(),
        lang=lang,
    )
    st.caption(str(packet.get("operator_caption") or "Latest prediction WarRoom display"))
    with st.expander(_t(lang, "reading_title"), expanded=True):
        st.write(_t(lang, "reading_summary"))
        st.info(str(packet.get("operator_reading_summary") or ""))
        guide_rows = list(packet.get("field_guide_rows_display") or [])
        if guide_rows:
            st.dataframe(guide_rows, width="stretch", hide_index=True)
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
    prediction_rows = list(packet.get("prediction_rows_display") or [])
    if prediction_rows:
        st.markdown(f"**{_t(lang, 'prediction_table_title')}**")
        st.dataframe(prediction_rows, width="stretch", hide_index=True)
    else:
        st.info(_t(lang, "no_rows"))
    with st.expander(_t(lang, "market_safety_title"), expanded=False):
        market_rows = list(packet.get("market_rows_display") or [])
        if market_rows:
            st.dataframe(market_rows, width="stretch", hide_index=True)
        safety_rows = list(packet.get("safety_rows_display") or [])
        if safety_rows:
            st.dataframe(safety_rows, width="stretch", hide_index=True)
    st.text(
        f"{_t(lang, 'footer_token')} "
        f"display_language={packet.get('display_language')} "
        f"freshness_state={packet.get('freshness_state')} "
        f"prediction_row_count={packet.get('prediction_row_count')} "
        f"view_artifact_write_allowed=false autotrade=false broker=false"
    )
    return packet


def render_latest_prediction_warroom_display_panel(*, fragment_enabled: bool = True) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_panel_body())

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
