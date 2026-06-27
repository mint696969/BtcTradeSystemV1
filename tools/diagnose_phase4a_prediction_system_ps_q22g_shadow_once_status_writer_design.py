# path: ./tools/diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py
# desc: PS-Q22G read-only design diagnostic for wiring future shadow-once to Q22E status writer. No writes, no scheduler/trigger/broker/AutoTrade.

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review import (  # noqa: E402
    _load,
    _meta,
    LATEST,
    STATUS,
    build_status_only_visibility_review,
)
from tools.verify_phase4a_prediction_system_ps_q21x_producer_loop_shadow_preflight_no_enablement import run_shadow_preflight  # noqa: E402

Q22A = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22a_producer_loop_shadow_once.py"
Q22E = REPO_ROOT / "tools/run_phase4a_prediction_system_ps_q22e_success_preserving_status_write_once.py"
DESIGN_VERSION = "prediction_warroom.shadow_once_status_writer_design.ps_q22g.v1"
SHADOW_ONCE_TOKEN = "ENABLE_DISABLED_PRODUCER_LOOP_SHADOW_ONCE_WITH_ROLLBACK_PLAN"
Q22E_STATUS_WRITE_TOKEN = "WRITE_D_HOT_SUCCESS_PRESERVING_PRODUCER_STATUS_ONCE"


def _git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False).stdout.strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_shadow_once_status_writer_design(*, q22a_source: str, q22e_source: str, q22f_packet: Mapping[str, Any]) -> dict[str, Any]:
    q22f = _as_mapping(q22f_packet)
    blockers: list[str] = []
    q22a_uses_q16b_scaffold = bool(
        "build_prediction_warroom_non_ui_scheduled_producer_runner" in q22a_source
        and "allow_status_artifact_write=True" in q22a_source
        and "execute_status_artifact_write=True" in q22a_source
        and "producer_loop_shadow_once_executed_status_write_only" in q22a_source
    )
    q22e_writer_available = bool(
        "run_success_preserving_status_write_once" in q22e_source
        and Q22E_STATUS_WRITE_TOKEN in q22e_source
        and "manual_refresh_exported_status_written" in q22e_source
        and "latest_prediction_artifact_written" in q22e_source
        and "status_artifact_written" in q22e_source
    )
    q22f_ready = bool(q22f.get("review_state") == "q22e_status_only_visibility_review_ready_no_write" and q22f.get("review_blockers") == [])
    q22f_observed = bool(q22f.get("status_only_write_observed") is True and q22f.get("preserves_q21x_success_marker") is True)
    if not q22a_uses_q16b_scaffold:
        blockers.append("current_q22a_scaffold_status_writer_not_detected")
    if not q22e_writer_available:
        blockers.append("q22e_success_preserving_status_writer_not_detected")
    if not q22f_ready:
        blockers.append("q22f_visibility_review_ready_required")
    if not q22f_observed:
        blockers.append("q22f_status_only_observation_required")
    design_ready = not blockers
    return {
        "ok": True,
        "design_version": DESIGN_VERSION,
        "read_only_no_write": True,
        "repo_status_short": _git_status(),
        "design_state": "shadow_once_status_writer_replacement_design_ready_no_write" if design_ready else "shadow_once_status_writer_replacement_design_blocked",
        "design_blockers": blockers,
        "current_q22a_uses_q16b_scaffold_status_writer": q22a_uses_q16b_scaffold,
        "q22e_success_preserving_status_writer_available": q22e_writer_available,
        "q22f_visibility_review_ready": q22f_ready,
        "q22f_status_only_write_observed": q22f.get("status_only_write_observed") is True,
        "q22f_preserves_q21x_success_marker": q22f.get("preserves_q21x_success_marker") is True,
        "q22f_q21x_shadow_ready": q22f.get("q21x_shadow_preflight_ready_for_one_shot") is True,
        "outer_shadow_once_token_to_keep": SHADOW_ONCE_TOKEN,
        "inner_status_writer_token_for_future_adapter": Q22E_STATUS_WRITE_TOKEN,
        "future_adapter_sequence_not_executed": [
            "run_q21x_shadow_preflight_no_write",
            "require_q22f_status_only_visibility_review_ready",
            "require_operator_ack_and_outer_shadow_once_token",
            "call_q22e_success_preserving_status_writer_once_instead_of_q16b_scaffold",
            "verify_latest_prediction_artifact_unchanged",
            "verify_status_artifact_written_once",
            "verify_q21x_remains_ready",
            "keep_scheduler_trigger_broker_autotrade_false",
        ],
        "future_contract": {
            "status_artifact_write_explicit_only": True,
            "latest_prediction_artifact_written": False,
            "producer_state_must_remain_q21x_success_marker": "manual_refresh_exported_status_written",
            "preserve_last_success_generated_at": True,
            "preserve_last_prediction_run_id": True,
            "verify_q21x_after_write": True,
            "single_run_only": True,
            "non_recurring": True,
            "requires_no_lock_overlap": True,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "would_send_to_broker": False,
        },
        "next_recommended_action": "implement_shadow_once_adapter_using_q22e_status_writer_exact_token_no_scheduler_enablement" if design_ready else "restore_visibility_or_inspect_q22a_q22e_sources_before_adapter",
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
    q22f = build_status_only_visibility_review(
        latest_meta=_meta(LATEST),
        status_meta=_meta(STATUS),
        status_payload=_load(STATUS),
        q21x_packet=run_shadow_preflight(),
    )
    report = build_shadow_once_status_writer_design(q22a_source=_read(Q22A), q22e_source=_read(Q22E), q22f_packet=q22f)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
