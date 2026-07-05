# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/copy_packet_view.py
# desc: Lightweight GPT analysis request builder for WarRoom chart/scenario review. Keeps copied text compact and points GPT to repo/data Actions.

from __future__ import annotations

import json
from typing import Any, Mapping

GPT_COPY_PACKET_VERSION = "warroom_gpt_review_packet.2026_07_05.v3_action_plan"


def _compact_mapping(value: object, *, allowed_keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    return {key: value.get(key) for key in allowed_keys if key in value}


def _iso_date(value: object) -> str | None:
    if not isinstance(value, str) or len(value) < 10:
        return None
    return value[:10]


def _iso_time(value: object) -> str | None:
    if not isinstance(value, str) or "T" not in value:
        return None
    return value.split("T", 1)[1].replace("Z", "").split("+", 1)[0]


def _recommended_actions(*, primary_market_trade_path: object, x_domain: Mapping[str, Any]) -> list[dict[str, Any]]:
    start = x_domain.get("start")
    end = x_domain.get("end")
    trade_path = primary_market_trade_path if isinstance(primary_market_trade_path, str) and primary_market_trade_path else None
    actions: list[dict[str, Any]] = [
        {
            "tool": "data_latest",
            "purpose": "read current hot runtime state and recent state candidates",
            "args": {"kind": "state", "max_files": 5},
        }
    ]
    if trade_path:
        actions.append(
            {
                "tool": "data_slice",
                "purpose": "inspect raw D-hot market.trade records around the selected chart range",
                "args": {
                    "path": trade_path,
                    "date_from": _iso_date(start),
                    "date_to": _iso_date(end),
                    "time_from": _iso_time(start),
                    "time_to": _iso_time(end),
                    "max_lines": 200,
                    "max_bytes": 60000,
                },
            }
        )
    actions.append(
        {
            "tool": "repo_read_batch",
            "purpose": "inspect deterministic chart logic and D-hot bootstrap adapter, not UI rendering only",
            "args": {
                "paths": [
                    "btcts_next/src/btcts/prediction/warroom_chart_series.py",
                    "btcts_next/src/btcts/prediction/warroom_chart_history_bootstrap.py",
                    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/copy_packet_view.py",
                ],
                "max_chars_per_file": 16000,
                "max_total_chars": 48000,
            },
        }
    )
    return actions


def _copy_chart_request(chart_render_summary: Mapping[str, Any] | None) -> dict[str, Any]:
    summary = dict(chart_render_summary or {})
    snapshot = dict(summary.get("gpt_review_chart_snapshot") or {})
    latest = _compact_mapping(snapshot.get("latest"), allowed_keys=("ts", "topic", "role", "price", "freshness_label", "bid", "ask", "mid", "spread"))
    x_domain = _compact_mapping(snapshot.get("x_domain"), allowed_keys=("start", "end", "latest_anchored"))
    candle_summary = _compact_mapping(snapshot.get("candle_summary"), allowed_keys=("rows", "closed", "forming", "source", "true_trade_ohlcv_connected"))
    dhot_bootstrap = _compact_mapping(
        snapshot.get("dhot_bootstrap"),
        allowed_keys=("ok", "version", "source_path", "source_root", "source_root_reason", "rows_read", "rows_returned", "tail_bytes", "max_rows", "error"),
    )
    trust_boundary = _compact_mapping(
        snapshot.get("trust_boundary"),
        allowed_keys=("chart_logic_owner", "ui_role", "input_source", "latest_candle_may_change", "closed_candles_should_not_change_in_session", "official_exchange_ohlc_connected", "manual_review_only"),
    )
    primary_market_trade_path = dhot_bootstrap.get("source_path")
    return {
        "schema_version": "warroom_chart_analysis_request.v1",
        "instruction_to_gpt": "Use Actions/data tools to inspect the referenced D-hot/repo artifacts when deeper evidence is needed. Do not rely on this copied text as the full dataset.",
        "display_mode": snapshot.get("display_mode"),
        "viewport_label": snapshot.get("viewport_label"),
        "viewport_minutes": snapshot.get("viewport_minutes"),
        "source_label": snapshot.get("source_label"),
        "source_notice": snapshot.get("source_notice"),
        "history_rows": snapshot.get("history_rows"),
        "visible_rows": snapshot.get("visible_rows"),
        "latest": latest,
        "x_domain": x_domain,
        "candle_summary": candle_summary,
        "dhot_bootstrap": dhot_bootstrap,
        "trust_boundary": trust_boundary,
        "analysis_target": {
            "scope": "currently selected WarRoom chart viewport",
            "time_range": x_domain,
            "latest_point": latest,
            "manual_operator_question": "Analyze this selected chart range using Actions; do not infer from embedded rows alone.",
        },
        "data_access_hints": {
            "hot_data_root": "D:/btc_ts_hot",
            "cold_data_root": "E:/btc_ts",
            "cold_root_policy": "Use cold archive only when the operator explicitly asks for archive/replay/historical validation.",
            "primary_runtime_state": "state/collector_vnext/unified_market_state_status.json",
            "primary_market_trade_path": primary_market_trade_path,
            "recommended_actions": _recommended_actions(primary_market_trade_path=primary_market_trade_path, x_domain=x_domain),
        },
        "copy_weight_policy": {
            "embedded_raw_rows": False,
            "embedded_visible_price_rows": False,
            "embedded_candles": False,
            "embedded_board_band": False,
            "reason": "Keep chat copy lightweight; GPT can read source artifacts through Actions.",
        },
    }


def build_gpt_copy_packet(
    *,
    market_strip: Mapping[str, Any],
    guidance: Mapping[str, Any],
    chart_packet: Mapping[str, Any],
    cards_packet: Mapping[str, Any],
    chart_render_summary: Mapping[str, Any] | None = None,
) -> str:
    chart_request = _copy_chart_request(chart_render_summary)
    payload = {
        "schema_version": GPT_COPY_PACKET_VERSION,
        "purpose": "manual trade observation review request; read-only; no order action",
        "how_to_use": "Paste this lightweight request to GPT, then ask GPT to follow operator_focus.selected_chart_range.data_access_hints.recommended_actions for bounded D-hot/repo inspection.",
        "market": {
            "symbol": market_strip.get("symbol"),
            "best_bid": market_strip.get("best_bid"),
            "best_ask": market_strip.get("best_ask"),
            "spread": market_strip.get("spread"),
            "spread_bps": market_strip.get("spread_bps"),
            "source": market_strip.get("source"),
            "last_event_ts": market_strip.get("last_event_ts"),
        },
        "operator_focus": {
            "selected_chart_range": chart_request,
            "scenario_guidance": {
                "scenario": guidance.get("scenario"),
                "confidence": guidance.get("confidence"),
                "rationale": guidance.get("rationale"),
                "evidence_summary": guidance.get("evidence", [])[:4] if isinstance(guidance.get("evidence", []), list) else [],
                "observation_only": True,
            },
            "prediction_cards_scope": "deferred_to_next_thread_context_only",
        },
        "safety": {
            "read_only": True,
            "manual_review_only": True,
            "websocket_send_enabled": False,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _copy_packet_range_summary(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except Exception:  # noqa: BLE001
        return {
            "ok": False,
            "range_label": "GPTコピー対象範囲: JSON解析不可",
            "source_label": "D-hot source: -",
            "rows_label": "rows: -",
        }
    selected = dict(((payload.get("operator_focus") or {}).get("selected_chart_range") or {}))
    x_domain = dict(selected.get("x_domain") or {})
    dhot = dict(selected.get("dhot_bootstrap") or {})
    start = x_domain.get("start") or "-"
    end = x_domain.get("end") or "-"
    source_path = dhot.get("source_path") or selected.get("data_access_hints", {}).get("primary_market_trade_path") or "-"
    history_rows = selected.get("history_rows")
    visible_rows = selected.get("visible_rows")
    return {
        "ok": True,
        "range_label": f"GPTコピー対象範囲: {start} ～ {end}",
        "source_label": f"D-hot source: {source_path}",
        "rows_label": f"rows: history={history_rows} / visible={visible_rows}",
    }


def build_gpt_copy_status_summary(text: str) -> str:
    summary = _copy_packet_range_summary(text)
    range_label = str(summary.get("range_label") or "GPTコピー対象範囲: -")
    rows_label = str(summary.get("rows_label") or "rows: -")
    source_label = str(summary.get("source_label") or "D-hot source: -")
    source_ready = "sourceあり"
    if source_label.strip() in {"D-hot source: -", "D-hot source:"} or source_label.rstrip().endswith(": -"):
        source_ready = "source未確認"
    range_text = range_label.replace("GPTコピー対象範囲: ", "")
    return f"GPTコピー準備: {range_text} / {rows_label} / {source_ready}"


def render_gpt_copy_packet(text: str, st_api: Any) -> dict[str, Any]:
    summary = _copy_packet_range_summary(text)
    status_summary = build_gpt_copy_status_summary(text)
    st_api.caption(status_summary)
    with st_api.expander("GPTへコピーするチャート範囲", expanded=False):
        st_api.caption(summary["range_label"])
        st_api.caption(summary["rows_label"])
        st_api.caption(summary["source_label"])
        st_api.caption("操作: 下の欄をクリック → Ctrl+A → Ctrl+C → GPTに貼り付け。軽量コピーなので生データ本体は含めません。")
        st_api.text_area("GPTに貼る軽量リクエスト", value=text, height=220)
    return {
        "ok": True,
        "copy_packet_rendered": True,
        "copy_packet_version": GPT_COPY_PACKET_VERSION,
        "copy_packet_chars": len(text),
        "copy_status_summary": status_summary,
        "lightweight_request": True,
        "copy_range_label": summary["range_label"],
        "copy_source_label": summary["source_label"],
        "copy_rows_label": summary["rows_label"],
        "read_only": True,
    }
