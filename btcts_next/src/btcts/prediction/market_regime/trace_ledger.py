# path: ./btcts_next/src/btcts/prediction/market_regime/trace_ledger.py
# desc: Market-regime prediction trace-ledger MVP. Builds compact trace rows and appends partitioned JSONL trace artifacts only; no raw market duplication, UI, scheduler, broker, AutoTrade, or trade ledger behavior.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from .artifact_contracts import MARKET_REGIME_TRACE_SCHEMA_VERSION
from .contracts import MarketRegimePredictionPacket
from .features import MarketRegimeFeatureBundle

MARKET_REGIME_TRACE_LEDGER_VERSION = "prediction.market_regime.trace_ledger.2026_07_08.v1"
TRACE_PART_FILENAME = "part-00001.jsonl"
TRACE_META_FILENAME = "part-00001.meta.json"
_MAX_TRACE_ROW_BYTES = 128 * 1024
_FORBIDDEN_RAW_KEYS = {
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
    "bids",
    "asks",
    "trades",
    "executions",
}


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _date_hour(generated_at: str) -> tuple[str, str]:
    text = str(generated_at)
    date = text[:10] if len(text) >= 10 else "unknown-date"
    hour = text[11:13] if len(text) >= 13 and text[10:11] == "T" else "00"
    if len(date) != 10 or date.count("-") != 2:
        date = "unknown-date"
    if len(hour) != 2 or not hour.isdigit():
        hour = "00"
    return date, hour


def trace_ledger_part_relpath(generated_at: str) -> str:
    date, hour = _date_hour(generated_at)
    return f"prediction/market_regime/ledgers/date={date}/hour={hour}/{TRACE_PART_FILENAME}"


def trace_ledger_meta_relpath(generated_at: str) -> str:
    date, hour = _date_hour(generated_at)
    return f"prediction/market_regime/ledgers/date={date}/hour={hour}/{TRACE_META_FILENAME}"


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _has_forbidden_raw_keys(nested):
                return True
    elif isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def _feature_summary(bundle: MarketRegimeFeatureBundle) -> Dict[str, Any]:
    group_counts: dict[str, int] = {}
    available_by_group: dict[str, int] = {}
    top_signals: list[dict[str, Any]] = []
    for signal in bundle.signals:
        group = _enum_value(signal.feature_group)
        group_counts[group] = group_counts.get(group, 0) + 1
        if signal.available:
            available_by_group[group] = available_by_group.get(group, 0) + 1
            if len(top_signals) < 24:
                top_signals.append({
                    "feature_group": group,
                    "name": signal.name,
                    "available": True,
                    "weight_hint": float(signal.weight_hint),
                    "source_refs": list(signal.source_refs),
                })
    return {
        "logic_version": bundle.logic_version,
        "source_snapshot_ok": bundle.source_snapshot_ok,
        "available_signal_count": bundle.available_signal_count(),
        "signal_count_by_group": group_counts,
        "available_signal_count_by_group": available_by_group,
        "missing_sources": list(bundle.missing_sources),
        "warnings": list(bundle.warnings),
        "coverage": [item.to_dict() for item in bundle.coverage],
        "top_available_signals": top_signals,
    }


def _prediction_summary(packet: MarketRegimePredictionPacket) -> Dict[str, Any]:
    horizons: list[dict[str, Any]] = []
    for prediction in packet.predictions:
        horizons.append({
            "horizon": prediction.horizon_label,
            "horizon_sec": int(prediction.horizon_sec),
            "horizon_key": prediction.horizon_key,
            "regime_code": _enum_value(prediction.regime_code),
            "confidence_percent": int(prediction.confidence_percent),
            "evidence_quality": _enum_value(prediction.evidence_quality),
            "freshness_state": _enum_value(prediction.freshness_state),
            "driver_count": len(prediction.drivers),
            "warning_count": len(prediction.warnings),
            "missing_source_count": len(prediction.missing_sources),
            "invalidation_hint_count": len(prediction.invalidation_hints),
            "parameter_set_id": prediction.parameter_set_id,
        })
    return {
        "logic_version": packet.logic_version,
        "generated_at": packet.generated_at,
        "horizon_count": len(horizons),
        "horizons": horizons,
        "missing_sources": list(packet.missing_sources),
        "warnings": list(packet.warnings),
    }


def _signal_summary(signal_score_report: Mapping[str, Any]) -> Dict[str, Any]:
    horizons: list[dict[str, Any]] = []
    for row in signal_score_report.get("horizons", []):
        if not isinstance(row, Mapping):
            continue
        horizons.append({
            "horizon": row.get("horizon"),
            "horizon_sec": row.get("horizon_sec"),
            "horizon_key": row.get("horizon_key"),
            "top_vote_ids": [vote.get("signal_id") for vote in row.get("signal_votes_top_n", [])[:5] if isinstance(vote, Mapping)],
            "regime_scores": dict(row.get("regime_scores", {})),
            "source_family_scores": dict(row.get("source_family_scores", {})),
            "conflict_count": len(row.get("signal_conflicts_top_n", [])),
        })
    return {
        "signal_scoring_version": signal_score_report.get("signal_scoring_version"),
        "signal_registry_version": signal_score_report.get("signal_registry_version"),
        "horizon_weight_version": signal_score_report.get("horizon_weight_version"),
        "total_vote_count": signal_score_report.get("total_vote_count", 0),
        "horizon_count": signal_score_report.get("horizon_count", len(horizons)),
        "horizons": horizons,
    }


