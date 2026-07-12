# path: ./btcts_next/src/btcts/prediction/market_regime/current_state_persistence.py
# desc: Pure/read-write bounded persistence for canonical MarketRegime current-state continuity. No scheduler, broker, AutoTrade, or order behavior.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

CURRENT_STATE_PERSISTENCE_VERSION = "prediction.market_regime.current_state_persistence.mr_f2.v1"
CURRENT_STATE_RELPATH = "prediction/market_regime/current_state.json"


def _parse_utc(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_sec(started_at: str, observed_at: str) -> int | None:
    start = _parse_utc(started_at)
    end = _parse_utc(observed_at)
    if start is None or end is None or end < start:
        return None
    return int((end - start).total_seconds())


def build_persisted_current_state(
    *,
    previous: Mapping[str, Any] | None,
    regime_code: str,
    observed_at: str,
    estimator_version: str,
    source_cutoff_time: str,
) -> dict[str, Any]:
    prior = dict(previous or {})
    regime = str(regime_code or "UNKNOWN").strip().upper() or "UNKNOWN"
    previous_regime = str(prior.get("regime_code") or "UNKNOWN").strip().upper() or "UNKNOWN"
    previous_started_at = str(prior.get("state_started_at") or "")

    if regime == "UNKNOWN" or _parse_utc(observed_at) is None:
        return {
            "schema_version": CURRENT_STATE_PERSISTENCE_VERSION,
            "regime_code": "UNKNOWN",
            "observed_at": observed_at,
            "state_started_at": "",
            "state_age_sec": None,
            "transition_detected": False,
            "previous_regime_code": previous_regime,
            "persistence_status": "unavailable",
            "estimator_version": estimator_version,
            "source_cutoff_time": source_cutoff_time,
            "read_only_sources": True,
            "would_send_to_broker": False,
        }

    continuing = previous_regime == regime and _parse_utc(previous_started_at) is not None
    state_started_at = previous_started_at if continuing else observed_at
    return {
        "schema_version": CURRENT_STATE_PERSISTENCE_VERSION,
        "regime_code": regime,
        "observed_at": observed_at,
        "state_started_at": state_started_at,
        "state_age_sec": _age_sec(state_started_at, observed_at),
        "transition_detected": previous_regime not in {"", "UNKNOWN", regime},
        "previous_regime_code": previous_regime,
        "persistence_status": "continued" if continuing else "started",
        "estimator_version": estimator_version,
        "source_cutoff_time": source_cutoff_time,
        "read_only_sources": True,
        "would_send_to_broker": False,
    }


def read_persisted_current_state(root: str | Path) -> dict[str, Any]:
    path = Path(root) / CURRENT_STATE_RELPATH
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def write_persisted_current_state(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(root) / CURRENT_STATE_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return {
        "ok": True,
        "current_state_json": CURRENT_STATE_RELPATH,
        "regime_code": str(payload.get("regime_code") or "UNKNOWN"),
        "state_started_at": str(payload.get("state_started_at") or ""),
        "state_age_sec": payload.get("state_age_sec"),
        "would_send_to_broker": False,
    }
