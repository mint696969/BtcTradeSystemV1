# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py
# desc: PS-Q18AK freshness/error fallback polish for latest_prediction_summary_widget auto-refresh display. UI-only fragment refresh companion; no runtime writes, AutoTrade, broker, parameter, or ledger behavior.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
)

LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ak_freshness_error_fallback_panel.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION = "prediction_warroom.latest_prediction_summary_widget.q18ak_japanese_localization.ps_q26g.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_ACK = "PS_Q18AK_ADD_FRESHNESS_ERROR_FALLBACK_POLISH_TO_AUTO_REFRESH_DISPLAY_ONLY"
LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_STATE = "auto_refresh_display_freshness_error_fallback_visible"
Q18AK_PAGE_ID = "warroom"
Q18AK_ZONE_ID = "prediction_overview_zone"
Q18AK_WIDGET_ID = "latest_prediction_summary_widget_freshness_error_fallback_panel"
Q18AK_REFRESH_MODE = "poll_normal"
Q18AK_DEFAULT_REFRESH_SEC = 5
FRESH_THRESHOLD_SEC = 900
DELAYED_THRESHOLD_SEC = 3600

TRUE_BOUNDARIES = (
    "read_only",
    "non_executing",
    "display_only",
    "freshness_error_fallback_panel_only",
    "q18aj_bounded_auto_refresh_panel_consumed",
    "auto_refresh_enabled",
    "fragment_slot_refresh_path_enabled",
    "partial_update_enabled",
    "freshness_monitor_enabled",
    "error_fallback_visible",
    "operator_safe_fallback_reason_codes_visible",
    "broad_page_reload_disabled",
)

