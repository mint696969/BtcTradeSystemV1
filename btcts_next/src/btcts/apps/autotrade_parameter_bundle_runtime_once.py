# path: ./btcts_next/src/btcts/apps/autotrade_parameter_bundle_runtime_once.py
# desc: CLI entry for one-shot AutoTrade parameter bundle runtime operations. No broker execution.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from btcts.autotrade.config.bundle_events import ParameterBundleEventType
from btcts.autotrade.config.bundle_runtime_store import (
    activate_parameter_bundle_runtime,
    build_parameter_bundle_runtime_status,
    initialize_default_parameter_bundle_runtime,
    rollback_parameter_bundle_runtime,
)


def _csv_tuple(value: str | None) -> tuple[str, ...]:
    if value is None or not value.strip():
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _event_type_for_action(action: str) -> ParameterBundleEventType:
    if action == "activate-shadow":
        return ParameterBundleEventType.BUNDLE_ACTIVATED_SHADOW
    if action == "activate-paper":
        return ParameterBundleEventType.BUNDLE_ACTIVATED_PAPER
    if action == "activate-live":
        return ParameterBundleEventType.BUNDLE_ACTIVATED_LIVE
    raise ValueError(f"unsupported activation action: {action!r}")


def _result_to_dict(result: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "event": result.event.to_dict(),
        "registry": result.registry.to_dict(),
        "bundle_path": str(result.bundle_path) if result.bundle_path is not None else None,
        "registry_path": str(result.registry_path),
        "event_ledger_path": str(result.event_ledger_path),
        "bundle_written": result.bundle_written,
        "registry_written": result.registry_written,
        "event_appended": result.event_appended,
        "would_send_to_broker": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one AutoTrade parameter bundle runtime operation. Writes only parameter bundle files/registry/event ledger."
    )
    sub = parser.add_subparsers(dest="action", required=True)

    status = sub.add_parser("status", help="Print read-only parameter bundle runtime status.")
    status.add_argument("--registry-path")
    status.add_argument("--event-ledger-path")
    status.add_argument("--max-events", type=int, default=5)

    init = sub.add_parser("init-default", help="Create the default split regime/trade parameter bundle in runtime store.")
    init.add_argument("--event-ts", required=True)
    init.add_argument("--reason", required=True)
    init.add_argument("--created-by", required=True)
    init.add_argument("--registry-path")
    init.add_argument("--event-ledger-path")
    init.add_argument("--source-decision-ids", default="")
    init.add_argument("--gpt-review-ids", default="")
    init.add_argument("--human-approval-id")
    init.add_argument("--notes", default="")

    for name in ("activate-shadow", "activate-paper", "activate-live"):
        act = sub.add_parser(name, help=f"Activate a parameter bundle for {name.removeprefix('activate-')} stage.")
        act.add_argument("--event-ts", required=True)
        act.add_argument("--bundle-id", required=True)
        act.add_argument("--reason", required=True)
        act.add_argument("--approved-by", required=True)
        act.add_argument("--registry-path")
        act.add_argument("--event-ledger-path")
        act.add_argument("--source-decision-ids", default="")
        act.add_argument("--gpt-review-ids", default="")
        act.add_argument("--human-approval-id")
        act.add_argument("--notes", default="")

    rollback = sub.add_parser("rollback", help="Rollback a parameter bundle for shadow/paper/live stage.")
    rollback.add_argument("--event-ts", required=True)
    rollback.add_argument("--rollback-bundle-id", required=True)
    rollback.add_argument("--target-stage", required=True, choices=("shadow", "paper", "live"))
    rollback.add_argument("--reason", required=True)
    rollback.add_argument("--approved-by", required=True)
    rollback.add_argument("--registry-path")
    rollback.add_argument("--event-ledger-path")
    rollback.add_argument("--source-decision-ids", default="")
    rollback.add_argument("--gpt-review-ids", default="")
    rollback.add_argument("--human-approval-id")
    rollback.add_argument("--notes", default="")

    return parser.parse_args(argv)


def _optional_path(value: str | None) -> Path | None:
    return Path(value) if value else None


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    if args.action == "status":
        data = build_parameter_bundle_runtime_status(
            registry_path=_optional_path(args.registry_path),
            event_ledger_path=_optional_path(args.event_ledger_path),
            max_events=args.max_events,
        )
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0

    if args.action == "init-default":
        result = initialize_default_parameter_bundle_runtime(
            event_ts=args.event_ts,
            reason=args.reason,
            created_by=args.created_by,
            registry_path=_optional_path(args.registry_path),
            event_ledger_path=_optional_path(args.event_ledger_path),
            source_decision_ids=_csv_tuple(args.source_decision_ids),
            gpt_review_ids=_csv_tuple(args.gpt_review_ids),
            human_approval_id=args.human_approval_id,
            notes=args.notes,
        )
    elif args.action in {"activate-shadow", "activate-paper", "activate-live"}:
        result = activate_parameter_bundle_runtime(
            event_type=_event_type_for_action(args.action),
            event_ts=args.event_ts,
            new_bundle_id=args.bundle_id,
            reason=args.reason,
            approved_by=args.approved_by,
            registry_path=_optional_path(args.registry_path),
            event_ledger_path=_optional_path(args.event_ledger_path),
            source_decision_ids=_csv_tuple(args.source_decision_ids),
            gpt_review_ids=_csv_tuple(args.gpt_review_ids),
            human_approval_id=args.human_approval_id,
            notes=args.notes,
        )
    elif args.action == "rollback":
        result = rollback_parameter_bundle_runtime(
            event_ts=args.event_ts,
            rollback_bundle_id=args.rollback_bundle_id,
            target_stage=args.target_stage,
            reason=args.reason,
            approved_by=args.approved_by,
            registry_path=_optional_path(args.registry_path),
            event_ledger_path=_optional_path(args.event_ledger_path),
            source_decision_ids=_csv_tuple(args.source_decision_ids),
            gpt_review_ids=_csv_tuple(args.gpt_review_ids),
            human_approval_id=args.human_approval_id,
            notes=args.notes,
        )
    else:
        raise ValueError(f"unsupported action: {args.action!r}")

    print(json.dumps(_result_to_dict(result), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
