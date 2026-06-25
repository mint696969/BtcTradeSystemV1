# path: ./tools/compare_actual_point_selection_policy_ps_q19x.py
# desc: PS-Q19X read-only helper comparing PS-Q19R strict nearest actual-point selection with nearest quality-ok within tolerance. Does not change PS-Q19R, write artifacts, trigger scheduler/UI/AutoTrade/broker/ledger, or apply parameters.

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Mapping

PS_Q19X_POLICY_VERSION = "prediction_warroom.ps_q19x_actual_point_selection_policy.v1"
DEFAULT_ROOT = r"D:\btc_ts_hot"
DEFAULT_PREDICTION_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"
DEFAULT_MARKET_OVERVIEW_RELATIVE_TEMPLATE = "data/market_state/exchange=bitflyer/symbol=FX_BTC_JPY/type=market.overview/date={date}/part-00001.jsonl"
DEFAULT_HORIZONS_SEC = (15, 60, 300, 600, 900)
DEFAULT_TOLERANCE_SEC = 30
SAFETY_FALSE_FIELDS = (
    "runtime_artifact_write_performed_by_policy_compare",
    "status_artifact_write_performed_by_policy_compare",
    "prediction_artifact_write_performed_by_policy_compare",
    "view_artifact_write_performed_by_policy_compare",
    "collector_state_write_performed_by_policy_compare",
    "ps_q19r_behavior_changed_by_policy_compare",
    "scheduler_enabled",
    "producer_enabled",
    "warroom_ui_trigger_enabled",
    "ui_triggered_runner_execution",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "would_send_to_broker",
)


