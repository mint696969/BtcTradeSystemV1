# path: ./btcts_next/src/btcts/prediction/market_regime/tools/runtime_horizon_dhot_write_once.py
# desc: MR-F9.19J interactive fresh-package one-shot writer boundary. No scheduler, latest pointer, UI, or execution activation.

from __future__ import annotations

import argparse
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from btcts.prediction.market_regime.runtime_horizon_persistence import (
    persist_runtime_horizon_plan_once,
)
from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    build_runtime_horizon_write_approval_token,
)
from btcts.prediction.market_regime.runtime_horizon_write_authorization import (
    build_runtime_horizon_write_authorization_package,
    validate_runtime_horizon_write_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    build_runtime_horizon_write_readiness_report,
)
from btcts.prediction.market_regime.tools.shadow_runtime_preflight_once import (
    build_shadow_runtime_preflight_once,
)

MR_F9_DHOT_WRITE_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.runtime_horizon_dhot_write_once.mr_f9_19j.v1"
)
AuthorizationReader = Callable[[str, Mapping[str, Any]], str]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_authorization_reader(expected_text: str, package: Mapping[str, Any]) -> str:
    print("\n===== ONE-SHOT WRITE AUTHORIZATION CONTEXT =====")
    print(f"destination_root={package['destination_root']}")
    print(f"run_id={package['run_id']}")
    print(f"prediction_origin={package['prediction_origin']}")
    print(f"expires_at={package['expires_at']}")
    print(f"authorization_package_sha256={package['authorization_package_sha256']}")
    print("===== EXACT AUTHORIZATION TEXT =====")
    print(expected_text)
    print("===== END AUTHORIZATION TEXT =====\n")
    print(
        "Paste the exact authorization text above within the package TTL. "
        "Any mismatch aborts before the writer."
    )
    return input("authorization> ")


