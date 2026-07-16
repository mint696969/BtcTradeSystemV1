# path: ./btcts_next/src/btcts/prediction/market_regime/tools/runtime_horizon_write_once.py
# desc: MR-F9.19E explicit once-only CLI boundary composing read-only preflight, persistence plan, and guarded tmp-root writer.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_persistence import (
    persist_runtime_horizon_plan_once,
)
from btcts.prediction.market_regime.tools.shadow_runtime_preflight_once import (
    build_shadow_runtime_preflight_once,
)

MR_F9_RUNTIME_HORIZON_WRITE_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.runtime_horizon_write_once.mr_f9_19e.v1"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]


def classify_output_root(
    output_root: str | Path,
    *,
    repository_root: str | Path = REPOSITORY_ROOT,
) -> str:
    resolved = Path(output_root).resolve()
    repo_tmp = (Path(repository_root).resolve() / "tmp").resolve()
    try:
        resolved.relative_to(repo_tmp)
    except ValueError as exc:
        raise ValueError("mr_f9_runtime_horizon_write_once_output_root_not_repo_tmp") from exc
    return "repo_tmp"


def execute_runtime_horizon_write_once(
    *,
    hot_root: str | Path,
    output_root: str | Path,
    generated_at: str,
    shadow_candidate_id: str,
    enabled: bool = False,
    once: bool = False,
    repository_root: str | Path = REPOSITORY_ROOT,
) -> Mapping[str, Any]:
    if any(type(value) is not bool for value in (enabled, once)):
        raise ValueError("mr_f9_runtime_horizon_write_once_flags_invalid")
    if enabled is not True:
        raise PermissionError("mr_f9_runtime_horizon_write_once_enabled_ack_required")
    if once is not True:
        raise PermissionError("mr_f9_runtime_horizon_write_once_once_ack_required")

    resolved_output_root = Path(output_root).resolve()
    output_kind = classify_output_root(
        resolved_output_root,
        repository_root=repository_root,
    )
    preflight = build_shadow_runtime_preflight_once(
        hot_root=hot_root,
        generated_at=generated_at,
        shadow_candidate_id=shadow_candidate_id,
    )
    if preflight.get("runtime_horizon_persistence_plan_built") is not True:
        raise ValueError("mr_f9_runtime_horizon_write_once_plan_not_built")
    if preflight.get("runtime_horizon_writer_registered") is not False:
        raise ValueError("mr_f9_runtime_horizon_write_once_writer_registration_invalid")
    if preflight.get("writer_invoked") is not False:
        raise ValueError("mr_f9_runtime_horizon_write_once_preflight_writer_state_invalid")
    if preflight.get("writes_dhot") is not False:
        raise ValueError("mr_f9_runtime_horizon_write_once_preflight_dhot_state_invalid")

    plan = preflight.get("runtime_horizon_persistence_plan")
    if not isinstance(plan, Mapping):
        raise ValueError("mr_f9_runtime_horizon_write_once_plan_invalid")
    write_result = persist_runtime_horizon_plan_once(
        resolved_output_root,
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
            raise ValueError(f"mr_f9_runtime_horizon_write_once_writer_result_safety_invalid:{key}")
    return {
        "schema_version": MR_F9_RUNTIME_HORIZON_WRITE_ONCE_TOOL_VERSION,
        "artifact_kind": "mr_f9_runtime_horizon_write_once_result",
        "hot_root": str(Path(hot_root)),
        "output_root": str(resolved_output_root),
        "output_root_kind": output_kind,
        "generated_at": preflight["generated_at"],
        "shadow_candidate_id": preflight["shadow_candidate_id"],
        "runtime_horizon_persistence_plan_built": True,
        "preflight_only_before_explicit_write": True,
        "explicit_enabled_acknowledged": True,
        "explicit_once_acknowledged": True,
        "write_result": dict(write_result),
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Explicitly build one MR-F9 runtime horizon preflight and persist its "
            "8 artifacts plus manifest to a repository tmp root only."
        )
    )
    parser.add_argument("--hot-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--shadow-candidate-id", required=True)
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument("--once", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.enabled or not args.once:
        parser.error("--enabled and --once are required; runtime registration is unavailable")
    result = execute_runtime_horizon_write_once(
        hot_root=args.hot_root,
        output_root=args.output_root,
        generated_at=args.generated_at,
        shadow_candidate_id=args.shadow_candidate_id,
        enabled=args.enabled,
        once=args.once,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