def _parse_iso_z(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso_z(dt: datetime | None) -> str:
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


def _extract_collector_ts_fast(line: str) -> str:
    marker = '"collector_ts":"'
    idx = line.find(marker)
    if idx < 0:
        marker = '"collector_ts": "'
        idx = line.find(marker)
    if idx < 0:
        return ""
    start = idx + len(marker)
    end = line.find('"', start)
    return line[start:end] if end > start else ""


def _load_generated_at(prediction_path: Path, override_generated_at: str = "") -> tuple[datetime | None, list[str]]:
    warnings: list[str] = []
    if override_generated_at:
        parsed = _parse_iso_z(override_generated_at)
        if parsed is None:
            warnings.append("override_generated_at_invalid")
        return parsed, warnings
    try:
        payload = json.loads(prediction_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        return None, ["prediction_payload_unreadable:" + exc.__class__.__name__]
    if not isinstance(payload, Mapping):
        return None, ["prediction_payload_root_not_object"]
    fb = payload.get("forecast_batch") if isinstance(payload.get("forecast_batch"), Mapping) else {}
    generated_at = _parse_iso_z(fb.get("generated_at"))
    if generated_at is None:
        warnings.append("prediction_generated_at_missing_or_invalid")
    return generated_at, warnings


def _default_prediction_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / DEFAULT_PREDICTION_RELATIVE_PATH


def _default_market_path(root: str, generated_at: datetime) -> Path:
    return Path(str(root).rstrip("\\/")) / DEFAULT_MARKET_OVERVIEW_RELATIVE_TEMPLATE.format(date=generated_at.date().isoformat())


def _quality_reasons(record: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    trust = str(record.get("trust_state") or "")
    bucket = str(record.get("interpretation_bucket") or "")
    continuity = str(record.get("continuity_state") or "")
    spread = _to_float(record.get("spread"))
    bid = _to_float(record.get("best_bid"))
    ask = _to_float(record.get("best_ask"))
    if trust != "trusted":
        reasons.append("market_point_not_trusted")
    if continuity != "continuous":
        reasons.append("market_point_not_continuous")
    if bucket != "allow_structural_use":
        reasons.append("market_point_not_structural_use")
    if spread is not None and spread < 0:
        reasons.append("market_point_negative_spread")
    if bid is not None and ask is not None and bid > ask:
        reasons.append("market_point_crossed_book")
    return reasons


def _project_record(record: Mapping[str, Any], target: datetime) -> dict[str, Any]:
    ts = _parse_iso_z(record.get("collector_ts") or record.get("exchange_ts"))
    reasons = _quality_reasons(record)
    return {
        "collector_ts": _iso_z(ts),
        "offset_sec": abs((ts - target).total_seconds()) if ts is not None else None,
        "quality_ok": not reasons,
        "quality_reasons": reasons,
        "trust_state": str(record.get("trust_state") or ""),
        "continuity_state": str(record.get("continuity_state") or ""),
        "interpretation_bucket": str(record.get("interpretation_bucket") or ""),
        "best_bid": record.get("best_bid"),
        "best_ask": record.get("best_ask"),
        "spread": record.get("spread"),
        "mid_price": record.get("mid_price"),
    }


def _target_ranges(generated_at: datetime, horizons: tuple[int, ...], tolerance_sec: int) -> list[tuple[int, datetime, datetime, datetime]]:
    out: list[tuple[int, datetime, datetime, datetime]] = []
    tolerance = timedelta(seconds=max(0, int(tolerance_sec)))
    for horizon in horizons:
        target = generated_at + timedelta(seconds=int(horizon))
        out.append((int(horizon), target - tolerance, target, target + tolerance))
    return out


def _load_candidate_rows(market_path: Path, ranges: list[tuple[int, datetime, datetime, datetime]]) -> tuple[dict[int, list[Mapping[str, Any]]], int, int]:
    by_horizon: dict[int, list[Mapping[str, Any]]] = {h: [] for h, _, _, _ in ranges}
    scanned_lines = 0
    parsed_rows = 0
    if not market_path.exists():
        return by_horizon, scanned_lines, parsed_rows
    min_start = min(start for _, start, _, _ in ranges)
    max_end = max(end for _, _, _, end in ranges)
    min_s = _iso_z(min_start)
    max_s = _iso_z(max_end)
    entered = False
    with market_path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            scanned_lines += 1
            ts_s = _extract_collector_ts_fast(line)
            if not ts_s:
                continue
            if ts_s < min_s:
                continue
            if ts_s > max_s:
                if entered:
                    break
                continue
            entered = True
            try:
                record = json.loads(line)
            except Exception:
                continue
            if not isinstance(record, Mapping):
                continue
            ts = _parse_iso_z(record.get("collector_ts") or record.get("exchange_ts"))
            if ts is None:
                continue
            parsed_rows += 1
            for horizon, start, _target, end in ranges:
                if start <= ts <= end:
                    by_horizon[horizon].append(record)
    return by_horizon, scanned_lines, parsed_rows


def _pick_strict_nearest(records: list[Mapping[str, Any]], target: datetime) -> Mapping[str, Any] | None:
    if not records:
        return None
    # Preserve file order as the tiebreaker, matching the current PS-Q19R nearest-row behavior.
    return min(records, key=lambda r: abs(((_parse_iso_z(r.get("collector_ts") or r.get("exchange_ts")) or target) - target).total_seconds()))


def _pick_quality_ok_nearest(records: list[Mapping[str, Any]], target: datetime) -> Mapping[str, Any] | None:
    ok_rows = [record for record in records if not _quality_reasons(record)]
    if not ok_rows:
        return None
    return min(ok_rows, key=lambda r: abs(((_parse_iso_z(r.get("collector_ts") or r.get("exchange_ts")) or target) - target).total_seconds()))


def compare_actual_point_selection_policy(
    *,
    market_path: Path,
    generated_at: datetime,
    horizons_sec: tuple[int, ...] = DEFAULT_HORIZONS_SEC,
    tolerance_sec: int = DEFAULT_TOLERANCE_SEC,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not market_path.exists():
        blockers.append("market_overview_path_missing")
    ranges = _target_ranges(generated_at, horizons_sec, int(tolerance_sec))
    by_horizon, scanned_lines, parsed_candidate_rows = _load_candidate_rows(market_path, ranges) if not blockers else ({h: [] for h in horizons_sec}, 0, 0)
    horizon_results: dict[str, dict[str, Any]] = {}
    impacted_horizons: list[str] = []
    quality_ok_alternative_available_count = 0
    strict_rejected_count = 0
    same_second_quality_ok_alternative_count = 0
    reason_counts: Counter[str] = Counter()

    for horizon, _start, target, _end in ranges:
        rows = by_horizon.get(horizon, [])
        strict = _pick_strict_nearest(rows, target)
        quality_ok = _pick_quality_ok_nearest(rows, target)
        strict_projection = _project_record(strict, target) if isinstance(strict, Mapping) else None
        ok_projection = _project_record(quality_ok, target) if isinstance(quality_ok, Mapping) else None
        strict_quality_ok = bool(strict_projection and strict_projection.get("quality_ok") is True)
        quality_ok_available = bool(ok_projection)
        strict_rejected = bool(strict_projection and strict_projection.get("quality_ok") is False)
        if strict_rejected:
            strict_rejected_count += 1
            reason_counts.update(strict_projection.get("quality_reasons") or [])
        if quality_ok_available:
            quality_ok_alternative_available_count += 1
        same_second_alternative = bool(
            strict_projection
            and ok_projection
            and strict_projection.get("collector_ts") == ok_projection.get("collector_ts")
            and strict_projection.get("quality_ok") is False
            and ok_projection.get("quality_ok") is True
        )
        if same_second_alternative:
            same_second_quality_ok_alternative_count += 1
        policy_delta = "no_quality_ok_candidate"
        if strict_projection is None:
            policy_delta = "strict_missing"
        elif strict_quality_ok:
            policy_delta = "strict_already_quality_ok"
        elif quality_ok_available:
            policy_delta = "strict_rejected_quality_ok_candidate_available"
            impacted_horizons.append(str(horizon))
        horizon_results[str(horizon)] = {
            "target_ts": _iso_z(target),
            "candidate_row_count": len(rows),
            "strict_nearest": strict_projection,
            "quality_ok_nearest": ok_projection,
            "strict_nearest_quality_ok": strict_quality_ok,
            "quality_ok_candidate_available": quality_ok_available,
            "same_second_quality_ok_candidate_available": same_second_alternative,
            "policy_delta": policy_delta,
        }

    if not any(item.get("candidate_row_count", 0) for item in horizon_results.values()) and not blockers:
        warnings.append("candidate_rows_missing_for_all_horizons")
    recommendation = "preserve_strict_fail_closed_policy"
    if impacted_horizons:
        recommendation = "consider_quality_ok_within_tolerance_policy_or_collector_repair"

    return {
        "ok": bool(not blockers),
        "ps_q19x_version": PS_Q19X_POLICY_VERSION,
        "source_market_path": str(market_path),
        "prediction_generated_at": _iso_z(generated_at),
        "selected_horizons_sec": list(horizons_sec),
        "tolerance_sec": int(tolerance_sec),
        "scanned_lines": scanned_lines,
        "parsed_candidate_rows": parsed_candidate_rows,
        "horizon_results": horizon_results,
        "strict_rejected_horizon_count": strict_rejected_count,
        "quality_ok_alternative_available_count": quality_ok_alternative_available_count,
        "same_second_quality_ok_alternative_count": same_second_quality_ok_alternative_count,
        "impacted_horizons": impacted_horizons,
        "strict_rejected_reason_counts": dict(reason_counts),
        "policy_comparison": {
            "current_ps_q19r_policy": "strict_nearest_then_fail_closed_quality_gate",
            "candidate_policy": "nearest_quality_ok_within_tolerance",
            "ps_q19r_behavior_changed_by_this_helper": False,
            "quality_rejected_records_should_not_be_scored": True,
            "quality_ok_candidate_does_not_imply_auto_rewrite": True,
            "operator_policy_decision_required_before_ps_q19r_change": True,
            "recommendation": recommendation,
        },
        "blocked_reasons": blockers,
        "warning_reasons": warnings,
        "read_only_policy_compare": True,
        **{field: False for field in SAFETY_FALSE_FIELDS},
    }


def load_and_compare_actual_point_selection_policy(
    *,
    root: str = DEFAULT_ROOT,
    prediction_path: str = "",
    market_path: str = "",
    generated_at_override: str = "",
    horizons_sec: tuple[int, ...] = DEFAULT_HORIZONS_SEC,
    tolerance_sec: int = DEFAULT_TOLERANCE_SEC,
) -> dict[str, Any]:
    pred_path = Path(prediction_path) if prediction_path else _default_prediction_path(root)
    generated_at, warnings = _load_generated_at(pred_path, generated_at_override)
    if generated_at is None:
        return {
            "ok": False,
            "ps_q19x_version": PS_Q19X_POLICY_VERSION,
            "source_prediction_path": str(pred_path),
            "source_market_path": str(market_path or ""),
            "blocked_reasons": ["prediction_generated_at_missing_or_invalid"],
            "warning_reasons": warnings,
            "read_only_policy_compare": True,
            **{field: False for field in SAFETY_FALSE_FIELDS},
        }
    mpath = Path(market_path) if market_path else _default_market_path(root, generated_at)
    packet = compare_actual_point_selection_policy(
        market_path=mpath,
        generated_at=generated_at,
        horizons_sec=horizons_sec,
        tolerance_sec=int(tolerance_sec),
    )
    packet["source_prediction_path"] = str(pred_path)
    if warnings:
        packet["warning_reasons"] = list(dict.fromkeys(list(packet.get("warning_reasons") or []) + warnings))
    return packet


def _parse_int_csv(text: str, default: tuple[int, ...]) -> tuple[int, ...]:
    if not str(text or "").strip():
        return default
    out: list[int] = []
    for part in str(text).split(","):
        item = part.strip()
        if item:
            out.append(int(item))
    return tuple(out) or default


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19X compare strict nearest vs nearest quality-ok actual point selection")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--prediction-path", default="")
    parser.add_argument("--market-path", default="")
    parser.add_argument("--generated-at", default="", help="Override prediction generated_at, useful for saved observations.")
    parser.add_argument("--horizons-sec", default=",".join(str(v) for v in DEFAULT_HORIZONS_SEC))
    parser.add_argument("--tolerance-sec", type=int, default=DEFAULT_TOLERANCE_SEC)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = load_and_compare_actual_point_selection_policy(
        root=str(args.root),
        prediction_path=str(args.prediction_path or ""),
        market_path=str(args.market_path or ""),
        generated_at_override=str(args.generated_at or ""),
        horizons_sec=_parse_int_csv(str(args.horizons_sec or ""), DEFAULT_HORIZONS_SEC),
        tolerance_sec=int(args.tolerance_sec),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
