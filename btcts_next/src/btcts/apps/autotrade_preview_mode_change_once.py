# path: ./btcts_next/src/btcts/apps/autotrade_preview_mode_change_once.py
# desc: CLI entry for read-only mode-change command applier preview. No ledger append, no broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.execution import preview_latest_mode_change_command_apply


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview latest unapplied accepted AutoTrade REQUEST_MODE_CHANGE without appending mode_state.")
    parser.add_argument("--max-lines", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = preview_latest_mode_change_command_apply(max_lines=args.max_lines)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.would_apply else 2


if __name__ == "__main__":
    raise SystemExit(main())
