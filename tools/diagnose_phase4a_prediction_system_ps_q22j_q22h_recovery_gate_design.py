# path: ./tools/diagnose_phase4a_prediction_system_ps_q22j_q22h_recovery_gate_design.py
# desc: PS-Q22J read-only design diagnostic for Q22H recovery gate. No writes, no scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review import _load, _meta, LATEST, STATUS  # noqa: E402
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

Q22F = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review.py"
Q22G = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py"
Q22H = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter.py"
Q22E = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py"
DESIGN_VERSION = "prediction_warroom.q22h_recovery_gate_design.ps_q22j.v1"
Q22E_STATUS_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"
SHADOW_TOKEN = "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN"
STATUS_TOKEN = "WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE"


def _git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False).stdout.strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_q22h_recovery_gate_design(*, q22f_source: str, q22g_source: str, q22h_source: str, q22e_source: str, latest_meta: Mapping[str, Any], status_meta: Mapping[str, Any], status_payload: Mapping[str, Any], q21x_packet: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    repo_status = _git_status()
    blockers: list[str] = []
    current_q22h_requires_q22g_ready = bool(
        "q22g_shadow_once_status_writer_design_ready_required" in q22h_source
        and "q22g_design_blockers_must_be_empty" in q22h_source
        and "q22f_visibility_review_ready_required" in q22h_source
    )
    q22g_requires_q22f_status_only_observation = bool(
        "q22f_status_only_observation_required" in q22g_source
        and "q22f_visibility_review_ready_required" in q22g_source
    )
    q22f_requires_q22e_status_marker = bool(
        "q22e_status_version_required" in q22f_source
        and Q22E_STATUS_VERSION in q22f_source
        and "status_only_write_observed" in q22f_source
    )
    q22e_writer_available = bool(
        "run_success_preserving_status_write_once" in q22e_source
        and STATUS_TOKEN in q22e_source
        and "manual_refresh_exported_status_written" in q22e_source
        and "latest_prediction_artifact_written" in q22e_source
    )
    q21x_ready = bool(q21x.get("shadow_preflight_ready_for_one_shot") is True and q21x.get("shadow_preflight_blockers") == [])
    success_status_available = bool(
        latest_meta.get("exists") is True
        and status_meta.get("exists") is True
        and status.get("producer_state") == "manual_refresh_exported_status_written"
        and bool(status.get("last_success_generated_at"))
        and bool(status.get("last_prediction_run_id"))
        and status.get("producer_enabled") is False
        and status.get("scheduler_enabled") is False
        and status.get("blockers") in ([], None)
    )
    q21zc_refresh_can_remove_q22e_status_marker = bool(success_status_available and status.get("producer_version") != Q22E_STATUS_VERSION)
    status_already_q22e_observed = bool(success_status_available and status.get("producer_version") == Q22E_STATUS_VERSION)
    if not current_q22h_requires_q22g_ready:
        blockers.append("current_q22h_q22g_dependency_not_detected")
    if not q22g_requires_q22f_status_only_observation:
        blockers.append("q22g_q22f_status_observation_dependency_not_detected")
    if not q22f_requires_q22e_status_marker:
        blockers.append("q22f_q22e_status_marker_dependency_not_detected")
    if not q22e_writer_available:
        blockers.append("q22e_success_preserving_status_writer_not_detected")
    if not success_status_available:
        blockers.append("manual_refresh_success_status_required_for_recovery_design")
    design_ready = not blockers
    return {
        "ok": True,
        "design_version": DESIGN_VERSION,
        "read_only_no_write": True,
        "repo_status_short": repo_status,
        "design_state": "q22h_recovery_gate_design_ready_no_write" if design_ready else "q22h_recovery_gate_design_blocked",
        "design_blockers": blockers,
        "current_q22h_requires_q22g_ready": current_q22h_requires_q22g_ready,
        "q22g_requires_q22f_status_only_observation": q22g_requires_q22f_status_only_observation,
        "q22f_requires_q22e_status_marker": q22f_requires_q22e_status_marker,
        "q21zc_refresh_can_remove_q22e_status_marker": q21zc_refresh_can_remove_q22e_status_marker,
        "status_already_q22e_observed": status_already_q22e_observed,
        "q22e_success_preserving_status_writer_available": q22e_writer_available,
        "q21x_shadow_preflight_ready_for_one_shot": q21x_ready,
        "q21x_shadow_preflight_blockers": list(q21x.get("shadow_preflight_blockers") or []),
        "success_status_available_for_recovery_design": success_status_available,
        "status_producer_version": status.get("producer_version"),
        "status_producer_state": status.get("producer_state"),
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_prediction_run_id": status.get("last_prediction_run_id"),
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "future_recovery_gate_not_executed": {
            "name": "q22h_recover_q22e_status_observation_from_success_status",
            "may_bypass_q22g_ready": True,
            "requires_repo_clean": True,
            "requires_q21x_ready": True,
            "requires_manual_refresh_success_status": True,
            "requires_q22e_writer_available": True,
            "requires_outer_shadow_once_token": SHADOW_TOKEN,
            "requires_inner_status_writer_token": STATUS_TOKEN,
            "writes_status_only": True,
            "writes_latest_prediction_artifact": False,
            "verify_q21x_after_write": True,
            "verify_q22i_after_write": True,
        },
        "normal_path_contract": {
            "keep_q22g_ready_required_for_non_recovery_shadow_once": True,
            "do_not_weaken_normal_path": True,
        },
        "next_recommended_action": "implement_q22h_recovery_gate_no_scheduler_no_latest_write" if design_ready else "inspect_cycle_dependencies_before_recovery_gate",
        "safety": {
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "warroom_ui_trigger_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
            "would_write_collector_state": False,
        },
    }


def main() -> int:
    report = build_q22h_recovery_gate_design(
        q22f_source=_read(Q22F),
        q22g_source=_read(Q22G),
        q22h_source=_read(Q22H),
        q22e_source=_read(Q22E),
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
        status_payload=_load(STATUS),
        q21x_packet=run_shadow_preflight(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
