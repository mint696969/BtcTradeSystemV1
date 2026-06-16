# path: ./btcts_next/src/btcts/apps/bitflyer_fx_public_rest_check_once.py
# desc: One-shot FX public REST collection check for SR-FX execution-market data.

from __future__ import annotations

import json
from typing import Dict

from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.fx_public_rest import (
    FxPublicRestError,
    emit_fx_rest_board_snapshot,
    emit_fx_rest_trades,
)
from btcts.collector_vnext.ids import SequenceManager, make_session_id
from btcts.collector_vnext.rate_runtime import VNextRateRuntime


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    rate_runtime = VNextRateRuntime.build(cfg)
    seq = SequenceManager.start()
    session_id = make_session_id(cfg.collector_id)

    result: Dict[str, object] = {
        "ok": True,
        "stage": "bitflyer_fx_public_rest_check_once",
        "session_id": session_id,
        "market_identity": cfg.market_identity_summary(),
        "checks": {},
    }

    try:
        board = emit_fx_rest_board_snapshot(seq, session_id, rate_runtime=rate_runtime)
        trades = emit_fx_rest_trades(seq, session_id, rate_runtime=rate_runtime)
    except FxPublicRestError as exc:
        result["ok"] = False
        result["error"] = str(exc)
        result["status_code"] = exc.status_code
        result["retry_after_sec"] = exc.retry_after_sec
        _print_json(result)
        return 3

    result["checks"] = {
        "fx_board_snapshot": board,
        "fx_executions": trades,
    }

    # Mechanical safety proof: no FX execution-market output should be written under symbol=BTC_JPY.
    paths = [str(board.get("raw_path", "")), str(board.get("canonical_path", "")), str(trades.get("raw_path", "")), str(trades.get("canonical_path", ""))]
    result["path_guard"] = {
        "all_paths_are_fx_symbol": all("symbol=FX_BTC_JPY" in p for p in paths if p),
        "no_path_is_spot_symbol": not any("symbol=BTC_JPY" in p for p in paths if p),
    }
    if not result["path_guard"]["all_paths_are_fx_symbol"] or not result["path_guard"]["no_path_is_spot_symbol"]:  # type: ignore[index]
        result["ok"] = False

    _print_json(result)
    return 0 if bool(result["ok"]) else 4


if __name__ == "__main__":
    raise SystemExit(main())
