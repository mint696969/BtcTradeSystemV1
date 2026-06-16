# path: ./btcts_next/src/btcts/collector_vnext/private_state.py
# desc: SR-FX private account/order state snapshot and readiness writer.

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .config import CollectorConfig, MarketIdentity
from .paths import ensure_dir
from .providers.bitflyer_private_rest import PrivateRestResult


DEFAULT_FRESHNESS_LIMITS_SEC: Dict[str, int] = {
    "collateral": 30,
    "positions": 15,
    "child_orders": 15,
    "own_executions": 30,
}

SECRET_FIELD_HINTS = (
    "api_key",
    "api_secret",
    "access-key",
    "access-sign",
    "access_timestamp",
    "access-timestamp",
    "signature",
    "secret",
)


@dataclass(frozen=True)
class PrivateEndpointSnapshot:
    name: str
    endpoint: str
    request_class: str
    ok: bool
    status_code: int
    received_ts: str | None
    payload: Dict[str, Any]
    payload_summary: Dict[str, Any]
    response_meta: Dict[str, Any]
    error: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "endpoint": self.endpoint,
            "request_class": self.request_class,
            "ok": self.ok,
            "status_code": self.status_code,
            "received_ts": self.received_ts,
            "payload": self.payload,
            "payload_summary": self.payload_summary,
            "response_meta": self.response_meta,
            "error": self.error,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def private_state_dir(cfg: CollectorConfig) -> Path:
    out = cfg.roots()["state"] / "private"
    ensure_dir(out)
    return out


def _contains_secret_key(key: str) -> bool:
    k = str(key or "").strip().lower().replace("_", "-")
    return any(hint in k for hint in SECRET_FIELD_HINTS)


