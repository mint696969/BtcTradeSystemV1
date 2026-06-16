# path: ./btcts_next/src/btcts/apps/autotrade_readiness_once.py
# desc: CLI entry for one-shot AutoTrade live readiness preflight. Read-only, no broker execution.

from __future__ import annotations

import argparse
import json

from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate one-shot AutoTrade readiness preflight for a target mode.")
    parser.add_argument("--current-mode", default=AutoTradeMode.ARMED_DRY_RUN.value, choices=[mode.value for mode in AutoTradeMode])
    parser.add_argument("--target-mode", default=AutoTradeMode.LIVE_MIN_SIZE.value, choices=[mode.value for mode in AutoTradeMode])
    parser.add_argument("--human-confirmed", action="store_true")
    parser.add_argument("--allow-warnings", action="store_true")
    parser.add_argument("--disable-parameter-bundle-runtime-check", action="store_true", help="Do not require active parameter bundle runtime status for dangerous target modes.")
    parser.add_argument("--required-parameter-bundle-stage", default="live", choices=("shadow", "paper", "live", "rollback", "last_known_good", "pending_draft"))
    parser.add_argument("--max-observer-run-age-sec", type=float, default=120.0)
    parser.add_argument("--max-lines", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate_autotrade_live_readiness(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        human_confirmed=args.human_confirmed,
        allow_warnings=args.allow_warnings,
        enforce_parameter_bundle_runtime=not args.disable_parameter_bundle_runtime_check,
        required_parameter_bundle_stage=args.required_parameter_bundle_stage,
        max_observer_run_age_sec=args.max_observer_run_age_sec,
        max_lines=args.max_lines,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
