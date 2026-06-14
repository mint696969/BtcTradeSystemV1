# path: ./btcts_next/src/btcts/collector_vnext/fx_public_market_readiness.py
# desc: SR-FX public market readiness from FX REST collection and FX WS preflight. No broker calls.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple


@dataclass(frozen=True)
class FxPublicMarketReadinessResult:
    ok: bool
    product_code: str
    market_uid: str
    market_role: str
    rest_market_ok: bool
    ws_market_ok: bool
    rest_board_ok: bool
    rest_executions_ok: bool
    rest_trade_count: int
    ws_ssl_verify: bool
    require_ws_ok: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    read_only: bool = True
    would_send_to_broker: bool = False
    contract_version: str = "sr_fx_public_market_readiness.v1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def _int_at(mapping: Mapping[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(mapping.get(key, default) or 0)
    except Exception:
        return default


def _path_values(*items: Mapping[str, Any]) -> tuple[str, ...]:
    paths: list[str] = []
    for item in items:
        for key in ("raw_path", "canonical_path"):
            raw = item.get(key)
            if raw:
                paths.append(str(raw))
    return tuple(paths)


def build_fx_public_market_readiness(
    *,
    board_check: Mapping[str, Any],
    executions_check: Mapping[str, Any],
    ws_preflight: Mapping[str, Any],
    require_ws_ok: bool = True,
) -> FxPublicMarketReadinessResult:
    blocked: list[str] = []
    warnings: list[str] = []

    product_code = str(board_check.get("product_code") or executions_check.get("product_code") or ws_preflight.get("product_code") or "")
    market_uid = str(board_check.get("market_uid") or executions_check.get("market_uid") or ws_preflight.get("market_uid") or "")
    market_role = str(board_check.get("market_role") or executions_check.get("market_role") or ws_preflight.get("market_role") or "")

    if product_code != "FX_BTC_JPY":
        blocked.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        blocked.append("execution_market_uid_mismatch")
    if market_role != "execution":
        blocked.append("execution_market_role_mismatch")

    rest_board_ok = _bool_at(board_check, "ok") and str(board_check.get("request_class") or "") == "public_rest_market_data"
    rest_executions_ok = _bool_at(executions_check, "ok") and str(executions_check.get("request_class") or "") == "public_rest_market_data"
    rest_trade_count = _int_at(executions_check, "trade_count")
    if not rest_board_ok:
        blocked.append("fx_rest_board_not_ok")
    if not rest_executions_ok:
        blocked.append("fx_rest_executions_not_ok")
    if rest_trade_count <= 0:
        blocked.append("fx_rest_trade_count_zero")

    paths = _path_values(board_check, executions_check)
    if paths and not all("symbol=FX_BTC_JPY" in p for p in paths):
        blocked.append("fx_public_rest_path_not_fx_symbol")
    if any("symbol=BTC_JPY" in p for p in paths):
        blocked.append("fx_public_rest_path_contains_spot_symbol")

    ws_market_ok = _bool_at(ws_preflight, "ok")
    ws_ssl_verify = _bool_at(ws_preflight, "ssl_verify", True)
    if not ws_ssl_verify:
        blocked.append("ws_ssl_verify_disabled")
    if require_ws_ok and not ws_market_ok:
        blocked.append("fx_public_ws_preflight_not_ok")
    elif not ws_market_ok:
        warnings.append("fx_public_ws_preflight_not_ok")

    attempts = ws_preflight.get("attempts")
    if isinstance(attempts, Mapping):
        for name, attempt in attempts.items():
            if isinstance(attempt, Mapping) and not attempt.get("ok"):
                err = attempt.get("error_class")
                warnings.append(f"ws_{name}_not_ok" if not err else f"ws_{name}_not_ok:{err}")

    rest_market_ok = rest_board_ok and rest_executions_ok and rest_trade_count > 0 and not any(
        b in blocked for b in ("fx_public_rest_path_not_fx_symbol", "fx_public_rest_path_contains_spot_symbol")
    )
    ok = rest_market_ok and (ws_market_ok or not require_ws_ok) and not blocked

    return FxPublicMarketReadinessResult(
        ok=bool(ok),
        product_code=product_code,
        market_uid=market_uid,
        market_role=market_role,
        rest_market_ok=bool(rest_market_ok),
        ws_market_ok=bool(ws_market_ok),
        rest_board_ok=bool(rest_board_ok),
        rest_executions_ok=bool(rest_executions_ok),
        rest_trade_count=rest_trade_count,
        ws_ssl_verify=bool(ws_ssl_verify),
        require_ws_ok=bool(require_ws_ok),
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        read_only=True,
        would_send_to_broker=False,
    )