def build_market_regime_trace_row(
    *,
    generated_at: str,
    run_id: str,
    source_refs: Mapping[str, Any],
    feature_bundle: MarketRegimeFeatureBundle,
    prediction_packet: MarketRegimePredictionPacket,
    signal_score_report: Mapping[str, Any],
    active_parameter_set_id: str,
    parameter_set_registry_validation: Mapping[str, Any],
) -> Dict[str, Any]:
    relpath = trace_ledger_part_relpath(generated_at)
    row = {
        "schema_version": MARKET_REGIME_TRACE_SCHEMA_VERSION,
        "trace_ledger_version": MARKET_REGIME_TRACE_LEDGER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "trace_row",
        "prediction_family_id": "market_regime",
        "event_type": "market_regime_prediction_trace",
        "trace_id": f"{run_id}:trace",
        "run_id": run_id,
        "generated_at": generated_at,
        "trace_part_jsonl": relpath,
        "source_refs": dict(source_refs),
        "feature_summary": _feature_summary(feature_bundle),
        "signal_summary": _signal_summary(signal_score_report),
        "prediction_summary": _prediction_summary(prediction_packet),
        "active_parameter_set_id": active_parameter_set_id,
        "parameter_set_registry_validation": dict(parameter_set_registry_validation),
        "safety": {
            "read_only_sources": True,
            "trace_ledger_append_only": True,
            "raw_market_data_duplicated": False,
            "ui_render_invokes_classifier": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
            "trade_ledger_append_allowed": False,
            "would_send_to_broker": False,
        },
    }
    validation = validate_market_regime_trace_row(row)
    if not validation.get("ok"):
        raise ValueError(f"market-regime trace row validation failed: {validation}")
    encoded = json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8")
    if len(encoded) > _MAX_TRACE_ROW_BYTES:
        raise ValueError(f"trace row too large: {len(encoded)} bytes")
    return row


def validate_market_regime_trace_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    failures: list[str] = []
    if row.get("schema_version") != MARKET_REGIME_TRACE_SCHEMA_VERSION:
        failures.append("schema_version_mismatch")
    if row.get("artifact_kind") != "trace_row":
        failures.append("artifact_kind_mismatch")
    if row.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if not row.get("run_id"):
        failures.append("run_id_missing")
    if not row.get("generated_at"):
        failures.append("generated_at_missing")
    if not isinstance(row.get("source_refs"), Mapping):
        failures.append("source_refs_missing")
    if not isinstance(row.get("feature_summary"), Mapping):
        failures.append("feature_summary_missing")
    if not isinstance(row.get("signal_summary"), Mapping):
        failures.append("signal_summary_missing")
    if not isinstance(row.get("prediction_summary"), Mapping):
        failures.append("prediction_summary_missing")
    if _has_forbidden_raw_keys(row):
        failures.append("forbidden_raw_payload_key_present")
    safety = row.get("safety") if isinstance(row.get("safety"), Mapping) else {}
    for key in (
        "scheduler_enabled",
        "producer_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_intent_submitted",
        "trade_ledger_append_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    if safety.get("trace_ledger_append_only") is not True:
        failures.append("safety_trace_ledger_append_only_not_true")
    return {
        "ok": not failures,
        "trace_ledger_version": MARKET_REGIME_TRACE_LEDGER_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "trace_part_jsonl": str(row.get("trace_part_jsonl") or ""),
    }


def append_market_regime_trace_row_once(root: str | Path, row: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validate_market_regime_trace_row(row)
    if not validation.get("ok"):
        raise ValueError(f"market-regime trace row validation failed: {validation}")
    base = Path(root)
    relpath = str(row.get("trace_part_jsonl") or trace_ledger_part_relpath(str(row.get("generated_at") or "")))
    path = base / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n"
    line_bytes = len(line.encode("utf-8"))
    if line_bytes > _MAX_TRACE_ROW_BYTES:
        raise ValueError(f"trace row too large: {line_bytes} bytes")
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)
    row_count = 0
    first_ts = ""
    last_ts = ""
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            row_count += 1
            try:
                payload = json.loads(raw)
                ts = str(payload.get("generated_at") or "")
            except Exception:
                ts = ""
            if ts and not first_ts:
                first_ts = ts
            if ts:
                last_ts = ts
    meta_relpath = trace_ledger_meta_relpath(str(row.get("generated_at") or ""))
    meta = {
        "schema_version": "market_regime_trace_part_meta.2026_07_08.v1",
        "trace_ledger_version": MARKET_REGIME_TRACE_LEDGER_VERSION,
        "part_jsonl": relpath,
        "row_count": row_count,
        "bytes": path.stat().st_size,
        "first_generated_at": first_ts,
        "last_generated_at": last_ts,
        "max_trace_row_bytes": _MAX_TRACE_ROW_BYTES,
        "closed": False,
        "raw_market_data_duplicated": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
    meta_path = base / meta_relpath
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "trace_ledger_version": MARKET_REGIME_TRACE_LEDGER_VERSION,
        "trace_part_jsonl": relpath,
        "trace_part_meta_json": meta_relpath,
        "bytes_appended": line_bytes,
        "row_count": row_count,
        "raw_market_data_duplicated": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }
