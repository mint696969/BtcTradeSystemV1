# path: ./btcts_next/src/btcts/prediction/market_regime/tools/runtime_horizon_collection.py
# desc: MR-F9.19M operator CLI for prepare/status/stop of one bounded 24h D-hot collection. Start remains fail-closed.

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_collection_authorization import (
    build_runtime_horizon_collection_start_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    build_runtime_horizon_collection_plan,
    validate_runtime_horizon_collection_plan,
)
from btcts.prediction.market_regime.runtime_horizon_collection_lease import (
    read_runtime_horizon_collection_lease,
)
from btcts.prediction.market_regime.runtime_horizon_collection_recovery import (
    recover_runtime_horizon_collection_runs,
)
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    read_runtime_horizon_collection_state,
    request_runtime_horizon_collection_stop,
)

TOOL_VERSION = "prediction.market_regime.tools.runtime_horizon_collection.mr_f9_19m.v1"
DEFAULT_DHOT_ROOT = Path(r"D:\btc_ts_hot")
DEFAULT_CONTROL_ROOT = Path(r"D:\btc_ts_hot")


def utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _read_mapping(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, Mapping):
        raise ValueError("runtime_horizon_collection_tool_payload_invalid")
    return dict(payload)


def plan_file_path(control_root: str | Path, collection_id: str) -> Path:
    return (
        Path(control_root)
        / "prediction/market_regime/runtime_horizon_collections"
        / f"collection_id={collection_id}"
        / "plan.json"
    )


def authorization_file_path(control_root: str | Path, collection_id: str) -> Path:
    return plan_file_path(control_root, collection_id).with_name("start_authorization.json")


def prepare_runtime_horizon_collection(
    *,
    source_root: str | Path,
    destination_root: str | Path,
    control_root: str | Path,
    shadow_candidate_id: str,
    operator_id: str,
    planned_start_utc: str,
    authorization_created_at: str,
    ttl_sec: int = 300,
) -> Mapping[str, Any]:
    plan = build_runtime_horizon_collection_plan(
        source_root=source_root,
        destination_root=destination_root,
        shadow_candidate_id=shadow_candidate_id,
        operator_id=operator_id,
        planned_start_utc=planned_start_utc,
    )
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at=authorization_created_at,
        expected_dhot_root=destination_root,
        ttl_sec=ttl_sec,
    )
    plan_path = plan_file_path(control_root, str(plan["collection_id"]))
    auth_path = authorization_file_path(control_root, str(plan["collection_id"]))
    _atomic_write_json(plan_path, plan)
    _atomic_write_json(auth_path, package)
    return {
        "schema_version": TOOL_VERSION,
        "event": "PREPARED",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "plan_path": str(plan_path),
        "authorization_path": str(auth_path),
        "expected_authorization_text": package["expected_authorization_text"],
        "authorization_expires_at": package["expires_at"],
        "human_authorized": False,
        "collection_started": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "order_submission_allowed": False,
    }


def load_runtime_horizon_collection_plan(path: str | Path) -> Mapping[str, Any]:
    plan = _read_mapping(Path(path))
    validate_runtime_horizon_collection_plan(plan)
    return plan


def status_runtime_horizon_collection(
    *,
    plan_path: str | Path,
    control_root: str | Path,
    include_recovery: bool = False,
) -> Mapping[str, Any]:
    plan = load_runtime_horizon_collection_plan(plan_path)
    state = read_runtime_horizon_collection_state(control_root, plan=plan)
    lease = read_runtime_horizon_collection_lease(control_root, plan=plan)
    recovery: Mapping[str, Any] = {}
    if include_recovery:
        recovery = recover_runtime_horizon_collection_runs(plan["destination_root"], plan=plan)
    return {
        "schema_version": TOOL_VERSION,
        "event": "STATUS",
        "collection_id": plan["collection_id"],
        "plan_sha256": plan["plan_sha256"],
        "planned_start_utc": plan["planned_start_utc"],
        "planned_end_utc": plan["planned_end_utc"],
        "state_present": bool(state),
        "state": dict(state),
        "lease_present": bool(lease),
        "lease": dict(lease),
        "recovery_included": include_recovery,
        "recovery": dict(recovery),
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "order_submission_allowed": False,
    }


def stop_runtime_horizon_collection(
    *,
    plan_path: str | Path,
    control_root: str | Path,
    requested_at: str | None = None,
) -> Mapping[str, Any]:
    plan = load_runtime_horizon_collection_plan(plan_path)
    receipt = request_runtime_horizon_collection_stop(
        control_root,
        plan=plan,
        requested_at=requested_at,
    )
    return {
        "schema_version": TOOL_VERSION,
        "event": "STOP_REQUESTED",
        "collection_id": plan["collection_id"],
        **dict(receipt),
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "detached_process_started": False,
        "order_submission_allowed": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare/status/stop one bounded MR-F9 24h collection.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare")
    prepare.add_argument("--source-root", default=str(DEFAULT_DHOT_ROOT))
    prepare.add_argument("--destination-root", default=str(DEFAULT_DHOT_ROOT))
    prepare.add_argument("--control-root", default=str(DEFAULT_CONTROL_ROOT))
    prepare.add_argument("--shadow-candidate-id", required=True)
    prepare.add_argument("--operator-id", required=True)
    prepare.add_argument("--planned-start-utc", required=True)
    prepare.add_argument("--authorization-created-at", default="")
    prepare.add_argument("--ttl-sec", type=int, default=300)

    status = sub.add_parser("status")
    status.add_argument("--plan-path", required=True)
    status.add_argument("--control-root", default=str(DEFAULT_CONTROL_ROOT))
    status.add_argument("--include-recovery", action="store_true")

    stop = sub.add_parser("stop")
    stop.add_argument("--plan-path", required=True)
    stop.add_argument("--control-root", default=str(DEFAULT_CONTROL_ROOT))
    stop.add_argument("--requested-at", default="")

    start = sub.add_parser("start")
    start.add_argument("--plan-path", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "prepare":
        result = prepare_runtime_horizon_collection(
            source_root=args.source_root,
            destination_root=args.destination_root,
            control_root=args.control_root,
            shadow_candidate_id=args.shadow_candidate_id,
            operator_id=args.operator_id,
            planned_start_utc=args.planned_start_utc,
            authorization_created_at=args.authorization_created_at or utc_now_text(),
            ttl_sec=args.ttl_sec,
        )
    elif args.command == "status":
        result = status_runtime_horizon_collection(
            plan_path=args.plan_path,
            control_root=args.control_root,
            include_recovery=args.include_recovery,
        )
    elif args.command == "stop":
        result = stop_runtime_horizon_collection(
            plan_path=args.plan_path,
            control_root=args.control_root,
            requested_at=args.requested_at or None,
        )
    else:
        raise PermissionError("runtime_horizon_collection_start_not_implemented_fail_closed")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
