# path: ./btcts_next/src/btcts/apps/bitflyer_fx_market_state_rest_snapshot_once.py
# desc: One-shot SR-FX market_state writer from public REST board. No broker calls.

from __future__ import annotations

import json

from btcts.autotrade.read_model.fx_market_state_rest_snapshot import write_fx_market_state_from_public_rest_board
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.rate_runtime import VNextRateRuntime


def main() -> int:
    cfg = load_config()
    result = write_fx_market_state_from_public_rest_board(rate_runtime=VNextRateRuntime.build(cfg))
    out = {
        "stage": "bitflyer_fx_market_state_rest_snapshot_once",
        "ok": result.ok,
        "result": result.to_dict(),
        "read_only": False,
        "would_send_to_broker": False,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