FALSE_BOUNDARIES = (
    "real_prediction_widget_rendering_allowed",
    "real_prediction_widget_render_invoked",
    "streamlit_real_widget_render_invoked",
    "component_runtime_binding_allowed",
    "component_props_bound_to_runtime",
    "runtime_artifact_write_allowed",
    "status_artifact_write_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_send_to_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _clean(value: Any) -> str:
    return "" if value is None else str(value)


def _bool_token(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return _clean(value).lower()


def _join_reason_codes(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    return _clean(value)


def _parse_utc(value: str) -> datetime | None:
    text = _clean(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now_utc(value: str | None = None) -> datetime:
    parsed = _parse_utc(value or "")
    if parsed is not None:
        return parsed
    return datetime.now(timezone.utc)


def _freshness_state(age_sec: int | None) -> str:
    if age_sec is None:
        return "unknown"
    if age_sec <= FRESH_THRESHOLD_SEC:
        return "fresh"
    if age_sec <= DELAYED_THRESHOLD_SEC:
        return "delayed"
    return "stale"


def _fallback_reasons(*, q18aj_ok: bool, generated_at: str, age_sec: int | None, state: str) -> list[str]:
    reasons: list[str] = []
    if not q18aj_ok:
        reasons.append("auto_refresh_source_packet_not_ok")
    if not generated_at:
        reasons.append("source_generated_at_missing")
    if age_sec is None:
        reasons.append("source_generated_at_unparseable")
    if state == "delayed":
        reasons.append("source_generated_at_delayed")
    if state == "stale":
        reasons.append("source_generated_at_stale")
    if not reasons:
        reasons.append("source_freshness_ok")
    return reasons


def build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
    *,
    supplied_q18aj_bounded_auto_refresh_packet: Mapping[str, Any] | Any | None = None,
    now_utc: str | None = None,
    fragment_supported: bool = True,
    ui_auto_refresh: bool = True,
) -> dict[str, Any]:
    source = _as_mapping(supplied_q18aj_bounded_auto_refresh_packet)
    if not source:
        source = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(
            fragment_supported=fragment_supported,
            ui_auto_refresh=ui_auto_refresh,
        )
    generated_at = _clean(source.get("component_source_generated_at"))
    source_dt = _parse_utc(generated_at)
    observed_now = _now_utc(now_utc)
    age_sec: int | None = None
    if source_dt is not None:
        age_sec = max(0, int((observed_now - source_dt).total_seconds()))
    state = _freshness_state(age_sec)
    q18aj_ok = source.get("ok") is True
    reasons = _fallback_reasons(q18aj_ok=q18aj_ok, generated_at=generated_at, age_sec=age_sec, state=state)
    failures: list[str] = []
    if not q18aj_ok:
        failures.append("q18aj_bounded_auto_refresh_packet_not_ok")
    if source.get("auto_refresh_enabled") is not True:
        failures.append("q18aj_auto_refresh_not_enabled")
    if source.get("fragment_slot_refresh_path_enabled") is not True:
        failures.append("q18aj_fragment_slot_refresh_not_enabled")
    if source.get("broad_page_reload_disabled") is not True:
        failures.append("q18aj_broad_page_reload_not_disabled")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed", "parameter_apply_allowed", "ledger_append_allowed"):
        if source.get(key) is not False:
            failures.append(f"q18aj_boundary_not_false:{key}")
    ok = bool(not failures and state != "unknown")
    packet: dict[str, Any] = {
        "ok": ok,
        "freshness_panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_VERSION,
        "freshness_panel_ack": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_ACK,
        "freshness_panel_state": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_FRESHNESS_ERROR_FALLBACK_PANEL_STATE if ok else "freshness_error_fallback_panel_blocked_or_unknown",
        "source_q18aj_bounded_auto_refresh_ready": q18aj_ok,
        "component_source_generated_at": generated_at,
        "observed_now_utc": observed_now.isoformat().replace("+00:00", "Z"),
        "source_age_sec": age_sec,
        "freshness_state": state,
        "fresh_threshold_sec": FRESH_THRESHOLD_SEC,
        "delayed_threshold_sec": DELAYED_THRESHOLD_SEC,
        "stale_source_warning_visible": state in {"delayed", "stale", "unknown"},
        "safe_fallback_reason_codes": reasons,
        "fallback_reason_count": len(reasons),
        "auto_refresh_enabled": source.get("auto_refresh_enabled") is True,
        "fragment_slot_refresh_path_enabled": source.get("fragment_slot_refresh_path_enabled") is True,
        "partial_update_enabled": source.get("partial_update_enabled") is True,
        "broad_page_reload_disabled": True,
        "refresh_mode": _clean(source.get("refresh_mode")) or Q18AK_REFRESH_MODE,
        "refresh_interval_sec": int(source.get("refresh_interval_sec") or Q18AK_DEFAULT_REFRESH_SEC),
        "page_id": Q18AK_PAGE_ID,
        "zone_id": Q18AK_ZONE_ID,
        "widget_id": Q18AK_WIDGET_ID,
        "panel_failures": failures,
        "operator_caption": "PS-Q26G Q18AK: 自動更新された latest prediction の鮮度と安全fallback理由を表示します。UI表示のみで、売買/runtime挙動はありません。",
        "recommended_next_slice": "UI smoke/manual visual check へ進みます。AutoTrade・broker・parameter・ledger・runtime書込は無効のままです。",
    }
    packet.update({key: ok for key in TRUE_BOUNDARIES})
    packet.update({key: False for key in FALSE_BOUNDARIES})
    packet["read_only"] = True
    packet["non_executing"] = True
    packet["display_only"] = True
    packet["freshness_monitor_enabled"] = True
    packet["error_fallback_visible"] = True
    packet["operator_safe_fallback_reason_codes_visible"] = True
    packet["broad_page_reload_disabled"] = True
    return packet



def _q26g_bool_ja(value: Any) -> str:
    if value is True:
        return "はい"
    if value is False:
        return "いいえ"
    text = _clean(value).lower()
    if text == "true":
        return "はい"
    if text == "false":
        return "いいえ"
    return _clean(value) or "-"


def _q26g_freshness_ja(value: Any) -> str:
    return {
        "fresh": "新しい",
        "delayed": "やや遅延",
        "stale": "古い",
        "unknown": "不明",
    }.get(_clean(value), _clean(value) or "-")


def _q26g_reason_ja(value: Any) -> str:
    mapping = {
        "auto_refresh_source_packet_not_ok": "自動更新元packetが未OK",
        "source_generated_at_missing": "生成時刻が欠落",
        "source_generated_at_unparseable": "生成時刻を解釈できない",
        "source_generated_at_delayed": "生成時刻がやや古い",
        "source_generated_at_stale": "生成時刻が古い",
        "source_freshness_ok": "鮮度OK",
    }
    if isinstance(value, (list, tuple)):
        return ", ".join(mapping.get(str(item), str(item)) for item in value) or "なし"
    text = _clean(value)
    for token, label in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(token, label)
    return text or "なし"


def latest_prediction_summary_widget_q18ak_visible_plain_text(packet: Mapping[str, Any] | Any) -> str:
    data = _as_mapping(packet)
    return (
        "PS-Q26G Q18AK 鮮度/fallback確認: "
        f"鮮度={_q26g_freshness_ja(data.get('freshness_state'))} / "
        f"経過={_clean(data.get('source_age_sec')) or '-'}秒 / "
        f"fallback理由={_q26g_reason_ja(data.get('safe_fallback_reason_codes'))} / "
        f"観測時刻={_clean(data.get('observed_now_utc')) or '-'} / "
        f"予測生成時刻={_clean(data.get('component_source_generated_at')) or '-'} / "
        f"自動更新={_q26g_bool_ja(data.get('auto_refresh_enabled'))} / "
        "広域ページreload=なし / 書込=なし / AutoTrade=なし / broker=なし"
    )


def latest_prediction_summary_widget_q18ak_visible_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        {"確認項目": "鮮度", "状態": _q26g_freshness_ja(data.get("freshness_state")), "見るポイント": "fresh/delayed/stale/unknown を日本語で確認します。"},
        {"確認項目": "経過秒", "状態": _clean(data.get("source_age_sec")) or "-", "見るポイント": "予測生成時刻から観測時刻までの秒数です。"},
        {"確認項目": "予測生成時刻", "状態": _clean(data.get("component_source_generated_at")) or "-", "見るポイント": "latest prediction artifact の生成時刻です。"},
        {"確認項目": "観測時刻", "状態": _clean(data.get("observed_now_utc")) or "-", "見るポイント": "UIが鮮度を見た時刻です。"},
        {"確認項目": "fallback理由", "状態": _q26g_reason_ja(data.get("safe_fallback_reason_codes")), "見るポイント": "表示用の安全fallback理由です。実行挙動はありません。"},
        {"確認項目": "自動更新", "状態": _q26g_bool_ja(data.get("auto_refresh_enabled")), "見るポイント": "WarRoom表示の自動更新です。予測生成ではありません。"},
        {"確認項目": "広域ページreload", "状態": "なし", "見るポイント": "fragment path のみです。"},
        {"確認項目": "AutoTrade / broker", "状態": "なし", "見るポイント": "AutoTrade trigger と broker/private API は無効です。"},
    ]



def _q26g_stale_q18aj_source_packet() -> dict[str, Any]:
    return {
        "ok": True,
        "component_source_generated_at": "2026-06-24T03:00:00Z",
        "auto_refresh_enabled": True,
        "fragment_slot_refresh_path_enabled": True,
        "partial_update_enabled": True,
        "broad_page_reload_disabled": True,
        "refresh_mode": Q18AK_REFRESH_MODE,
        "refresh_interval_sec": Q18AK_DEFAULT_REFRESH_SEC,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "ledger_append_allowed": False,
    }

def build_latest_prediction_summary_widget_q18ak_japanese_localization_packet() -> dict[str, Any]:
    sample = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        supplied_q18aj_bounded_auto_refresh_packet=_q26g_stale_q18aj_source_packet(),
        now_utc="2026-06-24T04:57:45Z",
    )
    return {
        "ok": True,
        "localization_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION,
        "visible_plain_text_japanese_localized": True,
        "visible_rows_japanese_localized": True,
        "legacy_searchable_plain_text_preserved": True,
        "sample_visible_plain_text": latest_prediction_summary_widget_q18ak_visible_plain_text(sample),
        "sample_visible_row_count": len(latest_prediction_summary_widget_q18ak_visible_display_rows(sample)),
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

def latest_prediction_summary_widget_q18ak_searchable_plain_text(packet: Mapping[str, Any] | Any) -> str:
    data = _as_mapping(packet)
    return (
        "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS "
        f"freshness_state={_clean(data.get('freshness_state'))} "
        f"safe_fallback_reason_codes={_join_reason_codes(data.get('safe_fallback_reason_codes'))} "
        f"observed_now_utc={_clean(data.get('observed_now_utc'))} "
        f"source_age_sec={_clean(data.get('source_age_sec'))} "
        f"component_source_generated_at={_clean(data.get('component_source_generated_at'))} "
        f"auto_refresh_enabled={_bool_token(data.get('auto_refresh_enabled'))} "
        f"broad_page_reload={_bool_token(False)} "
        f"autotrade={_bool_token(data.get('autotrade_trigger_allowed'))} "
        f"broker={_bool_token(data.get('broker_private_api_allowed'))}"
    )


def latest_prediction_summary_widget_q18ak_display_rows(packet: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    data = _as_mapping(packet)
    return [
        {"item": "freshness_state", "value": _clean(data.get("freshness_state")), "note": "fresh / delayed / stale / unknown"},
        {"item": "source_age_sec", "value": _clean(data.get("source_age_sec")), "note": "Age from component_source_generated_at to observed_now_utc."},
        {"item": "component_source_generated_at", "value": _clean(data.get("component_source_generated_at")), "note": "Latest prediction timestamp currently visible in WarRoom."},
        {"item": "observed_now_utc", "value": _clean(data.get("observed_now_utc")), "note": "UI observation time for freshness display."},
        {"item": "safe_fallback_reason_codes", "value": ", ".join(str(item) for item in data.get("safe_fallback_reason_codes") or []), "note": "Operator-visible fallback reasons; no execution behavior."},
        {"item": "auto_refresh_enabled", "value": _clean(data.get("auto_refresh_enabled")), "note": "WarRoom display auto-refresh remains enabled."},
        {"item": "broad_page_reload", "value": "false", "note": "Fragment path only; broad page reload remains disabled."},
        {"item": "autotrade_broker", "value": "false", "note": "AutoTrade and broker APIs remain disabled."},
    ]


def _render_q18ak_body() -> dict[str, Any]:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        fragment_supported=live_shell.supports_streamlit_fragment(),
        ui_auto_refresh=True,
    )
    st.caption(str(packet.get("operator_caption") or "PS-Q18AK freshness/error fallback panel"))
    st.caption(latest_prediction_summary_widget_q18ak_visible_plain_text(packet))
    st.text(latest_prediction_summary_widget_q18ak_visible_plain_text(packet))
    rows = latest_prediction_summary_widget_q18ak_visible_display_rows(packet)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    return packet


def render_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel(
    *,
    fragment_enabled: bool = True,
) -> Mapping[str, Any]:
    packet_holder: dict[str, Any] = {}

    def _render_body() -> None:
        packet_holder.update(_render_q18ak_body())

    meta = live_shell.make_slot_meta(
        Q18AK_PAGE_ID,
        Q18AK_ZONE_ID,
        Q18AK_WIDGET_ID,
        label="予測最新 鮮度 / fallback",
        tone="primary",
        help_text="自動更新された latest prediction の鮮度と安全fallbackを表示します。AutoTrade、broker、parameter、ledger、runtime書込はありません。",
        refresh_mode=Q18AK_REFRESH_MODE,
        priority=19,
        overlay_enabled=False,
        partial_update_enabled=True,
    )
    live_shell.render_fragment_slot(
        meta,
        _render_body,
        enabled=bool(fragment_enabled),
        default_sec=Q18AK_DEFAULT_REFRESH_SEC,
    )
    return packet_holder or build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        fragment_supported=live_shell.supports_streamlit_fragment(),
        ui_auto_refresh=bool(fragment_enabled),
    )
