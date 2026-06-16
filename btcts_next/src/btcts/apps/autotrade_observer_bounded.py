# path: ./btcts_next/src/btcts/apps/autotrade_observer_bounded.py
# desc: CLI entry for bounded AutoTrade observer cycle. No broker execution.

from __future__ import annotations

import argparse
import json
from pathlib import Path

from btcts.autotrade.observer_cycle import run_observer_cycle_bounded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded AutoTrade observer cycles: shadow decision + forecast outcome resolution.")
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol-raw", default="BTC_JPY")
    parser.add_argument("--state-type", default="market.overview")
    parser.add_argument("--max-cycles", type=int, required=True)
    parser.add_argument("--interval-sec", type=float, default=0.0)
    parser.add_argument("--max-decision-lines", type=int, default=1000)
    parser.add_argument("--max-actual-match-age-sec", type=float, default=45.0)
    parser.add_argument("--no-persist", action="store_true", help="Do not append shadow decisions or forecast outcomes.")
    parser.add_argument("--no-run-record", action="store_true", help="Do not append observer run summary record.")
    parser.add_argument("--allow-duplicate-snapshot", action="store_true", help="Append shadow decisions even when snapshot_id is unchanged.")
    parser.add_argument("--use-runtime-parameter-bundle", action="store_true", help="Load the active runtime parameter bundle for shadow decisions inside observer cycles.")
    parser.add_argument("--parameter-bundle-stage", default="shadow", choices=("shadow", "paper", "live", "rollback", "last_known_good", "pending_draft"))
    parser.add_argument("--parameter-bundle-id", help="Explicit parameter bundle id. Overrides the selected registry stage.")
    parser.add_argument("--parameter-bundle-registry-path", help="Optional registry path for tests or controlled runtime operations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_observer_cycle_bounded(
        exchange=args.exchange,
        symbol_raw=args.symbol_raw,
        state_type=args.state_type,
        max_cycles=args.max_cycles,
        interval_sec=args.interval_sec,
        persist=not args.no_persist,
        max_decision_lines=args.max_decision_lines,
        max_actual_match_age_sec=args.max_actual_match_age_sec,
        skip_duplicate_snapshot=not args.allow_duplicate_snapshot,
        persist_run_record=not args.no_run_record,
        load_runtime_parameter_bundle=args.use_runtime_parameter_bundle,
        parameter_bundle_stage=args.parameter_bundle_stage,
        parameter_bundle_id=args.parameter_bundle_id,
        parameter_bundle_registry_path=Path(args.parameter_bundle_registry_path) if args.parameter_bundle_registry_path else None,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.completed_cycles == args.max_cycles else 2


if __name__ == "__main__":
    raise SystemExit(main())
