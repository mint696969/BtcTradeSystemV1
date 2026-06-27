# path: ./tools/diagnose_phase4a_prediction_system_ps_q22i_shadow_once_path_handoff_review.py
# desc: PS-Q22I read-only review of Q22A scaffold path vs Q22H adapter path. No writes, no scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

from datetime import datetime, timezone
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

Q22A = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py"
Q22H = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22h_shadow_once_q22e_status_writer_adapter.py"
REVIEW_VERSION = "prediction_warroom.shadow_once_path_handoff_review.ps_q22i.v1"
Q22E_STATUS_VERSION = "prediction_warroom.success_preserving_status_write_once.ps_q22e.v1"
SHADOW_TOKEN = "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN"
STATUS_TOKEN = "WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False).stdout.strip()


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _status_only_observed(latest_meta: Mapping[str, Any], status_meta: Mapping[str, Any], status: Mapping[str, Any]) -> bool:
    latest_mtime = str(latest_meta.get("mtime_utc") or "")
    status_mtime = str(status_meta.get("mtime_utc") or "")
    return bool(
        latest_meta.get("exists") is True
        and status_meta.get("exists") is True
        and status_mtime >= latest_mtime
        and status.get("producer_version") == Q22E_STATUS_VERSION
        and status.get("producer_state") == "manual_refresh_exported_status_written"
        and bool(status.get("last_success_generated_at"))
        and bool(status.get("last_prediction_run_id"))
    )


def build_shadow_once_path_handoff_review(*, q22a_source: str, q22h_source: str, latest_meta: Mapping[str, Any], status_meta: Mapping[str, Any], status_payload: Mapping[str, Any], q21x_packet: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(status_payload)
    q21x = _as_mapping(q21x_packet)
    repo_status = _git_status()
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status.strip():
        warnings.append("repo_dirty_q21x_shadow_ready_may_be_false_until_commit")
    q22a_scaffold_path_detected = bool(
        "build_prediction_warroom_non_ui_scheduled_producer_runner" in q22a_source
        and "allow_status_artifact_write=True" in q22a_source
        and "execute_status_artifact_write=True" in q22a_source
        and "producer_loop_shadow_once_executed_status_write_only" in q22a_source
    )
    # Q22H imports the exact tokens from Q22G rather than duplicating literal
    # strings. Accept either the literal token values or the imported constant
    # names as evidence of the two-token gate.
    q22h_shadow_token_gate_detected = SHADOW_TOKEN in q22h_source or "SHADOW_ONCE_TOKEN" in q22h_source
    q22h_status_token_gate_detected = STATUS_TOKEN in q22h_source or "Q22E_STATUS_WRITE_TOKEN" in q22h_source
    q22h_adapter_path_detected = bool(
        "run_shadow_once_q22e_status_writer_adapter" in q22h_source
        and "run_success_preserving_status_write_once" in q22h_source
        and "uses_q16b_scaffold_status_writer" in q22h_source
        and "uses_q22e_success_preserving_status_writer" in q22h_source
        and q22h_shadow_token_gate_detected
        and q22h_status_token_gate_detected
    )
    q22h_avoids_scaffold_call = "build_prediction_warroom_non_ui_scheduled_producer_runner" not in q22h_source
    q22h_exact_execution_observed = _status_only_observed(latest_meta, status_meta, status)
    q21x_ready_when_clean = bool(q21x.get("shadow_preflight_ready_for_one_shot") is True and q21x.get("shadow_preflight_blockers") == [])
    if not q22a_scaffold_path_detected:
        blockers.append("q22a_scaffold_path_not_detected_for_historical_comparison")
    if not q22h_adapter_path_detected:
        blockers.append("q22h_adapter_path_not_detected")
    if not q22h_avoids_scaffold_call:
        blockers.append("q22h_must_not_call_q16b_scaffold_writer")
    if not q22h_exact_execution_observed:
        blockers.append("q22h_exact_status_only_execution_observation_required")
    if not q21x_ready_when_clean and not repo_status.strip():
        blockers.append("q21x_ready_required_when_repo_clean")
    handoff_ready = not blockers
    return {
        "ok": True,
        "review_version": REVIEW_VERSION,
        "read_only_no_write": True,
        "repo_status_short": repo_status,
        "review_state": "shadow_once_path_handoff_review_ready_no_write" if handoff_ready else "shadow_once_path_handoff_review_blocked",
        "review_blockers": blockers,
        "review_warnings": warnings,
        "q22a_scaffold_path_detected": q22a_scaffold_path_detected,
        "q22h_adapter_path_detected": q22h_adapter_path_detected,
        "q22h_shadow_token_gate_detected": q22h_shadow_token_gate_detected,
        "q22h_status_token_gate_detected": q22h_status_token_gate_detected,
        "q22h_avoids_q16b_scaffold_call": q22h_avoids_scaffold_call,
        "q22h_exact_execution_observed": q22h_exact_execution_observed,
        "q22h_should_be_preferred_for_future_shadow_once": handoff_ready,
        "q22a_scaffold_status_path_should_not_be_used_for_future_shadow_once": handoff_ready,
        "outer_shadow_once_token": SHADOW_TOKEN,
        "inner_status_writer_token": STATUS_TOKEN,
        "latest_meta": dict(latest_meta),
        "status_meta": dict(status_meta),
        "status_producer_version": status.get("producer_version"),
        "status_producer_state": status.get("producer_state"),
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_prediction_run_id": status.get("last_prediction_run_id"),
        "q21x_shadow_preflight_ready_for_one_shot": q21x.get("shadow_preflight_ready_for_one_shot") is True,
        "q21x_shadow_preflight_blockers": list(q21x.get("shadow_preflight_blockers") or []),
        "q21x_latest_prediction_non_stale": q21x.get("latest_prediction_non_stale") is True,
        "q21x_latest_status_success_observed": q21x.get("latest_status_success_observed") is True,
        "q21x_disabled_boundary_preserved": q21x.get("disabled_boundary_preserved") is True,
        "handoff_recommendation": {
            "prefer_q22h_adapter_path": handoff_ready,
            "keep_q22a_as_historical_evidence": True,
            "future_cleanup_should_deprecate_or_wrap_q22a": handoff_ready,
            "future_exact_execution_should_require_both_tokens": True,
            "do_not_enable_recurring_scheduler_yet": True,
        },
        "next_recommended_action": "prepare_q22j_deprecation_or_wrapper_design_for_q22a_no_enablement" if handoff_ready else "restore_q22h_observation_or_recheck_sources_before_handoff",
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
    report = build_shadow_once_path_handoff_review(
        q22a_source=_read(Q22A),
        q22h_source=_read(Q22H),
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
        status_payload=_load(STATUS),
        q21x_packet=run_shadow_preflight(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
