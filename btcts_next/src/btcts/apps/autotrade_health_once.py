# path: ./btcts_next/src/btcts/apps/autotrade_health_once.py
# desc: CLI entry for one-shot AutoTrade runtime health snapshot. Read-only, no broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.health import build_autotrade_runtime_health_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print one-shot AutoTrade runtime health snapshot.")
    parser.add_argument("--max-observer-run-age-sec", type=float, default=120.0)
    parser.add_argument("--max-lines", type=int, default=1000)
    parser.add_argument("--strict-warn", action="store_true", help="Return exit code 1 when health_state is warn.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = build_autotrade_runtime_health_snapshot(
        max_observer_run_age_sec=args.max_observer_run_age_sec,
        max_lines=args.max_lines,
    )
    print(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2, default=str))
    if snapshot.blocked_by:
        return 2
    if args.strict_warn and snapshot.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
