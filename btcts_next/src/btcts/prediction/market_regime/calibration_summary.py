# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_summary.py
# desc: Market-regime calibration summary MVP. Aggregates compact outcome rows into daily/monthly summary artifacts. No raw market read, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

MARKET_REGIME_CALIBRATION_SUMMARY_VERSION = "prediction.market_regime.calibration_summary.2026_07_08.v1"
MARKET_REGIME_CALIBRATION_TABLE_VERSION = "prediction.market_regime.calibration_table.2026_07_08.v1"
_ALLOWED_OUTCOME_LABELS = ("hit", "partial", "miss", "invalidated", "unknown")
_SCORE = {"hit": 1.0, "partial": 0.5, "miss": 0.0, "invalidated": 0.0, "unknown": 0.0}
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


def _date_from_ts(value: object) -> str:
    text = str(value or "")
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    return "unknown-date"


def _month_from_date(value: str) -> str:
    return value[:7] if len(value) >= 7 and value[4:5] == "-" else "unknown-month"


def calibration_daily_summary_relpath(date: str) -> str:
    return f"prediction/market_regime/calibration/date={date}/daily_summary.json"


def calibration_table_relpath(month: str) -> str:
    return f"prediction/market_regime/calibration/month={month}/calibration_table.json"


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


def _normalize_observation_source(value: object) -> str:
    source = str(value or "").strip().lower()
    if source in {"candle", "candles", "candle_summary", "derived_candles"}:
        return "candle_summary"
    if source in {"latest_cards", "current", "latest_current", "latest_cards_current", ""}:
        return "latest_cards_current"
    return source


def _row_observation_source(row: Mapping[str, Any]) -> str:
    if row.get("observation_source"):
        return _normalize_observation_source(row.get("observation_source"))
    observation_summary = row.get("observation_summary") if isinstance(row.get("observation_summary"), Mapping) else {}
    if observation_summary.get("observation_source"):
        return _normalize_observation_source(observation_summary.get("observation_source"))
    if row.get("observation_evaluator_version") or observation_summary.get("observation_evaluator_version"):
        return "candle_summary"
    return "latest_cards_current"

def _empty_counts() -> dict[str, int]:
    return {label: 0 for label in _ALLOWED_OUTCOME_LABELS}


def _update_bucket(bucket: dict[str, Any], row: Mapping[str, Any]) -> None:
    label = str(row.get("outcome_label") or "unknown")
    if label not in _ALLOWED_OUTCOME_LABELS:
        label = "unknown"
    bucket["total"] += 1
    bucket["counts"][label] += 1
    bucket["score_sum"] += _SCORE[label]
    confidence = row.get("confidence_percent")
    if isinstance(confidence, int | float):
        bucket["confidence_sum"] += float(confidence)
        bucket["confidence_count"] += 1
    trace_ref = str(row.get("trace_part_jsonl") or "")
    if trace_ref and trace_ref not in bucket["sample_trace_refs"] and len(bucket["sample_trace_refs"]) < 5:
        bucket["sample_trace_refs"].append(trace_ref)


def _finalize_bucket(key: str, bucket: Mapping[str, Any]) -> dict[str, Any]:
    total = int(bucket.get("total") or 0)
    counts = dict(bucket.get("counts") or _empty_counts())
    known_total = total - int(counts.get("unknown") or 0)
    score_sum = float(bucket.get("score_sum") or 0.0)
    confidence_count = int(bucket.get("confidence_count") or 0)
    confidence_sum = float(bucket.get("confidence_sum") or 0.0)
    return {
        "key": key,
        "total": total,
        "known_total": known_total,
        "counts": counts,
        "hit_rate": round(counts.get("hit", 0) / known_total, 4) if known_total > 0 else None,
        "partial_rate": round(counts.get("partial", 0) / known_total, 4) if known_total > 0 else None,
        "miss_rate": round(counts.get("miss", 0) / known_total, 4) if known_total > 0 else None,
        "calibration_score": round(score_sum / known_total, 4) if known_total > 0 else None,
        "avg_confidence_percent": round(confidence_sum / confidence_count, 2) if confidence_count > 0 else None,
        "sample_trace_refs": list(bucket.get("sample_trace_refs") or []),
    }


def _bucket() -> dict[str, Any]:
    return {"total": 0, "counts": _empty_counts(), "score_sum": 0.0, "confidence_sum": 0.0, "confidence_count": 0, "sample_trace_refs": []}


