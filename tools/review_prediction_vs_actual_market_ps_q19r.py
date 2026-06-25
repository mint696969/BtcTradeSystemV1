# path: ./tools/review_prediction_vs_actual_market_ps_q19r.py
# desc: PS-Q19R read-only helper to compare latest prediction records with realized FX_BTC_JPY market overview mid-price movement. No writes, scheduler, UI trigger, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH  # noqa: E402

PS_Q19R_REVIEW_VERSION = "prediction_warroom.ps_q19r_prediction_actual_market_review.v1"
DEFAULT_MARKET_OVERVIEW_RELATIVE_TEMPLATE = "data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date={date}/part-00001.jsonl"
DEFAULT_HORIZONS_SEC = (15, 60, 300, 600, 900)
DEFAULT_SELECTED_FAMILIES = (
    "market_regime",
    "trend_bias",
    "reversal_zone",
    "breakout_false_break",
    "opportunity_participation",
    "cross_venue_confirmation",
    "human_technical_structure",
)
DEFAULT_TAIL_BYTES = 240_000_000
DEFAULT_DIRECTION_THRESHOLD_BPS = 2.0


@dataclass(frozen=True)
class MarketPoint:
    ts: datetime
    mid_price: float
    best_bid: float | None
    best_ask: float | None
    spread: float | None
    trust_state: str
    continuity_state: str
    interpretation_bucket: str