def assert_no_secret_fields(value: Any, *, path: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if _contains_secret_key(str(key)):
                raise ValueError(f"secret-like field is not allowed in private state snapshot: {path}.{key}")
            assert_no_secret_fields(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            assert_no_secret_fields(item, path=f"{path}[{i}]")


def persisted_credential_diagnostics(redacted: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert runtime redacted credential diagnostics to state-safe field names.

    Runtime/CLI diagnostics may say api_secret_loaded because that is useful to the operator.
    Persisted state should avoid both secret values and secret-like field names, so state readers
    cannot accidentally start depending on secret-shaped diagnostics.
    """

    api_key_masked = str(redacted.get("api_key_masked") or "")
    pair_loaded = bool(api_key_masked) and bool(redacted.get("api_secret_loaded"))

    out: Dict[str, Any] = {
        "exchange": str(redacted.get("exchange") or ""),
        "credential_name": str(redacted.get("credential_name") or ""),
        "permission_mode": str(redacted.get("permission_mode") or ""),
        "api_key_masked": api_key_masked,
        "credential_pair_loaded": pair_loaded,
        "private_api_enabled": bool(redacted.get("private_api_enabled", False)),
        "order_send_enabled": bool(redacted.get("order_send_enabled", False)),
    }
    assert_no_secret_fields(out)
    return out


def _items(payload: Dict[str, Any]) -> list[Any]:
    items = payload.get("items")
    return items if isinstance(items, list) else []


def summarize_payload(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if name == "collateral":
        return {
            "has_collateral": "collateral" in payload,
            "has_keep_rate": "keep_rate" in payload,
            "has_require_collateral": "require_collateral" in payload,
            "has_open_position_pnl": "open_position_pnl" in payload,
        }

    items = _items(payload)
    summary: Dict[str, Any] = {
        "item_count": len(items),
        "is_empty": len(items) == 0,
    }

    if name == "positions":
        summary["nonzero_positions_known"] = True
    elif name == "child_orders":
        summary["open_order_state_known"] = True
    elif name == "own_executions":
        summary["own_fill_state_known"] = True

    return summary


def endpoint_snapshot(name: str, result: PrivateRestResult) -> PrivateEndpointSnapshot:
    payload = result.payload if isinstance(result.payload, dict) else {}
    snapshot = PrivateEndpointSnapshot(
        name=name,
        endpoint=result.endpoint,
        request_class=result.request_class,
        ok=bool(result.ok),
        status_code=int(result.status_code or 0),
        received_ts=result.received_ts,
        payload=payload,
        payload_summary=summarize_payload(name, payload),
        response_meta=result.response_meta,
        error=str(result.error or ""),
    )
    assert_no_secret_fields(snapshot.as_dict())
    return snapshot


def endpoint_freshness_ok(snapshot: PrivateEndpointSnapshot, *, now: datetime, max_age_sec: int) -> bool:
    if not snapshot.ok or not snapshot.received_ts:
        return False
    try:
        ts = datetime.fromisoformat(snapshot.received_ts.replace("Z", "+00:00"))
    except Exception:
        return False
    age = max((now - ts).total_seconds(), 0.0)
    return age <= float(max_age_sec)


def _endpoint_item_count(endpoints: Mapping[str, PrivateEndpointSnapshot], name: str) -> int:
    snap = endpoints.get(name)
    if snap is None:
        return 0
    raw = snap.payload_summary.get("item_count", 0)
    try:
        return max(int(raw), 0)
    except Exception:
        return 0


def account_clear_summary(endpoints: Mapping[str, PrivateEndpointSnapshot]) -> Dict[str, Any]:
    position_count = _endpoint_item_count(endpoints, "positions")
    open_order_count = _endpoint_item_count(endpoints, "child_orders")
    own_execution_count = _endpoint_item_count(endpoints, "own_executions")

    existing_positions_detected = position_count > 0
    existing_open_orders_detected = open_order_count > 0
    account_clear = not existing_positions_detected and not existing_open_orders_detected

    if account_clear:
        reason = "clear"
    elif existing_positions_detected and existing_open_orders_detected:
        reason = "existing_positions_and_open_orders_detected"
    elif existing_positions_detected:
        reason = "existing_positions_detected"
    else:
        reason = "existing_open_orders_detected"

    return {
        "account_clear_for_new_auto_entry": account_clear,
        "existing_positions_detected": existing_positions_detected,
        "existing_open_orders_detected": existing_open_orders_detected,
        "position_item_count": position_count,
        "open_order_item_count": open_order_count,
        "own_execution_item_count": own_execution_count,
        "reason": reason,
    }


def build_readiness(
    endpoints: Mapping[str, PrivateEndpointSnapshot],
    *,
    product_code: str,
    market_uid: str,
    freshness_limits_sec: Mapping[str, int] | None = None,
    now: datetime | None = None,
) -> Dict[str, Any]:
    limits = dict(DEFAULT_FRESHNESS_LIMITS_SEC)
    if freshness_limits_sec:
        limits.update({str(k): int(v) for k, v in freshness_limits_sec.items()})

    now_dt = now or datetime.now(timezone.utc)
    endpoint_states: Dict[str, Any] = {}
    all_ok = True
    all_fresh = True

    for name, snap in endpoints.items():
        fresh = endpoint_freshness_ok(snap, now=now_dt, max_age_sec=limits.get(name, 0))
        endpoint_states[name] = {
            "ok": snap.ok,
            "fresh": fresh,
            "status_code": snap.status_code,
            "received_ts": snap.received_ts,
            "max_age_sec": limits.get(name),
            "request_class": snap.request_class,
            "summary": snap.payload_summary,
        }
        all_ok = all_ok and snap.ok
        all_fresh = all_fresh and fresh

    state_known_and_fresh = bool(all_ok and all_fresh)
    account_clear = account_clear_summary(endpoints)
    readiness = {
        "ts": now_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "product_code": product_code,
        "market_uid": market_uid,
        "private_state_ok": state_known_and_fresh,
        "private_state_known_and_fresh": state_known_and_fresh,
        "all_endpoints_ok": bool(all_ok),
        "all_endpoints_fresh": bool(all_fresh),
        "account_clear_for_new_auto_entry": bool(account_clear["account_clear_for_new_auto_entry"]),
        "existing_positions_detected": bool(account_clear["existing_positions_detected"]),
        "existing_open_orders_detected": bool(account_clear["existing_open_orders_detected"]),
        "account_state_summary": account_clear,
        "order_send_allowed": False,
        "reason": (
            "ok_clear"
            if state_known_and_fresh and bool(account_clear["account_clear_for_new_auto_entry"])
            else "account_not_clear_for_new_auto_entry"
            if state_known_and_fresh
            else "private_state_not_ready"
        ),
        "endpoints": endpoint_states,
    }
    assert_no_secret_fields(readiness)
    return readiness


def build_private_state_snapshot(
    *,
    cfg: CollectorConfig,
    execution_market: MarketIdentity,
    endpoints: Mapping[str, PrivateEndpointSnapshot],
    credential_diagnostics: Dict[str, Any],
    readiness: Dict[str, Any],
) -> Dict[str, Any]:
    exe = execution_market.normalized()
    snapshot = {
        "ts": utc_now_iso(),
        "collector_id": cfg.collector_id,
        "collector_role": cfg.collector_role,
        "exchange": exe.exchange,
        "product_code": exe.product_code,
        "market_type": exe.market_type,
        "market_role": exe.role,
        "market_uid": exe.market_uid,
        "source": "private_rest",
        "credential": persisted_credential_diagnostics(credential_diagnostics),
        "readiness": readiness,
        "endpoints": {name: snap.as_dict() for name, snap in endpoints.items()},
    }
    assert_no_secret_fields(snapshot)
    return snapshot


def write_private_state_files(
    cfg: CollectorConfig,
    *,
    snapshot: Dict[str, Any],
    readiness: Dict[str, Any],
    state_filename: str = "bitflyer_fx_state.json",
    readiness_filename: str = "bitflyer_fx_readiness.json",
) -> Dict[str, str]:
    out_dir = private_state_dir(cfg)
    state_path = out_dir / state_filename
    readiness_path = out_dir / readiness_filename

    assert_no_secret_fields(snapshot)
    assert_no_secret_fields(readiness)

    state_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    readiness_path.write_text(json.dumps(readiness, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "state_path": str(state_path),
        "readiness_path": str(readiness_path),
    }
