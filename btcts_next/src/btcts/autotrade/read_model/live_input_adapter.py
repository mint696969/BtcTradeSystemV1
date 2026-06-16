# path: ./btcts_next/src/btcts/autotrade/read_model/live_input_adapter.py
# desc: Read-only live-input adapter contract for AutoTrade. No UI imports, no mutation.

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from btcts.autotrade.config.models import ParameterSet
from btcts.autotrade.read_model.ids import build_snapshot_id
from btcts.autotrade.read_model.temporal_flow_adapter import build_temporal_flow_features_from_rows
from btcts.autotrade.read_model.models import (
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)
from btcts.core import paths as core_paths


@dataclass(frozen=True)
class LiveInputAdapterDiagnostics:
    data_root: Path
    market_state_root: Path
    latest_part_path: Path | None
    latest_part_exists: bool
    requested_exchange: str
    requested_symbol_raw: str
    requested_state_type: str
    requested_market_role: str
    execution_product_code: str | None
    execution_market_uid: str | None
    latest_row_market_uid: str | None
    latest_row_symbol_raw: str | None
    preferred_row_freshness: str
    preferred_row_age_sec: float | None
    preferred_row_is_stale: bool | None
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key in ("data_root", "market_state_root", "latest_part_path"):
            if data.get(key) is not None:
                data[key] = str(data[key])
        return data


def market_state_root() -> Path:
    return core_paths.data_dir(ensure=False) / "market_state"


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def latest_market_state_part_file(*, exchange: str = "bitflyer", symbol_raw: str = "BTC_JPY", state_type: str = "market.overview") -> Path | None:
    root = market_state_root() / f"exchange={exchange}" / f"symbol={symbol_raw}" / f"type={state_type}"
    if not root.exists():
        return None
    date_dirs = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("date=")], key=lambda p: p.name)
    if not date_dirs:
        return None
    part_files = sorted(date_dirs[-1].glob("part-*.jsonl"))
    return part_files[-1] if part_files else None


def preferred_market_state_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    preferred: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("trust_state") or "") != "trusted":
            continue
        if str(row.get("continuity_state") or "") != "continuous":
            continue
        if str(row.get("interpretation_bucket") or "") != "allow_structural_use":
            continue
        preferred.append(row)
    return preferred[-1] if preferred else rows[-1]


def _parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def row_age_seconds(row: dict[str, Any]) -> float | None:
    dt = _parse_ts(row.get("collector_ts") or row.get("exchange_ts"))
    if dt is None:
        return None
    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def freshness_label(row: dict[str, Any], *, live_sec: float = 30.0, stale_sec: float = 120.0) -> str:
    age = row_age_seconds(row)
    if age is None:
        return "UNKNOWN"
    if age <= live_sec:
        return "LIVE"
    if age <= stale_sec:
        return "QUIET"
    return "STALE"

def _execution_product_code() -> str | None:
    value = os.getenv("BTCTS_EXECUTION_PRODUCT_CODE")
    return value.strip() if value and value.strip() else None


def _execution_market_uid() -> str | None:
    value = os.getenv("BTCTS_EXECUTION_MARKET_UID")
    return value.strip() if value and value.strip() else None


def _market_role_for_symbol(symbol_raw: str) -> str:
    text = str(symbol_raw or "").strip().upper()
    if text.startswith("FX_"):
        return "execution"
    return "reference"