def _safe_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "outcome_id": str(row.get("outcome_id") or ""),
        "run_id": str(row.get("run_id") or ""),
        "generated_at": str(row.get("generated_at") or ""),
        "resolved_at": str(row.get("resolved_at") or ""),
        "horizon_key": str(row.get("horizon_key") or ""),
        "horizon_sec": int(row.get("horizon_sec") or 0),
        "predicted_regime_code": str(row.get("predicted_regime_code") or "UNKNOWN"),
        "observed_regime_code": str(row.get("observed_regime_code") or "UNKNOWN"),
        "outcome_label": str(row.get("outcome_label") or "unknown"),
        "observation_source": _row_observation_source(row),
        "observation_evaluator_version": str(row.get("observation_evaluator_version") or (row.get("observation_summary") or {}).get("observation_evaluator_version") if isinstance(row.get("observation_summary"), Mapping) else ""),
        "confidence_percent": row.get("confidence_percent"),
        "parameter_set_id": str(row.get("parameter_set_id") or ""),
        "trace_part_jsonl": str(row.get("trace_part_jsonl") or ""),
    }


def build_market_regime_calibration_summary(*, rows: Iterable[Mapping[str, Any]], date: str = "") -> Dict[str, Any]:
    safe_rows: list[dict[str, Any]] = []
    by_horizon: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_regime: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_parameter: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_parameter_horizon: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_observation_source: dict[str, dict[str, Any]] = defaultdict(_bucket)
    by_observation_source_horizon: dict[str, dict[str, Any]] = defaultdict(_bucket)
    failures: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            failures.append(f"row_{index}_not_mapping")
            continue
        if _has_forbidden_raw_keys(row):
            failures.append(f"row_{index}_forbidden_raw_payload_key_present")
            continue
        safe = _safe_row(row)
        if safe["outcome_label"] not in _ALLOWED_OUTCOME_LABELS:
            safe["outcome_label"] = "unknown"
        safe_rows.append(safe)
        horizon_key = safe["horizon_key"] or "unknown"
        regime_key = safe["predicted_regime_code"] or "UNKNOWN"
        parameter_key = safe["parameter_set_id"] or "unknown_parameter_set"
        observation_source_key = safe["observation_source"] or "latest_cards_current"
        _update_bucket(by_horizon[horizon_key], safe)
        _update_bucket(by_regime[regime_key], safe)
        _update_bucket(by_parameter[parameter_key], safe)
        _update_bucket(by_parameter_horizon[f"{parameter_key}|{horizon_key}"], safe)
        _update_bucket(by_observation_source[observation_source_key], safe)
        _update_bucket(by_observation_source_horizon[f"{observation_source_key}|{horizon_key}"], safe)
    effective_date = date or (_date_from_ts(safe_rows[0]["generated_at"]) if safe_rows else "unknown-date")
    summary = {
        "schema_version": "market_regime_calibration_daily_summary.2026_07_08.v1",
        "calibration_summary_version": MARKET_REGIME_CALIBRATION_SUMMARY_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "calibration_daily_summary",
        "prediction_family_id": "market_regime",
        "date": effective_date,
        "row_count": len(safe_rows),
        "input_failure_count": len(failures),
        "input_failures": failures,
        "overall": _finalize_bucket("overall", _aggregate_all(safe_rows)),
        "by_horizon": [_finalize_bucket(key, by_horizon[key]) for key in sorted(by_horizon)],
        "by_predicted_regime": [_finalize_bucket(key, by_regime[key]) for key in sorted(by_regime)],
        "by_parameter_set": [_finalize_bucket(key, by_parameter[key]) for key in sorted(by_parameter)],
        "by_parameter_set_horizon": [_finalize_bucket(key, by_parameter_horizon[key]) for key in sorted(by_parameter_horizon)],
        "by_observation_source": [_finalize_bucket(key, by_observation_source[key]) for key in sorted(by_observation_source)],
        "by_observation_source_horizon": [_finalize_bucket(key, by_observation_source_horizon[key]) for key in sorted(by_observation_source_horizon)],
        "promotion_candidates": _promotion_candidates(by_parameter),
        "safety": _safety(),
    }
    validation = validate_market_regime_calibration_summary(summary)
    if not validation.get("ok"):
        raise ValueError(f"market-regime calibration summary validation failed: {validation}")
    return summary


