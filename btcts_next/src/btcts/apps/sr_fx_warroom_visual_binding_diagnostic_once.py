# path: ./btcts_next/src/btcts/apps/sr_fx_warroom_visual_binding_diagnostic_once.py
# desc: Read-only diagnostic for SR-FX WarRoom visual binding. No broker calls/no mode changes.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from btcts.collector_vnext.config import load_config
from btcts.apps.operator_ui.components.market_state_bridge import (
    execution_market_context,
    load_execution_market_overview,
    load_execution_market_summary_status_payload,
    load_execution_market_summary_widget_model,
    load_execution_market_prediction_summary_status_payload,
    load_execution_market_prediction_summary_widget_model,
    load_market_summary_status_payload,
)
from btcts.apps.operator_ui.components.market_signal_state import load_market_signal_context
from btcts.apps.operator_ui.components.warroom_header_state import build_warroom_header_state
from btcts.apps.operator_ui.components.market_regime_state import build_market_regime_state
from btcts.apps.operator_ui.components.market_monitor_state import analyze_market_monitor_state
from btcts.apps.operator_ui.components.liquidity_pressure_state import build_liquidity_pressure_state
from btcts.apps.operator_ui.components.trade_flow_state import build_trade_flow_state
from btcts.apps.operator_ui.components.ai_operator_state import analyze_operator_state
from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_sources

STAGE = "sr_fx_warroom_visual_binding_diagnostic_once"
DIAGNOSTIC_VERSION = "sr_fx_warroom_visual_binding_diagnostic.v1"
EXPECTED_PRODUCT_CODE = "FX_BTC_JPY"
EXPECTED_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _state_root() -> Path:
    return load_config().roots()["state"]


def _output_path() -> Path:
    return _state_root() / "operator_ui" / "sr_fx_warroom_visual_binding_diagnostic.json"


def _safe_call(fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        value = fn()
        return {"ok": True, "value": value, "error": None, "error_class": None}
    except Exception as exc:
        return {"ok": False, "value": None, "error": str(exc), "error_class": exc.__class__.__name__}


def _materialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _materialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_materialize(v) for v in value]
    if hasattr(value, "__dict__"):
        return {str(k): _materialize(v) for k, v in vars(value).items()}
    return str(value)


def _extract_identity(payload: Any) -> dict[str, Any]:
    data = _materialize(payload)
    if not isinstance(data, dict):
        return {}
    return {
        "product_code": data.get("product_code") or data.get("execution_product_code") or data.get("symbol_raw"),
        "market_uid": data.get("market_uid") or data.get("execution_market_uid"),
        "symbol_raw": data.get("symbol_raw"),
        "service_input_role": data.get("service_input_role"),
        "source": data.get("source") or data.get("source_kind") or data.get("source_label"),
        "freshness": data.get("freshness"),
        "is_stale": data.get("is_stale"),
        "continuity_state": data.get("continuity_state"),
        "trust_state": data.get("trust_state"),
        "interpretation_bucket": data.get("interpretation_bucket"),
    }


def _identity_blocker(name: str, payload: Any) -> str | None:
    identity = _extract_identity(payload)
    product = identity.get("product_code") or identity.get("symbol_raw")
    market_uid = identity.get("market_uid")
    if product and str(product) != EXPECTED_PRODUCT_CODE:
        return f"{name}_not_execution_product"
    if market_uid and str(market_uid) != EXPECTED_MARKET_UID:
        return f"{name}_not_execution_market"
    return None


def _source_status(name: str, call: dict[str, Any]) -> dict[str, Any]:
    value = _materialize(call.get("value"))
    present = bool(value)
    identity = _extract_identity(value)
    product = identity.get("product_code") or identity.get("symbol_raw")
    market_uid = identity.get("market_uid")
    identity_ok = (
        (not product or str(product) == EXPECTED_PRODUCT_CODE)
        and (not market_uid or str(market_uid) == EXPECTED_MARKET_UID)
    )
    return {
        "name": name,
        "call_ok": bool(call.get("ok")),
        "present": present,
        "identity_ok": bool(identity_ok),
        "identity": identity,
        "error": call.get("error"),
        "error_class": call.get("error_class"),
        "preview": value if isinstance(value, dict) else None,
    }


