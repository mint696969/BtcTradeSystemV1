# path: ./btcts_next/src/btcts/apps/autotrade_apply_mode_change_rechecked_once.py
# desc: CLI entry for one-shot mode-change command applier with readiness recheck. Mode-state ledger only; no broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.execution import apply_latest_mode_change_command_once_with_readiness_recheck


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply latest accepted AutoTrade REQUEST_MODE_CHANGE with fresh readiness recheck.")
    parser.add_argument("--max-lines", type=int, default=1000)
    parser.add_argument("--max-observer-run-age-sec", type=float, default=120.0)
    parser.add_argument("--allow-warnings", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = apply_latest_mode_change_command_once_with_readiness_recheck(
        max_lines=args.max_lines,
        max_observer_run_age_sec=args.max_observer_run_age_sec,
        allow_warnings=args.allow_warnings,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.applied else 2


if __name__ == "__main__":
    raise SystemExit(main())
