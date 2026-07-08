# path: ./btcts_next/src/btcts/prediction/market_regime/tools/resolve_outcomes.py
# desc: Manual once/preflight tool that resolves expired market-regime latest_cards predictions into outcome rows and refreshes calibration summary. Uses artifact snapshots only; no raw market reads, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.calibration_summary import write_market_regime_calibration_artifacts
from btcts.prediction.market_regime.observation_evaluator import build_market_regime_candle_observation
from btcts.prediction.market_regime.outcome_resolver import (
    append_market_regime_outcome_row_once,
    build_market_regime_outcome_row,
    outcome_part_relpath,
)

MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION = "prediction.market_regime.tools.resolve_outcomes.2026_07_08.v1"
LATEST_CARDS_RELPATH = "prediction/market_regime/latest_cards.json"


def _parse_ts(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_now_iso() -> str:
    return _iso(datetime.now(timezone.utc))


def _date(value: object) -> str:
    text = str(value or "")
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    return "unknown-date"


def _load_latest_cards(root: str | Path) -> dict[str, Any]:
    path = Path(root) / LATEST_CARDS_RELPATH
    if not path.exists():
        raise FileNotFoundError(f"latest_cards not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("latest_cards payload is not an object")
    return payload


def _cards(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("cards")
    if not isinstance(rows, list):
        return []
    return [dict(item) for item in rows if isinstance(item, Mapping)]


def _current_card(cards: list[dict[str, Any]]) -> dict[str, Any] | None:
    for card in cards:
        if str(card.get("horizon_key") or "").lower() == "current" or int(card.get("horizon_sec") or 0) == 0:
            return dict(card)
    return cards[0] if cards else None


def _prediction_from_card(payload: Mapping[str, Any], card: Mapping[str, Any]) -> dict[str, Any]:
    detail = card.get("detail") if isinstance(card.get("detail"), Mapping) else {}
    run_id = str(card.get("run_id") or payload.get("run_id") or "")
    generated_at = str(card.get("generated_at") or payload.get("generated_at") or "")
    horizon_key = str(card.get("horizon_key") or ("current" if int(card.get("horizon_sec") or 0) == 0 else f"{int(card.get('horizon_sec') or 0)}s"))
    return {
        "run_id": run_id,
        "prediction_id": str(card.get("prediction_id") or payload.get("prediction_id") or f"{run_id}:{horizon_key}"),
        "generated_at": generated_at,
        "horizon": str(card.get("horizon") or ""),
        "horizon_key": horizon_key,
        "horizon_sec": int(card.get("horizon_sec") or 0),
        "regime_code": str(card.get("regime_code") or card.get("primary_regime") or "UNKNOWN"),
        "confidence_percent": int(card.get("confidence_percent") or 0),
        "evidence_quality": str(card.get("evidence_quality") or ""),
        "freshness_badge": str(card.get("freshness_badge") or ""),
        "parameter_set_id": str(card.get("parameter_set_id") or detail.get("active_parameter_set_id") or detail.get("parameter_set_id") or payload.get("parameter_set_id") or ""),
        "detail": {"trace_part_jsonl": str(card.get("trace_part_jsonl") or detail.get("trace_part_jsonl") or "")},
    }


def _observation_from_current_card(*, payload: Mapping[str, Any], current_card: Mapping[str, Any], resolved_at: str) -> dict[str, Any]:
    return {
        "observation_at": resolved_at,
        "observation_available": True,
        "observed_regime_code": str(current_card.get("regime_code") or "UNKNOWN"),
        "source_refs": [LATEST_CARDS_RELPATH, str(current_card.get("detail", {}).get("trace_part_jsonl") if isinstance(current_card.get("detail"), Mapping) else "")],
        "summary": f"observed_from_latest_cards_current run_id={payload.get('run_id') or '-'} horizon={current_card.get('horizon') or '-'} regime={current_card.get('regime_code') or 'UNKNOWN'}",
        "invalidated": False,
        "partial_match": False,
    }


def _expiry_at(prediction: Mapping[str, Any]) -> str:
    generated = _parse_ts(prediction.get("generated_at"))
    if generated is None:
        return ""
    return _iso(generated + timedelta(seconds=max(int(prediction.get("horizon_sec") or 0), 0)))


def _is_expired(prediction: Mapping[str, Any], resolved_at: str) -> bool:
    expiry = _parse_ts(_expiry_at(prediction))
    resolved = _parse_ts(resolved_at)
    if expiry is None or resolved is None:
        return False
    return resolved >= expiry


def _existing_outcome_ids(root: str | Path, generated_at: str) -> set[str]:
    path = Path(root) / outcome_part_relpath(generated_at)
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            if isinstance(payload, Mapping) and payload.get("outcome_id"):
                ids.add(str(payload.get("outcome_id")))
    return ids


def build_market_regime_outcome_once_plan(*, hot_root: str | Path, resolved_at: str | None = None) -> dict[str, Any]:
    root = Path(hot_root)
    effective_resolved_at = resolved_at or _utc_now_iso()
    payload = _load_latest_cards(root)
    cards = _cards(payload)
    current = _current_card(cards)
    if current is None:
        raise ValueError("latest_cards has no current/observable card")
    observation = _observation_from_current_card(payload=payload, current_card=current, resolved_at=effective_resolved_at)
    expired_predictions: list[dict[str, Any]] = []
    unexpired_count = 0
    skipped_current_count = 0
    for card in cards:
        prediction = _prediction_from_card(payload, card)
        if int(prediction.get("horizon_sec") or 0) <= 0:
            skipped_current_count += 1
            continue
        if _is_expired(prediction, effective_resolved_at):
            expired_predictions.append(prediction)
        else:
            unexpired_count += 1
    existing_ids = _existing_outcome_ids(root, str(payload.get("generated_at") or ""))
    candidate_rows: list[dict[str, Any]] = []
    duplicate_count = 0
    for prediction in expired_predictions:
        row = build_market_regime_outcome_row(prediction=prediction, observation=observation, resolved_at=effective_resolved_at)
        if str(row.get("outcome_id")) in existing_ids:
            duplicate_count += 1
            continue
        candidate_rows.append(row)
    return {
        "ok": True,
        "tool_version": MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION,
        "hot_root": str(root),
        "latest_cards_relpath": LATEST_CARDS_RELPATH,
        "latest_run_id": str(payload.get("run_id") or ""),
        "latest_generated_at": str(payload.get("generated_at") or ""),
        "resolved_at": effective_resolved_at,
        "card_count": len(cards),
        "skipped_current_count": skipped_current_count,
        "expired_prediction_count": len(expired_predictions),
        "unexpired_prediction_count": unexpired_count,
        "duplicate_outcome_count": duplicate_count,
        "candidate_outcome_count": len(candidate_rows),
        "observed_regime_code": str(observation.get("observed_regime_code") or "UNKNOWN"),
        "candidate_rows": candidate_rows,
        "would_write": False,
        "would_update_calibration": bool(candidate_rows),
        "safety": _safety(),
    }


def resolve_market_regime_outcomes_once(*, hot_root: str | Path, resolved_at: str | None = None, update_calibration: bool = True) -> dict[str, Any]:
    root = Path(hot_root)
    plan = build_market_regime_outcome_once_plan(hot_root=root, resolved_at=resolved_at)
    appended: list[dict[str, Any]] = []
    for row in plan["candidate_rows"]:
        appended.append(append_market_regime_outcome_row_once(root, row))
    calibration_result: dict[str, Any] = {}
    if update_calibration and appended:
        date = _date(plan.get("latest_generated_at") or plan.get("resolved_at"))
        calibration_result = write_market_regime_calibration_artifacts(root, date=date)
    return {
        "ok": True,
        "tool_version": MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION,
        "hot_root": str(root),
        "latest_run_id": plan["latest_run_id"],
        "latest_generated_at": plan["latest_generated_at"],
        "resolved_at": plan["resolved_at"],
        "expired_prediction_count": plan["expired_prediction_count"],
        "candidate_outcome_count": plan["candidate_outcome_count"],
        "duplicate_outcome_count": plan["duplicate_outcome_count"],
        "appended_outcome_count": len(appended),
        "appended": appended,
        "calibration_result": calibration_result,
        "safety": _safety(),
    }


def _safety(observation_source: str = "latest_cards_current") -> dict[str, Any]:
    source = _normalize_observation_source(observation_source)
    return {
        "artifact_snapshot_only": True,
        "observation_source": source,
        "reads_latest_cards_only": source == "latest_cards_current",
        "reads_derived_warroom_candles_only": source == "candle_summary",
        "raw_market_data_read": False,
        "raw_market_data_duplicated": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "parameter_auto_promotion_allowed": False,
        "would_send_to_broker": False,
    }





def _normalize_observation_source(value: object) -> str:
    source = str(value or "latest_cards_current").strip().lower()
    if source in {"latest_cards", "current", "latest_current", "latest_cards_current"}:
        return "latest_cards_current"
    if source in {"candle", "candles", "candle_summary", "derived_candles"}:
        return "candle_summary"
    raise ValueError(f"unsupported market-regime observation source: {value}")


def _outcome_id_for_prediction(prediction: Mapping[str, Any]) -> str:
    run_id = str(prediction.get("run_id") or "")
    horizon_sec = int(prediction.get("horizon_sec") or 0)
    horizon_key = str(prediction.get("horizon_key") or ("current" if horizon_sec == 0 else f"{horizon_sec}s"))
    generated_at = str(prediction.get("generated_at") or prediction.get("prediction_generated_at") or "")
    return f"{run_id}:{horizon_key}:outcome" if run_id else f"{generated_at}:{horizon_key}:outcome"


def _observation_for_prediction(
    root: str | Path,
    *,
    payload: Mapping[str, Any],
    current_card: Mapping[str, Any],
    prediction: Mapping[str, Any],
    resolved_at: str,
    observation_source: str,
) -> dict[str, Any]:
    source = _normalize_observation_source(observation_source)
    if source == "candle_summary":
        return build_market_regime_candle_observation(root, prediction=prediction, resolved_at=resolved_at)
    return _observation_from_current_card(payload=payload, current_card=current_card, resolved_at=resolved_at)

def _trace_part_paths(root: str | Path) -> list[Path]:
    base = Path(root) / "prediction/market_regime/ledgers"
    if not base.exists():
        return []
    return sorted(base.glob("date=*/hour=*/part-00001.jsonl"))


def _iter_trace_rows(root: str | Path, *, max_rows: int = 5000) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    limit = max(1, int(max_rows))
    for path in _trace_part_paths(root):
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                if not raw.strip():
                    continue
                try:
                    payload = json.loads(raw)
                except Exception:
                    continue
                if isinstance(payload, Mapping) and payload.get("artifact_kind") == "trace_row":
                    rows.append(dict(payload))
                    if len(rows) >= limit:
                        return rows
    return rows


def _prediction_from_trace_horizon(trace_row: Mapping[str, Any], horizon: Mapping[str, Any]) -> dict[str, Any]:
    run_id = str(trace_row.get("run_id") or "")
    generated_at = str(trace_row.get("generated_at") or trace_row.get("prediction_summary", {}).get("generated_at") if isinstance(trace_row.get("prediction_summary"), Mapping) else "")
    horizon_sec = int(horizon.get("horizon_sec") or 0)
    horizon_key = str(horizon.get("horizon_key") or ("current" if horizon_sec == 0 else f"{horizon_sec}s"))
    return {
        "run_id": run_id,
        "prediction_id": f"{run_id}:{horizon_key}" if run_id else f"{generated_at}:{horizon_key}",
        "generated_at": generated_at,
        "horizon": str(horizon.get("horizon") or ""),
        "horizon_key": horizon_key,
        "horizon_sec": horizon_sec,
        "regime_code": str(horizon.get("regime_code") or "UNKNOWN"),
        "confidence_percent": int(horizon.get("confidence_percent") or 0),
        "evidence_quality": str(horizon.get("evidence_quality") or ""),
        "freshness_badge": str(horizon.get("freshness_state") or horizon.get("freshness_badge") or ""),
        "parameter_set_id": str(horizon.get("parameter_set_id") or trace_row.get("active_parameter_set_id") or ""),
        "detail": {"trace_part_jsonl": str(trace_row.get("trace_part_jsonl") or "")},
    }


def _trace_predictions(root: str | Path, *, resolved_at: str, max_rows: int = 5000) -> tuple[list[dict[str, Any]], int, int]:
    predictions: list[dict[str, Any]] = []
    trace_rows = _iter_trace_rows(root, max_rows=max_rows)
    skipped_current_count = 0
    for trace_row in trace_rows:
        summary = trace_row.get("prediction_summary") if isinstance(trace_row.get("prediction_summary"), Mapping) else {}
        horizons = summary.get("horizons") if isinstance(summary.get("horizons"), list) else []
        for horizon in horizons:
            if not isinstance(horizon, Mapping):
                continue
            prediction = _prediction_from_trace_horizon(trace_row, horizon)
            if int(prediction.get("horizon_sec") or 0) <= 0:
                skipped_current_count += 1
                continue
            predictions.append(prediction)
    return predictions, len(trace_rows), skipped_current_count


def _existing_outcome_ids_for_predictions(root: str | Path, predictions: list[Mapping[str, Any]]) -> set[str]:
    ids: set[str] = set()
    seen_parts: set[Path] = set()
    for prediction in predictions:
        generated_at = str(prediction.get("generated_at") or "")
        path = Path(root) / outcome_part_relpath(generated_at)
        if path in seen_parts:
            continue
        seen_parts.add(path)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                if not raw.strip():
                    continue
                try:
                    payload = json.loads(raw)
                except Exception:
                    continue
                if isinstance(payload, Mapping) and payload.get("outcome_id"):
                    ids.add(str(payload.get("outcome_id")))
    return ids


def build_market_regime_trace_outcome_once_plan(
    *,
    hot_root: str | Path,
    resolved_at: str | None = None,
    max_trace_rows: int = 5000,
    observation_source: str = "latest_cards_current",
) -> dict[str, Any]:
    root = Path(hot_root)
    effective_resolved_at = resolved_at or _utc_now_iso()
    effective_observation_source = _normalize_observation_source(observation_source)
    payload = _load_latest_cards(root)
    current = _current_card(_cards(payload))
    if current is None:
        raise ValueError("latest_cards has no current/observable card")
    predictions, trace_row_count, skipped_current_count = _trace_predictions(root, resolved_at=effective_resolved_at, max_rows=max_trace_rows)
    expired_predictions: list[dict[str, Any]] = []
    unexpired_count = 0
    for prediction in predictions:
        if _is_expired(prediction, effective_resolved_at):
            expired_predictions.append(prediction)
        else:
            unexpired_count += 1
    existing_ids = _existing_outcome_ids_for_predictions(root, expired_predictions)
    candidate_rows: list[dict[str, Any]] = []
    duplicate_count = 0
    observed_regime_counts: dict[str, int] = {}
    for prediction in expired_predictions:
        if _outcome_id_for_prediction(prediction) in existing_ids:
            duplicate_count += 1
            continue
        observation = _observation_for_prediction(
            root,
            payload=payload,
            current_card=current,
            prediction=prediction,
            resolved_at=effective_resolved_at,
            observation_source=effective_observation_source,
        )
        row = build_market_regime_outcome_row(prediction=prediction, observation=observation, resolved_at=effective_resolved_at)
        observed = str(row.get("observed_regime_code") or "UNKNOWN")
        observed_regime_counts[observed] = observed_regime_counts.get(observed, 0) + 1
        candidate_rows.append(row)
    observed_regime_code = ""
    if len(observed_regime_counts) == 1:
        observed_regime_code = next(iter(observed_regime_counts))
    elif observed_regime_counts:
        observed_regime_code = "MIXED"
    else:
        observed_regime_code = str(current.get("regime_code") or "UNKNOWN") if effective_observation_source == "latest_cards_current" else "UNKNOWN"
    return {
        "ok": True,
        "tool_version": MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION,
        "source": "trace_ledger",
        "observation_source": effective_observation_source,
        "hot_root": str(root),
        "latest_cards_relpath": LATEST_CARDS_RELPATH,
        "latest_run_id": str(payload.get("run_id") or ""),
        "resolved_at": effective_resolved_at,
        "trace_row_count": trace_row_count,
        "trace_prediction_count": len(predictions),
        "skipped_current_count": skipped_current_count,
        "expired_prediction_count": len(expired_predictions),
        "unexpired_prediction_count": unexpired_count,
        "duplicate_outcome_count": duplicate_count,
        "candidate_outcome_count": len(candidate_rows),
        "observed_regime_code": observed_regime_code,
        "observed_regime_counts": observed_regime_counts,
        "candidate_rows": candidate_rows,
        "would_write": False,
        "would_update_calibration": bool(candidate_rows),
        "safety": _safety(effective_observation_source),
    }

def resolve_market_regime_trace_outcomes_once(
    *,
    hot_root: str | Path,
    resolved_at: str | None = None,
    update_calibration: bool = True,
    max_trace_rows: int = 5000,
    observation_source: str = "latest_cards_current",
) -> dict[str, Any]:
    root = Path(hot_root)
    plan = build_market_regime_trace_outcome_once_plan(
        hot_root=root,
        resolved_at=resolved_at,
        max_trace_rows=max_trace_rows,
        observation_source=observation_source,
    )
    appended: list[dict[str, Any]] = []
    affected_dates: set[str] = set()
    for row in plan["candidate_rows"]:
        appended.append(append_market_regime_outcome_row_once(root, row))
        affected_dates.add(_date(row.get("generated_at")))
    calibration_results: list[dict[str, Any]] = []
    if update_calibration and appended:
        for date in sorted(affected_dates):
            calibration_results.append(write_market_regime_calibration_artifacts(root, date=date))
    return {
        "ok": True,
        "tool_version": MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION,
        "source": "trace_ledger",
        "observation_source": plan["observation_source"],
        "hot_root": str(root),
        "latest_run_id": plan["latest_run_id"],
        "resolved_at": plan["resolved_at"],
        "trace_row_count": plan["trace_row_count"],
        "trace_prediction_count": plan["trace_prediction_count"],
        "expired_prediction_count": plan["expired_prediction_count"],
        "candidate_outcome_count": plan["candidate_outcome_count"],
        "duplicate_outcome_count": plan["duplicate_outcome_count"],
        "observed_regime_counts": plan["observed_regime_counts"],
        "appended_outcome_count": len(appended),
        "appended": appended,
        "calibration_results": calibration_results,
        "safety": _safety(plan["observation_source"]),
    }

def _json_for_print(payload: Mapping[str, Any]) -> str:
    clean = dict(payload)
    if "candidate_rows" in clean:
        clean["candidate_rows"] = [{"outcome_id": row.get("outcome_id"), "horizon_key": row.get("horizon_key"), "outcome_label": row.get("outcome_label")} for row in clean.get("candidate_rows", [])]
    return json.dumps(clean, ensure_ascii=False, sort_keys=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve expired market-regime predictions into outcomes once.")
    parser.add_argument("--hot-root", required=True, help="Hot or fixture root containing prediction/market_regime artifacts.")
    parser.add_argument("--resolved-at", default=None, help="UTC resolution timestamp. Defaults to current UTC.")
    parser.add_argument("--source", choices=("latest_cards", "trace_ledger"), default="latest_cards", help="Prediction source to evaluate. latest_cards keeps CP17 behavior; trace_ledger evaluates historical trace rows.")
    parser.add_argument("--max-trace-rows", type=int, default=5000, help="Maximum trace rows to scan when --source trace_ledger is used.")
    parser.add_argument("--observation-source", choices=("latest_cards_current", "candle_summary"), default="latest_cards_current", help="Observation source used for trace-ledger outcomes. Default keeps CP18 latest-current behavior; candle_summary uses derived WarRoom closed candles.")
    parser.add_argument("--preflight", action="store_true", help="Build outcome plan without writing outcome/calibration artifacts.")
    parser.add_argument("--once", action="store_true", help="Required acknowledgement for outcome/calibration writes.")
    parser.add_argument("--no-calibration", action="store_true", help="Append outcomes but skip calibration artifact refresh.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    source = str(args.source or "latest_cards")
    if args.preflight:
        if source == "trace_ledger":
            result = build_market_regime_trace_outcome_once_plan(hot_root=args.hot_root, resolved_at=args.resolved_at, max_trace_rows=args.max_trace_rows, observation_source=args.observation_source)
        else:
            result = build_market_regime_outcome_once_plan(hot_root=args.hot_root, resolved_at=args.resolved_at)
        print(_json_for_print(result))
        return 0
    if not args.once:
        parser.error("--once is required unless --preflight is used")
    if source == "trace_ledger":
        result = resolve_market_regime_trace_outcomes_once(
            hot_root=args.hot_root,
            resolved_at=args.resolved_at,
            update_calibration=not args.no_calibration,
            max_trace_rows=args.max_trace_rows,
            observation_source=args.observation_source,
        )
    else:
        result = resolve_market_regime_outcomes_once(hot_root=args.hot_root, resolved_at=args.resolved_at, update_calibration=not args.no_calibration)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
