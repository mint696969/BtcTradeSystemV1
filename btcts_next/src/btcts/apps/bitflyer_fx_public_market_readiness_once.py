# path: ./btcts_next/src/btcts/apps/bitflyer_fx_public_market_readiness_once.py
# desc: One-shot SR-FX public market readiness writer. Public market data only; no broker calls.

from __future__ import annotations

import json
import os
from typing import Dict

from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.fx_public_market_readiness import build_fx_public_market_readiness
from btcts.collector_vnext.fx_public_rest import FxPublicRestError, emit_fx_rest_board_snapshot, emit_fx_rest_trades
from btcts.collector_vnext.fx_public_ws import preflight_fx_public_ws
from btcts.collector_vnext.ids import SequenceManager, make_session_id
from btcts.collector_vnext.paths import ensure_dir
from btcts.collector_vnext.rate_runtime import VNextRateRuntime


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _write_json(path, payload: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    rate_runtime = VNextRateRuntime.build(cfg)
    seq = SequenceManager.start()
    session_id = make_session_id(cfg.collector_id)
    require_ws_ok = _env_bool("BTCTS_REQUIRE_FX_WS_OK_FOR_PUBLIC_MARKET", True)
    out_path = cfg.roots()["state"] / "public" / "bitflyer_fx_public_market_readiness.json"

    board: Dict[str, object]
    trades: Dict[str, object]
    rest_error: Dict[str, object] | None = None
    try:
        board = dict(emit_fx_rest_board_snapshot(seq, session_id, rate_runtime=rate_runtime))
        trades = dict(emit_fx_rest_trades(seq, session_id, rate_runtime=rate_runtime))
    except FxPublicRestError as exc:
        rest_error = {"error": str(exc), "status_code": exc.status_code, "retry_after_sec": exc.retry_after_sec}
        board = {"ok": False, "product_code": cfg.execution_market.product_code, "market_uid": cfg.execution_market.market_uid, "market_role": cfg.execution_market.role}
        trades = {"ok": False, "product_code": cfg.execution_market.product_code, "market_uid": cfg.execution_market.market_uid, "market_role": cfg.execution_market.role, "trade_count": 0}

    ws_preflight = dict(preflight_fx_public_ws())
    readiness = build_fx_public_market_readiness(
        board_check=board,
        executions_check=trades,
        ws_preflight=ws_preflight,
        require_ws_ok=require_ws_ok,
    )

    result: Dict[str, object] = {
        "ok": readiness.ok,
        "stage": "bitflyer_fx_public_market_readiness_once",
        "session_id": session_id,
        "public_market_readiness_path": str(out_path),
        "market_identity": cfg.market_identity_summary(),
        "require_ws_ok": require_ws_ok,
        "checks": {
            "fx_rest_board_snapshot": board,
            "fx_rest_executions": trades,
            "fx_ws_preflight": ws_preflight,
        },
        "public_market_readiness": readiness.to_dict(),
    }
    if rest_error is not None:
        result["rest_error"] = rest_error

    _write_json(out_path, result)
    _print_json(result)
    # Return 0 even when not ready; false readiness is expected when WS/SSL is not usable.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