def _parse_utc(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _prediction_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH


def _market_path_for_generated_at(root: str, generated_at: datetime) -> Path:
    return Path(str(root).rstrip("\\/")) / DEFAULT_MARKET_OVERVIEW_RELATIVE_TEMPLATE.format(date=generated_at.date().isoformat())


def _load_json_object(path: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, exc.__class__.__name__
    return (loaded if isinstance(loaded, Mapping) else {}), None


def _tail_bytes(path: Path, max_tail_bytes: int) -> bytes:
    size = path.stat().st_size
    with path.open("rb") as fh:
        if size > max_tail_bytes:
            fh.seek(max(0, size - max_tail_bytes))
            chunk = fh.read(int(max_tail_bytes))
            first_newline = chunk.find(b"\n")
            return chunk[first_newline + 1 :] if first_newline >= 0 else chunk
        return fh.read()


def _iter_jsonl_tail(path: Path, *, max_tail_bytes: int) -> Iterable[Mapping[str, Any]]:
    try:
        data = _tail_bytes(path, int(max_tail_bytes))
    except Exception:
        return
    for raw in data.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line.decode("utf-8"))
        except Exception:
            continue
        if isinstance(item, Mapping):
            yield item


def _market_point_from_row(row: Mapping[str, Any]) -> MarketPoint | None:
    ts = _parse_utc(row.get("collector_ts") or row.get("exchange_ts"))
    if ts is None:
        return None
    mid = _to_float(row.get("mid_price"))
    if mid is None:
        top = row.get("top_book_summary") if isinstance(row.get("top_book_summary"), Mapping) else {}
        bid = _to_float(row.get("best_bid") or top.get("best_bid"))
        ask = _to_float(row.get("best_ask") or top.get("best_ask"))
        if bid is not None and ask is not None:
            mid = (bid + ask) / 2.0
    if mid is None:
        return None
    top = row.get("top_book_summary") if isinstance(row.get("top_book_summary"), Mapping) else {}
    bid = _to_float(row.get("best_bid") or top.get("best_bid"))
    ask = _to_float(row.get("best_ask") or top.get("best_ask"))
    spread = _to_float(row.get("spread") or top.get("spread"))
    return MarketPoint(
        ts=ts,
        mid_price=float(mid),
        best_bid=bid,
        best_ask=ask,
        spread=spread,
        trust_state=str(row.get("trust_state") or ""),
        continuity_state=str(row.get("continuity_state") or ""),
        interpretation_bucket=str(row.get("interpretation_bucket") or ""),
    )


def _nearest(points: list[MarketPoint], target: datetime) -> MarketPoint | None:
    if not points:
        return None
    return min(points, key=lambda p: abs((p.ts - target).total_seconds()))


def _direction_from_label(label: str) -> str:
    text = label.lower()
    if any(token in text for token in ("long", "buy", "up", "bull", "positive")):
        return "up"
    if any(token in text for token in ("short", "sell", "down", "bear", "negative")):
        return "down"
    if any(token in text for token in ("range", "neutral", "compression", "blocked", "watch", "candidate", "confirmed", "structure")):
        return "neutral_or_range"
    return "non_directional"


def _realized_direction(return_bps: float | None, *, threshold_bps: float) -> str:
    if return_bps is None:
        return "unavailable"
    if return_bps > threshold_bps:
        return "up"
    if return_bps < -threshold_bps:
        return "down"
    return "flat"


def _actual_quality_reasons(point: MarketPoint) -> list[str]:
    reasons: list[str] = []
    if point.trust_state != "trusted":
        reasons.append("market_point_not_trusted")
    if point.continuity_state != "continuous":
        reasons.append("market_point_not_continuous")
    if point.interpretation_bucket != "allow_structural_use":
        reasons.append("market_point_not_structural_use")
    if point.spread is not None and point.spread < 0:
        reasons.append("market_point_negative_spread")
    if point.best_bid is not None and point.best_ask is not None and point.best_bid > point.best_ask:
        reasons.append("market_point_crossed_book")
    return reasons


def _actual_quality_ok(point: MarketPoint) -> bool:
    return not _actual_quality_reasons(point)


def _alignment(expected: str, realized: str) -> str:
    if realized == "unavailable":
        return "actual_unavailable"
    if expected in ("up", "down"):
        return "direction_match" if expected == realized else "direction_mismatch"
    if expected == "neutral_or_range":
        return "range_or_neutral_match" if realized == "flat" else "range_or_neutral_broken"
    return "not_scored_non_directional"


def _records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    fb = payload.get("forecast_batch") if isinstance(payload.get("forecast_batch"), Mapping) else {}
    rows = fb.get("records") if isinstance(fb.get("records"), list) else []
    return [row for row in rows if isinstance(row, Mapping)]


def _family_horizon_summary(rows: list[Mapping[str, Any]], *, families: tuple[str, ...], horizons: tuple[int, ...]) -> list[Mapping[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    family_set = set(families)
    horizon_set = set(horizons)
    for row in rows:
        family = str(row.get("family") or "")
        try:
            horizon = int(row.get("horizon_sec"))
        except Exception:
            continue
        if family in family_set and horizon in horizon_set:
            selected.append(row)
    selected.sort(key=lambda r: (int(r.get("horizon_sec") or 0), str(r.get("family") or "")))
    return selected


def build_prediction_actual_market_review_packet(
    *,
    prediction_payload: Mapping[str, Any],
    market_points: list[MarketPoint],
    source_prediction_path: str = "",
    source_market_path: str = "",
    selected_horizons_sec: tuple[int, ...] = DEFAULT_HORIZONS_SEC,
    selected_families: tuple[str, ...] = DEFAULT_SELECTED_FAMILIES,
    direction_threshold_bps: float = DEFAULT_DIRECTION_THRESHOLD_BPS,
) -> dict[str, Any]:
    forecast_batch = prediction_payload.get("forecast_batch") if isinstance(prediction_payload.get("forecast_batch"), Mapping) else {}
    generated_at = _parse_utc(forecast_batch.get("generated_at"))
    blockers: list[str] = []
    warnings: list[str] = []
    if not prediction_payload:
        blockers.append("prediction_payload_missing")
    if not forecast_batch:
        blockers.append("forecast_batch_missing")
    if generated_at is None:
        blockers.append("forecast_batch_generated_at_missing_or_invalid")
    if not market_points:
        blockers.append("market_points_missing")

    start_point = _nearest(market_points, generated_at) if generated_at is not None else None
    if start_point is None:
        blockers.append("start_market_point_missing")
    elif generated_at is not None and abs((start_point.ts - generated_at).total_seconds()) > 10:
        warnings.append("start_market_point_not_close_to_prediction_generated_at")

    actual_by_horizon: dict[int, dict[str, Any]] = {}
    if generated_at is not None and start_point is not None:
        for horizon in selected_horizons_sec:
            target = generated_at + timedelta(seconds=int(horizon))
            point = _nearest(market_points, target)
            if point is None:
                actual_by_horizon[int(horizon)] = {"available": False, "target_ts": _iso(target), "reason": "market_point_missing"}
                continue
            offset = abs((point.ts - target).total_seconds())
            close_enough = offset <= max(5.0, min(30.0, int(horizon) * 0.10))
            quality_reasons = _actual_quality_reasons(point)
            quality_ok = not quality_reasons
            available = bool(close_enough and quality_ok)
            if not close_enough:
                warnings.append(f"actual_market_point_not_close_enough:{horizon}")
            if quality_reasons:
                warnings.extend(f"actual_market_point_quality_rejected:{horizon}:{reason}" for reason in quality_reasons)
            delta = point.mid_price - start_point.mid_price
            return_bps = (delta / start_point.mid_price) * 10000.0 if start_point.mid_price else None
            actual_by_horizon[int(horizon)] = {
                "available": bool(available),
                "actual_quality_ok": bool(quality_ok),
                "actual_quality_reasons": list(quality_reasons),
                "target_ts": _iso(target),
                "observed_ts": _iso(point.ts),
                "offset_sec": int(offset),
                "start_mid_price": start_point.mid_price,
                "actual_mid_price": point.mid_price,
                "delta_price": delta,
                "return_bps": return_bps,
                "realized_direction": _realized_direction(return_bps, threshold_bps=direction_threshold_bps) if available else "unavailable",
                "spread": point.spread,
                "trust_state": point.trust_state,
                "continuity_state": point.continuity_state,
                "interpretation_bucket": point.interpretation_bucket,
            }

    review_rows: list[dict[str, Any]] = []
    for row in _family_horizon_summary(_records(prediction_payload), families=selected_families, horizons=selected_horizons_sec):
        family = str(row.get("family") or "")
        horizon = int(row.get("horizon_sec") or 0)
        label = str(row.get("primary_label") or "")
        expected = _direction_from_label(label)
        actual = actual_by_horizon.get(horizon, {})
        realized = str(actual.get("realized_direction") or "unavailable") if actual.get("available") is True else "unavailable"
        review_rows.append(
            {
                "family": family,
                "horizon_sec": horizon,
                "primary_label": label,
                "confidence": row.get("confidence"),
                "score": row.get("score"),
                "usable": row.get("usable") is True,
                "expected_direction_bucket": expected,
                "actual_available": actual.get("available") is True,
                "actual_quality_ok": actual.get("actual_quality_ok") is True,
                "actual_quality_reasons": list(actual.get("actual_quality_reasons") or []),
                "actual_return_bps": actual.get("return_bps") if actual.get("available") is True else None,
                "actual_delta_price": actual.get("delta_price") if actual.get("available") is True else None,
                "realized_direction": realized,
                "alignment_hint": _alignment(expected, realized),
                "warnings": list(row.get("warnings") or [])[:4] if isinstance(row.get("warnings"), list) else [],
                "drivers": list(row.get("drivers") or [])[:4] if isinstance(row.get("drivers"), list) else [],
            }
        )

    alignment_counter = Counter(str(row.get("alignment_hint")) for row in review_rows)
    available_count = sum(1 for row in review_rows if row.get("actual_available") is True)
    packet = {
        "ok": bool(not blockers and review_rows),
        "ps_q19r_version": PS_Q19R_REVIEW_VERSION,
        "source_prediction_path": source_prediction_path,
        "source_market_path": source_market_path,
        "prediction_generated_at": _iso(generated_at),
        "market_point_count_loaded": len(market_points),
        "start_market_point": {
            "ts": _iso(start_point.ts) if start_point else "",
            "mid_price": start_point.mid_price if start_point else None,
            "spread": start_point.spread if start_point else None,
        },
        "selected_horizons_sec": list(selected_horizons_sec),
        "selected_families": list(selected_families),
        "direction_threshold_bps": float(direction_threshold_bps),
        "actual_by_horizon": {str(k): v for k, v in sorted(actual_by_horizon.items())},
        "review_row_count": len(review_rows),
        "actual_available_row_count": available_count,
        "alignment_summary": dict(alignment_counter),
        "review_rows": review_rows,
        "blocked_reasons": list(dict.fromkeys(blockers)),
        "warning_reasons": list(dict.fromkeys(warnings)),
        "read_only_review": True,
        "runtime_artifact_write_performed_by_review": False,
        "status_artifact_write_performed_by_review": False,
        "prediction_artifact_write_performed_by_review": False,
        "view_artifact_write_performed_by_review": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }
    return packet


def load_and_build_prediction_actual_market_review_packet(
    *,
    root: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    prediction_path: str = "",
    market_path: str = "",
    max_tail_bytes: int = DEFAULT_TAIL_BYTES,
    horizons_sec: tuple[int, ...] = DEFAULT_HORIZONS_SEC,
    families: tuple[str, ...] = DEFAULT_SELECTED_FAMILIES,
    direction_threshold_bps: float = DEFAULT_DIRECTION_THRESHOLD_BPS,
) -> dict[str, Any]:
    pred_path = Path(prediction_path) if prediction_path else _prediction_path(root)
    payload, load_error = _load_json_object(pred_path)
    generated_at = None
    if payload:
        fb = payload.get("forecast_batch") if isinstance(payload.get("forecast_batch"), Mapping) else {}
        generated_at = _parse_utc(fb.get("generated_at"))
    mpath = Path(market_path) if market_path else (_market_path_for_generated_at(root, generated_at) if generated_at else Path(str(root).rstrip("\\/")) / DEFAULT_MARKET_OVERVIEW_RELATIVE_TEMPLATE.format(date=datetime.now(timezone.utc).date().isoformat()))
    points: list[MarketPoint] = []
    for row in _iter_jsonl_tail(mpath, max_tail_bytes=int(max_tail_bytes)):
        point = _market_point_from_row(row)
        if point is not None:
            points.append(point)
    points.sort(key=lambda p: p.ts)
    packet = build_prediction_actual_market_review_packet(
        prediction_payload=payload,
        market_points=points,
        source_prediction_path=str(pred_path),
        source_market_path=str(mpath),
        selected_horizons_sec=horizons_sec,
        selected_families=families,
        direction_threshold_bps=direction_threshold_bps,
    )
    if load_error:
        packet["blocked_reasons"].append("prediction_payload_unreadable:" + load_error)
        packet["ok"] = False
    if not mpath.exists():
        packet["blocked_reasons"].append("market_overview_path_missing")
        packet["ok"] = False
    return packet


def _parse_int_csv(text: str, default: tuple[int, ...]) -> tuple[int, ...]:
    if not text.strip():
        return default
    out: list[int] = []
    for part in text.split(","):
        item = part.strip()
        if item:
            out.append(int(item))
    return tuple(out) or default


def _parse_str_csv(text: str, default: tuple[str, ...]) -> tuple[str, ...]:
    if not text.strip():
        return default
    out = tuple(part.strip() for part in text.split(",") if part.strip())
    return out or default


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19R latest prediction vs actual market review")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT)
    parser.add_argument("--prediction-path", default="")
    parser.add_argument("--market-path", default="")
    parser.add_argument("--max-tail-bytes", type=int, default=DEFAULT_TAIL_BYTES)
    parser.add_argument("--horizons-sec", default=",".join(str(v) for v in DEFAULT_HORIZONS_SEC))
    parser.add_argument("--families", default=",".join(DEFAULT_SELECTED_FAMILIES))
    parser.add_argument("--direction-threshold-bps", type=float, default=DEFAULT_DIRECTION_THRESHOLD_BPS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = load_and_build_prediction_actual_market_review_packet(
        root=str(args.root),
        prediction_path=str(args.prediction_path or ""),
        market_path=str(args.market_path or ""),
        max_tail_bytes=int(args.max_tail_bytes),
        horizons_sec=_parse_int_csv(str(args.horizons_sec or ""), DEFAULT_HORIZONS_SEC),
        families=_parse_str_csv(str(args.families or ""), DEFAULT_SELECTED_FAMILIES),
        direction_threshold_bps=float(args.direction_threshold_bps),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
