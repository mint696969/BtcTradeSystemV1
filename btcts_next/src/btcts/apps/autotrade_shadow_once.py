# path: ./btcts_next/src/btcts/apps/autotrade_shadow_once.py
# desc: CLI entry for one-shot AutoTrade shadow cycle. No broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.shadow_cycle import run_shadow_cycle_once


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one AutoTrade shadow cycle from latest market_state.")
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol-raw", default="BTC_JPY")
    parser.add_argument("--state-type", default="market.overview")
    parser.add_argument("--no-persist", action="store_true", help="Do not append to shadow decision ledger.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_shadow_cycle_once(
        exchange=args.exchange,
        symbol_raw=args.symbol_raw,
        state_type=args.state_type,
        persist=not args.no_persist,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.result.snapshot_id is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