def _identity_blockers(*, symbol_raw: str, preferred: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    execution_product = _execution_product_code()
    execution_uid = _execution_market_uid()
    requested_symbol = str(symbol_raw or "").strip()
    row_symbol = str(preferred.get("symbol_raw") or "").strip() if preferred else ""
    row_uid = str(preferred.get("market_uid") or "").strip() if preferred else ""

    if execution_product and requested_symbol and requested_symbol != execution_product:
        blocked.append("live_input_symbol_differs_from_execution_product")
    if execution_product and row_symbol and row_symbol != execution_product:
        blocked.append("live_input_row_symbol_differs_from_execution_product")
    if execution_uid and row_uid and row_uid != execution_uid:
        blocked.append("live_input_row_market_uid_differs_from_execution_market_uid")
    return tuple(dict.fromkeys(blocked))



def live_input_adapter_diagnostics(*, exchange: str = "bitflyer", symbol_raw: str = "BTC_JPY", state_type: str = "market.overview") -> LiveInputAdapterDiagnostics:
    latest = latest_market_state_part_file(exchange=exchange, symbol_raw=symbol_raw, state_type=state_type)
    rows = _read_jsonl_rows(latest) if latest is not None else []
    preferred = preferred_market_state_row(rows)
    freshness = freshness_label(preferred) if preferred else "UNKNOWN"
    age = row_age_seconds(preferred) if preferred else None
    blocked: list[str] = list(_identity_blockers(symbol_raw=symbol_raw, preferred=preferred))
    warnings: list[str] = []
    if latest is None or not latest.exists():
        blocked.append("market_state_latest_part_missing")
    if not preferred:
        blocked.append("market_state_preferred_row_missing")
    if freshness == "STALE":
        blocked.append("market_state_preferred_row_stale")
    if freshness == "UNKNOWN":
        warnings.append("market_state_preferred_row_freshness_unknown")
    return LiveInputAdapterDiagnostics(
        data_root=core_paths.data_dir(ensure=False),
        market_state_root=market_state_root(),
        latest_part_path=latest,
        latest_part_exists=bool(latest and latest.exists()),
        requested_exchange=str(exchange),
        requested_symbol_raw=str(symbol_raw),
        requested_state_type=str(state_type),
        requested_market_role=_market_role_for_symbol(symbol_raw),
        execution_product_code=_execution_product_code(),
        execution_market_uid=_execution_market_uid(),
        latest_row_market_uid=str(preferred.get("market_uid")) if preferred.get("market_uid") else None,
        latest_row_symbol_raw=str(preferred.get("symbol_raw")) if preferred.get("symbol_raw") else None,
        preferred_row_freshness=freshness,
        preferred_row_age_sec=age,
        preferred_row_is_stale=(freshness == "STALE") if freshness != "UNKNOWN" else None,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(warnings),
    )


def _ground_from_row(row: dict[str, Any]) -> GroundState:
    direction = GroundDirection.UNKNOWN
    confidence = Confidence.LOW
    text = " ".join(str(row.get(key) or "").lower() for key in ("interpretation_reason", "market_bias", "pressure_bias"))
    if "sell" in text or "ask" in text or "resistance" in text:
        direction = GroundDirection.SELL_LEANING
    elif "buy" in text or "bid" in text or "support" in text:
        direction = GroundDirection.BUY_LEANING
    elif str(row.get("interpretation_bucket") or "") == "allow_structural_use":
        direction = GroundDirection.MIXED
    if str(row.get("trust_state") or "") == "trusted" and str(row.get("continuity_state") or "") == "continuous":
        confidence = Confidence.MEDIUM
    return GroundState(direction=direction, confidence=confidence, reason_codes=("market_state_adapter",))


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def snapshot_from_market_state_row(row: dict[str, Any], *, parameter_set: ParameterSet, diagnostics: LiveInputAdapterDiagnostics | None = None, temporal_rows: Iterable[dict[str, Any]] | None = None) -> AutoTradeSnapshot:
    event_ts = str(row.get("collector_ts") or row.get("exchange_ts") or "") or None
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    market_uid = str(row.get("market_uid") or f"{row.get('exchange') or 'bitflyer'}:{row.get('symbol_raw') or 'BTC_JPY'}")
    diag = diagnostics or live_input_adapter_diagnostics()
    stale_reasons = tuple(diag.blocked_by)
    fresh_ok = diag.preferred_row_freshness in {"LIVE", "QUIET"} and not stale_reasons
    temporal_flow = None
    temporal_anchor = _parse_ts(event_ts)
    if temporal_rows is not None:
        temporal_flow, _temporal_diag = build_temporal_flow_features_from_rows(
            temporal_rows,
            parameter_set=parameter_set,
            now=temporal_anchor,
        )
    temporal_usable = bool(fresh_ok and temporal_flow and temporal_flow.usable)
    trade_delta_input = _float_or_none(row.get("trade_delta"))
    trade_usable = bool(fresh_ok and trade_delta_input is not None)
    snapshot_id = build_snapshot_id(
        market_uid=market_uid,
        created_at=created_at,
        parameter_set_id=parameter_set.parameter_set_id,
        effective_event_ts=event_ts,
    )
    return AutoTradeSnapshot(
        snapshot_id=snapshot_id,
        created_at=created_at,
        market_uid=market_uid,
        parameter_set_id=parameter_set.parameter_set_id,
        logic_version=parameter_set.logic_version,
        effective_event_ts=event_ts,
        ground=_ground_from_row(row),
        usability=SnapshotUsability(
            regime=fresh_ok,
            liquidity=fresh_ok,
            trade=trade_usable,
            l4=fresh_ok,
            temporal=temporal_usable,
        ),
        inputs=CurrentMarketInputs(
            spread=_float_or_none(row.get("spread")),
            imbalance=_float_or_none(row.get("imbalance")),
            wall_ratio=_float_or_none(row.get("wall_ratio")),
            wall_side=row.get("wall_side") if isinstance(row.get("wall_side"), str) else None,
            trade_delta=trade_delta_input,
            price=_float_or_none(row.get("price")),
            mid_price=_float_or_none(row.get("mid_price")),
        ),
        temporal_flow=temporal_flow or TemporalFlowFeatures(
            windows_sec=parameter_set.temporal_flow.windows_sec,
            generated_at=created_at,
            usable=False,
            blocked_by=("temporal_flow_adapter_not_connected",),
        ),
        source_refs={
            "adapter": "autotrade.read_model.live_input_adapter",
            "latest_part_path": str(diag.latest_part_path) if diag.latest_part_path else None,
            "freshness": diag.preferred_row_freshness,
        },
        stale_reasons=stale_reasons,
    )


def load_latest_snapshot_from_market_state(*, parameter_set: ParameterSet, exchange: str = "bitflyer", symbol_raw: str = "BTC_JPY", state_type: str = "market.overview") -> tuple[AutoTradeSnapshot | None, LiveInputAdapterDiagnostics]:
    diag = live_input_adapter_diagnostics(exchange=exchange, symbol_raw=symbol_raw, state_type=state_type)
    latest = diag.latest_part_path
    rows = _read_jsonl_rows(latest) if latest is not None else []
    row = preferred_market_state_row(rows)
    if not row:
        return None, diag
    return snapshot_from_market_state_row(row, parameter_set=parameter_set, diagnostics=diag, temporal_rows=rows), diag
