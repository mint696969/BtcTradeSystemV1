# path: ./tools/run_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter.py
# desc: PS-Q22H shadow-once adapter using Q22E success-preserving status writer. Default no-write; no latest/scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design import (  # noqa: E402
    Q22E_STATUS_WRITE_TOKEN,
    SHADOW_ONCE_TOKEN,
    build_shadow_once_status_writer_design,
)
from tools.diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review import (  # noqa: E402
    _load,
    _meta,
    LATEST,
    STATUS,
    build_status_only_visibility_review,
)
from tools.run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once import (  # noqa: E402
    run_success_preserving_status_write_once,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

ADAPTER_VERSION = "prediction_warroom.shadow_once_q22e_status_writer_adapter.ps_q22h.v1"
StatusWriterRunner = Callable[..., Mapping[str, Any]]


def _repo_clean() -> bool:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip() == ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _false_boundary() -> dict[str, Any]:
    return {
        "latest_prediction_artifact_written": False,
        "producer_loop_enabled": False,
        "producer_runner_invoked": False,
        "scheduled_loop_enabled": False,
        "scheduler_enabled": False,
        "scheduler_enablement_allowed_now": False,
        "trigger_added": False,
        "trigger_addition_allowed_now": False,
        "recurring_enablement_allowed_now": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
        "would_write_collector_state": False,
    }


def _current_q22g_design(q21x_packet: Mapping[str, Any] | None = None) -> dict[str, Any]:
    q21x = dict(q21x_packet) if q21x_packet is not None else run_shadow_preflight()
    q22f = build_status_only_visibility_review(
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
        status_payload=_load(STATUS),
        q21x_packet=q21x,
    )
    q22a = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py"
    q22e = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py"
    return build_shadow_once_status_writer_design(q22a_source=_read(q22a), q22e_source=_read(q22e), q22f_packet=q22f)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return dict(converted) if isinstance(converted, Mapping) else {}
    return {}


def run_shadow_once_q22e_status_writer_adapter(
    *,
    operator_acknowledged: bool = False,
    execute_shadow_once: bool = False,
    shadow_once_confirmation: str = "",
    status_write_confirmation: str = "",
    q21x_packet: Mapping[str, Any] | None = None,
    q21x_after_packet: Mapping[str, Any] | None = None,
    q22g_design_packet: Mapping[str, Any] | None = None,
    status_writer_runner: StatusWriterRunner | None = None,
    repo_clean: bool | None = None,
) -> dict[str, Any]:
    q21x = dict(q21x_packet) if q21x_packet is not None else run_shadow_preflight()
    q22g = dict(q22g_design_packet) if q22g_design_packet is not None else _current_q22g_design(q21x)
    blockers: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_shadow_once:
        blockers.append("execute_shadow_once_flag_required")
    if shadow_once_confirmation != SHADOW_ONCE_TOKEN:
        blockers.append("exact_shadow_once_confirmation_token_required")
    if status_write_confirmation != Q22E_STATUS_WRITE_TOKEN:
        blockers.append("exact_status_write_confirmation_token_required")
    repo_is_clean = _repo_clean() if repo_clean is None else bool(repo_clean)
    if not repo_is_clean:
        blockers.append("repo_clean_required_before_shadow_once")
    if q21x.get("shadow_preflight_ready_for_one_shot") is not True:
        blockers.append("q21x_shadow_preflight_ready_required")
    if q21x.get("shadow_preflight_blockers") not in ([], None):
        blockers.append("q21x_shadow_preflight_blockers_must_be_empty")
    if q21x.get("latest_prediction_non_stale") is not True:
        blockers.append("latest_prediction_non_stale_required_before_shadow_once")
    if q21x.get("latest_status_success_observed") is not True:
        blockers.append("latest_status_success_required_before_shadow_once")
    if q21x.get("disabled_boundary_preserved") is not True:
        blockers.append("disabled_boundary_preserved_required_before_shadow_once")
    if q22g.get("design_state") != "shadow_once_status_writer_replacement_design_ready_no_write":
        blockers.append("q22g_shadow_once_status_writer_design_ready_required")
    if q22g.get("design_blockers") not in ([], None):
        blockers.append("q22g_design_blockers_must_be_empty")
    if q22g.get("q22e_success_preserving_status_writer_available") is not True:
        blockers.append("q22e_success_preserving_status_writer_available_required")
    if q22g.get("q22f_visibility_review_ready") is not True:
        blockers.append("q22f_visibility_review_ready_required")
    if blockers:
        return {
            "ok": True,
            "adapter_version": ADAPTER_VERSION,
            "adapter_state": "shadow_once_q22e_status_writer_blocked_no_write",
            "success": False,
            "blocked_reasons": blockers,
            "q21x_preflight": q21x,
            "q22g_design": q22g,
            "status_writer_invoked": False,
            "status_artifact_written": False,
            "required_shadow_once_confirmation": SHADOW_ONCE_TOKEN,
            "required_status_write_confirmation": Q22E_STATUS_WRITE_TOKEN,
            "uses_q16b_scaffold_status_writer": False,
            "uses_q22e_success_preserving_status_writer": True,
            **_false_boundary(),
        }
    runner = status_writer_runner or run_success_preserving_status_write_once
    writer_packet = _as_dict(runner(
        operator_acknowledged=True,
        execute_status_write_once=True,
        confirmation=Q22E_STATUS_WRITE_TOKEN,
    ))
    status_written = writer_packet.get("status_artifact_written") is True
    latest_written = writer_packet.get("latest_prediction_artifact_written") is True
    after_q21x = dict(q21x_after_packet) if q21x_after_packet is not None else run_shadow_preflight()
    after_ready = bool(after_q21x.get("shadow_preflight_ready_for_one_shot") is True and after_q21x.get("shadow_preflight_blockers") == [])
    success = bool(status_written and not latest_written and after_ready)
    return {
        "ok": True,
        "adapter_version": ADAPTER_VERSION,
        "adapter_state": "shadow_once_q22e_status_writer_executed_status_write_only" if success else "shadow_once_q22e_status_writer_failed_or_incomplete",
        "success": success,
        "blocked_reasons": [],
        "q21x_preflight": q21x,
        "q21x_after": after_q21x,
        "q22g_design": q22g,
        "status_writer_packet": writer_packet,
        "status_writer_invoked": True,
        "status_artifact_written": status_written,
        "status_artifact_path": str(writer_packet.get("status_artifact_path") or ""),
        "required_shadow_once_confirmation": SHADOW_ONCE_TOKEN,
        "required_status_write_confirmation": Q22E_STATUS_WRITE_TOKEN,
        "uses_q16b_scaffold_status_writer": False,
        "uses_q22e_success_preserving_status_writer": True,
        **_false_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q22H shadow-once adapter using Q22E status writer")
    parser.add_argument("--operator-acknowledged", action="store_true")
    parser.add_argument("--execute-shadow-once", action="store_true")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--status-write-confirmation", default="")
    args = parser.parse_args(argv)
    result = run_shadow_once_q22e_status_writer_adapter(
        operator_acknowledged=args.operator_acknowledged,
        execute_shadow_once=args.execute_shadow_once,
        shadow_once_confirmation=args.confirmation,
        status_write_confirmation=args.status_write_confirmation,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True and (result.get("success") is True or not args.execute_shadow_once) else 1


if __name__ == "__main__":
    raise SystemExit(main())
