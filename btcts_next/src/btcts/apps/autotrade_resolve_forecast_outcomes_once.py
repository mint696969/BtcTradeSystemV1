# path: ./btcts_next/src/btcts/apps/autotrade_resolve_forecast_outcomes_once.py
# desc: CLI entry for one-shot AutoTrade forecast outcome resolver. No broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.ledger import resolve_due_shadow_forecast_outcomes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve due AutoTrade shadow forecasts once against target-time market_state actuals.")
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol-raw", default="BTC_JPY")
    parser.add_argument("--state-type", default="market.overview")
    parser.add_argument("--max-decision-lines", type=int, default=1000)
    parser.add_argument("--max-actual-match-age-sec", type=float, default=45.0)
    parser.add_argument("--no-persist", action="store_true", help="Do not append to forecast outcome ledger.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = resolve_due_shadow_forecast_outcomes(
        exchange=args.exchange,
        symbol_raw=args.symbol_raw,
        state_type=args.state_type,
        max_decision_lines=args.max_decision_lines,
        max_actual_match_age_sec=args.max_actual_match_age_sec,
        persist=not args.no_persist,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 2 if result.blocked_by else 0


if __name__ == "__main__":
    raise SystemExit(main())
