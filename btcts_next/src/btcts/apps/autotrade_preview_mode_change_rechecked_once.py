# path: ./btcts_next/src/btcts/apps/autotrade_preview_mode_change_rechecked_once.py
# desc: CLI entry for read-only mode-change command applier preview with readiness recheck. No ledger append, no broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.execution import preview_latest_mode_change_command_apply_with_readiness_recheck


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview latest AutoTrade REQUEST_MODE_CHANGE with readiness recheck without appending mode_state.")
    parser.add_argument("--max-lines", type=int, default=1000)
    parser.add_argument("--max-observer-run-age-sec", type=float, default=120.0)
    parser.add_argument("--allow-warnings", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = preview_latest_mode_change_command_apply_with_readiness_recheck(
        max_lines=args.max_lines,
        max_observer_run_age_sec=args.max_observer_run_age_sec,
        allow_warnings=args.allow_warnings,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.would_apply else 2


if __name__ == "__main__":
    raise SystemExit(main())