def execute_runtime_horizon_dhot_write_once(
    *,
    source_root: str | Path,
    destination_root: str | Path,
    shadow_candidate_id: str,
    operator_id: str,
    enabled: bool = False,
    once: bool = False,
    authorization_reader: AuthorizationReader = _default_authorization_reader,
    now_provider: Callable[[], str] = utc_now_text,
    ttl_sec: int = 300,
) -> Mapping[str, Any]:
    if any(type(value) is not bool for value in (enabled, once)):
        raise ValueError("mr_f9_dhot_write_once_flags_invalid")
    if enabled is not True:
        raise PermissionError("mr_f9_dhot_write_once_enabled_ack_required")
    if once is not True:
        raise PermissionError("mr_f9_dhot_write_once_once_ack_required")
    if not callable(authorization_reader) or not callable(now_provider):
        raise ValueError("mr_f9_dhot_write_once_callback_invalid")

    operator = str(operator_id).strip()
    if not operator:
        raise ValueError("mr_f9_dhot_write_once_operator_id_required")

    source = Path(source_root).resolve()
    destination = Path(destination_root).resolve()
    generated_at = now_provider()
    preflight = build_shadow_runtime_preflight_once(
        hot_root=source,
        generated_at=generated_at,
        shadow_candidate_id=shadow_candidate_id,
    )
    if preflight.get("runtime_horizon_persistence_plan_built") is not True:
        raise ValueError("mr_f9_dhot_write_once_plan_not_built")
    for key in (
        "runtime_horizon_writer_registered",
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "producer_loop_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if preflight.get(key) is not False:
            raise ValueError(f"mr_f9_dhot_write_once_preflight_safety_invalid:{key}")

    plan = preflight.get("runtime_horizon_persistence_plan")
    if not isinstance(plan, Mapping):
        raise ValueError("mr_f9_dhot_write_once_plan_invalid")

    readiness_preflight = dict(preflight)
    readiness_preflight["hot_root"] = str(destination)
    readiness = build_runtime_horizon_write_readiness_report(
        preflight=readiness_preflight,
        destination_root=destination,
        operator_id=operator,
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    if readiness.get("ready") is not True or tuple(readiness.get("blockers") or ()):
        raise PermissionError("mr_f9_dhot_write_once_readiness_not_ready")

    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id=operator,
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    package_created_at = now_provider()
    package = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=package_created_at,
        ttl_sec=ttl_sec,
        expected_dhot_root=destination,
    )
    validate_runtime_horizon_write_authorization_package(
        package=package,
        token=token,
        readiness=readiness,
        plan=plan,
        now=package_created_at,
        expected_dhot_root=destination,
    )

    expected_text = str(package["expected_authorization_text"])
    supplied_text = authorization_reader(expected_text, package)
    if not isinstance(supplied_text, str) or not hmac.compare_digest(supplied_text, expected_text):
        raise PermissionError("mr_f9_dhot_write_once_authorization_text_mismatch")

    writer_now = now_provider()
    validate_runtime_horizon_write_authorization_package(
        package=package,
        token=token,
        readiness=readiness,
        plan=plan,
        now=writer_now,
        expected_dhot_root=destination,
    )

    write_result = persist_runtime_horizon_plan_once(
        destination,
        plan=plan,
        enabled=True,
        once=True,
    )
    for key in (
        "latest_pointer_created",
        "writer_registered",
        "producer_loop_enabled",
        "scheduler_enabled",
        "websocket_opened",
        "order_submission_allowed",
    ):
        if write_result.get(key) is not False:
            raise ValueError(f"mr_f9_dhot_write_once_writer_result_safety_invalid:{key}")

    expected_order = tuple(str(item) for item in package["write_order"])
    written_paths = tuple(str(item) for item in (write_result.get("written_paths") or ()))
    duplicate_paths = tuple(str(item) for item in (write_result.get("duplicate_paths") or ()))
    written_set = set(written_paths)
    duplicate_set = set(duplicate_paths)
    if len(written_set) != len(written_paths) or len(duplicate_set) != len(duplicate_paths):
        raise ValueError("mr_f9_dhot_write_once_writer_result_path_duplicate")
    if written_set.intersection(duplicate_set):
        raise ValueError("mr_f9_dhot_write_once_writer_result_path_overlap")
    if written_set.union(duplicate_set) != set(expected_order):
        raise ValueError("mr_f9_dhot_write_once_writer_result_path_set_mismatch")
    expected_written_paths = tuple(path for path in expected_order if path in written_set)
    expected_duplicate_paths = tuple(path for path in expected_order if path in duplicate_set)
    if written_paths != expected_written_paths:
        raise ValueError("mr_f9_dhot_write_once_writer_result_written_path_order_mismatch")
    if duplicate_paths != expected_duplicate_paths:
        raise ValueError("mr_f9_dhot_write_once_writer_result_duplicate_path_order_mismatch")
    if int(write_result.get("written_count") or 0) != len(written_paths):
        raise ValueError("mr_f9_dhot_write_once_writer_result_written_count_mismatch")
    if int(write_result.get("duplicate_count") or 0) != len(duplicate_paths):
        raise ValueError("mr_f9_dhot_write_once_writer_result_duplicate_count_mismatch")
    if len(written_paths) + len(duplicate_paths) != 9:
        raise ValueError("mr_f9_dhot_write_once_writer_result_count_invalid")
    if str(write_result.get("manifest_relpath") or "") != expected_order[-1]:
        raise ValueError("mr_f9_dhot_write_once_manifest_receipt_path_mismatch")
    if written_paths and write_result.get("manifest_written_last") is not True:
        raise ValueError("mr_f9_dhot_write_once_manifest_not_written_last")

    return {
        "schema_version": MR_F9_DHOT_WRITE_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f9_runtime_horizon_dhot_write_once_result",
        "source_root": str(source),
        "destination_root": str(destination),
        "generated_at": preflight["generated_at"],
        "shadow_candidate_id": preflight["shadow_candidate_id"],
        "operator_id": operator,
        "run_id": package["run_id"],
        "prediction_origin": package["prediction_origin"],
        "approval_token_sha256": package["approval_token_sha256"],
        "authorization_package_sha256": package["authorization_package_sha256"],
        "authorization_text_sha256": package["expected_authorization_text_sha256"],
        "authorization_validated": True,
        "human_authorized": True,
        "writer_invoked": True,
        "write_result": dict(write_result),
        "writes_dhot": destination == source,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build one fresh MR-F9 authorization package, require exact interactive "
            "human authorization, and invoke the guarded writer once."
        )
    )
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--destination-root", required=True)
    parser.add_argument("--shadow-candidate-id", required=True)
    parser.add_argument("--operator-id", required=True)
    parser.add_argument("--ttl-sec", type=int, default=300)
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument("--once", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.enabled or not args.once:
        parser.error("--enabled and --once are required; scheduler and registration remain unavailable")
    result = execute_runtime_horizon_dhot_write_once(
        source_root=args.source_root,
        destination_root=args.destination_root,
        shadow_candidate_id=args.shadow_candidate_id,
        operator_id=args.operator_id,
        enabled=args.enabled,
        once=args.once,
        ttl_sec=args.ttl_sec,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
