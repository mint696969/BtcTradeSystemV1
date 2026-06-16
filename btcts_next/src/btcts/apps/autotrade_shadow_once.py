# path: ./btcts_next/src/btcts/apps/autotrade_shadow_once.py
# desc: CLI entry for one-shot AutoTrade shadow cycle. No broker execution.

from __future__ import annotations

import argparse
import json
from pathlib import Path

from btcts.autotrade.shadow_cycle import run_shadow_cycle_once


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one AutoTrade shadow cycle from latest market_state.")
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol-raw", default="BTC_JPY")
    parser.add_argument("--state-type", default="market.overview")
    parser.add_argument("--no-persist", action="store_true", help="Do not append to shadow decision ledger.")
    parser.add_argument("--use-runtime-parameter-bundle", action="store_true", help="Load the active runtime parameter bundle and record its split identity in the decision ledger.")
    parser.add_argument("--parameter-bundle-stage", default="shadow", choices=("shadow", "paper", "live", "rollback", "last_known_good", "pending_draft"))
    parser.add_argument("--parameter-bundle-id", help="Explicit parameter bundle id. Overrides the selected registry stage.")
    parser.add_argument("--parameter-bundle-registry-path", help="Optional registry path for tests or controlled runtime operations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_shadow_cycle_once(
        exchange=args.exchange,
        symbol_raw=args.symbol_raw,
        state_type=args.state_type,
        persist=not args.no_persist,
        load_runtime_parameter_bundle=args.use_runtime_parameter_bundle,
        parameter_bundle_stage=args.parameter_bundle_stage,
        parameter_bundle_id=args.parameter_bundle_id,
        parameter_bundle_registry_path=Path(args.parameter_bundle_registry_path) if args.parameter_bundle_registry_path else None,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.result.snapshot_id is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