def _aggregate_all(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    bucket = _bucket()
    for row in rows:
        _update_bucket(bucket, row)
    return bucket


def _promotion_candidates(by_parameter: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for parameter_set_id, bucket in by_parameter.items():
        finalized = _finalize_bucket(parameter_set_id, bucket)
        known_total = int(finalized.get("known_total") or 0)
        score = finalized.get("calibration_score")
        if known_total >= 20 and isinstance(score, float) and score >= 0.65:
            candidates.append({
                "parameter_set_id": parameter_set_id,
                "known_total": known_total,
                "calibration_score": score,
                "state": "candidate_evidence_only",
                "human_gate_required": True,
                "auto_promotion_allowed": False,
            })
    return sorted(candidates, key=lambda item: item["calibration_score"], reverse=True)


def _safety() -> dict[str, Any]:
    return {
        "read_only_outcome_rows": True,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "parameter_auto_promotion_allowed": False,
        "human_gate_required_for_parameter_change": True,
        "would_send_to_broker": False,
    }


def build_market_regime_calibration_table(*, daily_summaries: Iterable[Mapping[str, Any]], month: str = "") -> Dict[str, Any]:
    summaries = [dict(item) for item in daily_summaries if isinstance(item, Mapping)]
    rows: list[dict[str, Any]] = []
    observation_source_rows: list[dict[str, Any]] = []
    for summary in summaries:
        date = str(summary.get("date") or "")
        for item in summary.get("by_parameter_set_horizon", []):
            if not isinstance(item, Mapping):
                continue
            row = dict(item)
            row["date"] = date
            rows.append(row)
        for item in summary.get("by_observation_source_horizon", []):
            if not isinstance(item, Mapping):
                continue
            row = dict(item)
            row["date"] = date
            observation_source_rows.append(row)
    effective_month = month or (_month_from_date(str(summaries[0].get("date") or "")) if summaries else "unknown-month")
    return {
        "schema_version": "market_regime_calibration_table.2026_07_08.v1",
        "calibration_table_version": MARKET_REGIME_CALIBRATION_TABLE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "calibration_table",
        "prediction_family_id": "market_regime",
        "month": effective_month,
        "daily_summary_count": len(summaries),
        "row_count": len(rows),
        "rows": rows,
        "observation_source_row_count": len(observation_source_rows),
        "observation_source_rows": observation_source_rows,
        "promotion_candidates": [candidate for summary in summaries for candidate in summary.get("promotion_candidates", []) if isinstance(candidate, Mapping)],
        "safety": _safety(),
    }


def validate_market_regime_calibration_summary(summary: Mapping[str, Any]) -> Dict[str, Any]:
    failures: list[str] = []
    if summary.get("artifact_kind") != "calibration_daily_summary":
        failures.append("artifact_kind_mismatch")
    if summary.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    if _has_forbidden_raw_keys(summary):
        failures.append("forbidden_raw_payload_key_present")
    safety = summary.get("safety") if isinstance(summary.get("safety"), Mapping) else {}
    for key in (
        "scheduler_enabled",
        "producer_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "parameter_auto_promotion_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    if safety.get("human_gate_required_for_parameter_change") is not True:
        failures.append("safety_human_gate_required_not_true")
    return {
        "ok": not failures,
        "calibration_summary_version": MARKET_REGIME_CALIBRATION_SUMMARY_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "row_count": int(summary.get("row_count") or 0),
    }


def read_market_regime_outcome_rows(root: str | Path, *, date: str) -> list[dict[str, Any]]:
    part = Path(root) / f"prediction/market_regime/outcomes/date={date}/part-00001.jsonl"
    if not part.exists():
        return []
    rows: list[dict[str, Any]] = []
    with part.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            payload = json.loads(raw)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def write_market_regime_calibration_artifacts(root: str | Path, *, date: str) -> Dict[str, Any]:
    base = Path(root)
    rows = read_market_regime_outcome_rows(base, date=date)
    summary = build_market_regime_calibration_summary(rows=rows, date=date)
    daily_relpath = calibration_daily_summary_relpath(date)
    month = _month_from_date(date)
    table = build_market_regime_calibration_table(daily_summaries=[summary], month=month)
    table_relpath = calibration_table_relpath(month)
    for relpath, payload in ((daily_relpath, summary), (table_relpath, table)):
        path = base / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "calibration_summary_version": MARKET_REGIME_CALIBRATION_SUMMARY_VERSION,
        "date": date,
        "month": month,
        "daily_summary_json": daily_relpath,
        "calibration_table_json": table_relpath,
        "outcome_row_count": len(rows),
        "safety": _safety(),
    }