def build_sr_fx_warroom_visual_binding_diagnostic_payload() -> dict[str, Any]:
    ctx_call = _safe_call(execution_market_context)
    source_calls = {
        "execution_market_overview": _safe_call(load_execution_market_overview),
        "execution_market_summary_status": _safe_call(load_execution_market_summary_status_payload),
        "execution_market_summary_widget": _safe_call(load_execution_market_summary_widget_model),
        "execution_market_prediction_status": _safe_call(load_execution_market_prediction_summary_status_payload),
        "execution_market_prediction_widget": _safe_call(load_execution_market_prediction_summary_widget_model),
        "legacy_default_market_summary_status": _safe_call(load_market_summary_status_payload),
        "market_signal_context": _safe_call(load_market_signal_context),
        "warroom_header_state": _safe_call(build_warroom_header_state),
        "market_regime_state": _safe_call(build_market_regime_state),
        "market_monitor_state": _safe_call(analyze_market_monitor_state),
        "liquidity_pressure_state": _safe_call(build_liquidity_pressure_state),
        "trade_flow_state": _safe_call(build_trade_flow_state),
        "ai_operator_state": _safe_call(analyze_operator_state),
        "ai_operator_display_sources": _safe_call(load_operator_display_sources),
    }
    source_status = {
        name: _source_status(name, call)
        for name, call in source_calls.items()
    }

    required_present = {
        "warroom_header_state": source_status["warroom_header_state"]["present"],
        "market_regime_state": source_status["market_regime_state"]["present"],
        "market_monitor_state": source_status["market_monitor_state"]["present"],
        "liquidity_pressure_state": source_status["liquidity_pressure_state"]["present"],
        "trade_flow_state": source_status["trade_flow_state"]["present"],
        "ai_operator_state": source_status["ai_operator_state"]["present"],
    }
    blocked_by = [f"{name}_missing" for name, ok in required_present.items() if not ok]

    legacy_status = source_status["legacy_default_market_summary_status"]
    legacy_identity = legacy_status.get("identity") or {}
    warnings: list[str] = []
    if str(legacy_identity.get("product_code") or legacy_identity.get("symbol_raw") or "") == "BTC_JPY":
        warnings.append("legacy_default_market_summary_is_btc_jpy_informational_only")

    display_sources = _materialize(source_calls["ai_operator_display_sources"].get("value"))
    if isinstance(display_sources, dict):
        for display_key in ("summary_widget", "prediction_widget", "tactic_context"):
            blocker = _identity_blocker(
                f"ai_operator_{display_key}",
                display_sources.get(display_key),
            )
            if blocker:
                blocked_by.append(blocker)

    blocked_by = list(dict.fromkeys(blocked_by))
    return {
        "stage": STAGE,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now_iso(),
        "ok": not blocked_by,
        "context": _materialize(ctx_call.get("value")),
        "required_present": required_present,
        "source_status": source_status,
        "blocked_by": blocked_by,
        "warnings": warnings,
        "decision": "warroom_visual_binding_ok" if not blocked_by else "fix_warroom_visual_binding_before_closing_data_ui_gate",
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    }


def write_sr_fx_warroom_visual_binding_diagnostic(payload: Mapping[str, Any]) -> Path:
    out = _output_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return out


def main() -> int:
    try:
        payload = build_sr_fx_warroom_visual_binding_diagnostic_payload()
        out = write_sr_fx_warroom_visual_binding_diagnostic(payload)
        payload = {**payload, "paths": {"diagnostic_path": str(out)}}
    except Exception as exc:
        payload = {
            "stage": STAGE,
            "diagnostic_version": DIAGNOSTIC_VERSION,
            "generated_at": _utc_now_iso(),
            "ok": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_warroom_visual_binding_diagnostic_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
        try:
            out = write_sr_fx_warroom_visual_binding_diagnostic(payload)
            payload["paths"] = {"diagnostic_path": str(out)}
        except Exception:
            pass
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
