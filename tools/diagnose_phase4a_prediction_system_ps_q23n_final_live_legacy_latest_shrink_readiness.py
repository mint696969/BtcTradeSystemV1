# path: ./tools/diagnose_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness.py
# desc: PS-Q23N final no-write readiness before executing gated live legacy latest shrink.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write import run_legacy_latest_shrink_readiness_no_write  # noqa: E402
from tools.run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once import (  # noqa: E402
    DEFAULT_HOT_ROOT,
    LEGACY_LATEST_RELATIVE_PATH,
    REQUIRED_CONFIRMATION,
    RUNNER_VERSION as Q23M_RUNNER_VERSION,
    run_legacy_latest_shrink_once,
)

DIAGNOSTIC_VERSION = "prediction_warroom.final_live_legacy_latest_shrink_readiness.ps_q23n.v1"
LATEST_MANIFEST_RELATIVE_PATH = "prediction/latest_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _actual_shrink_command(*, hot_root: Path) -> str:
    return (
        "python .\\tools\\run_phase4a_prediction_system_ps_q23m_gated_legacy_latest_shrink_once.py "
        f"--hot-root {str(hot_root)!r} "
        "--operator-acknowledged "
        "--execute-legacy-latest-shrink-once "
        f"--confirmation {REQUIRED_CONFIRMATION}"
    )


def _rollback_command_template(*, hot_root: Path) -> str:
    target = hot_root / LEGACY_LATEST_RELATIVE_PATH
    return (
        "$backupRelativePath = '<backup_relative_path_from_ps_q23m_actual_result>'\n"
        f"Copy-Item -LiteralPath (Join-Path {str(hot_root)!r} $backupRelativePath) -Destination {str(target)!r} -Force"
    )


def _false_safety_flags() -> dict[str, Any]:
    return {
        "read_only_diagnostic": True,
        "actual_legacy_latest_shrink_executed": False,
        "legacy_latest_shrink_executed": False,
        "latest_prediction_artifact_written": False,
        "status_artifact_written": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "runtime_artifact_write_enabled": False,
        "backup_written": False,
        "scheduler_action_changed": False,
        "scheduler_enabled_by_this_tool": False,
        "trigger_added": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def run_final_live_legacy_latest_shrink_readiness(*, hot_root: Path = DEFAULT_HOT_ROOT) -> dict[str, Any]:
    repo_status = _git_status_short()
    q23k = run_legacy_latest_shrink_readiness_no_write()
    default_probe = run_legacy_latest_shrink_once(
        hot_root=hot_root,
        operator_acknowledged=False,
        execute_legacy_latest_shrink_once=False,
        confirmation="",
    )
    candidate = _as_mapping(default_probe.get("candidate"))
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status:
        blockers.append("repo_clean_required_before_actual_legacy_latest_shrink")
    if q23k.get("legacy_latest_shrink_ready") is not True:
        blockers.append("q23k_legacy_latest_shrink_ready_required")
    expected_gate_blockers = {
        "exact_legacy_latest_shrink_confirmation_required",
        "execute_legacy_latest_shrink_once_flag_required",
        "operator_acknowledgement_required",
    }
    actual_gate_blockers = set(str(item) for item in _as_list(default_probe.get("blocked_reasons")))
    if actual_gate_blockers != expected_gate_blockers and not repo_status:
        blockers.append("q23m_default_probe_must_be_blocked_only_by_gate")
    if default_probe.get("success") is not False:
        blockers.append("q23m_default_probe_must_not_succeed")
    if default_probe.get("legacy_latest_shrink_executed") is not False:
        blockers.append("q23m_default_probe_must_not_execute_shrink")
    if candidate.get("source_artifact_mode") != "distributed":
        blockers.append("candidate_source_artifact_mode_must_be_distributed")
    if candidate.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("candidate_source_artifact_relative_path_must_be_latest_manifest")
    if candidate.get("distributed_reader_ready") is not True:
        blockers.append("candidate_distributed_reader_ready_required")
    if candidate.get("distributed_stale_vs_legacy") is True:
        blockers.append("candidate_distributed_must_not_be_stale_vs_legacy")
    if candidate.get("candidate_read_model_ok") is not True:
        blockers.append("candidate_compact_read_model_ok_required")
    if int(candidate.get("compact_record_count") or 0) <= 0:
        blockers.append("candidate_compact_record_count_required")
    if int(candidate.get("original_record_count") or 0) <= int(candidate.get("compact_record_count") or 0):
        blockers.append("candidate_compact_record_count_must_be_smaller_than_original")
    if int(candidate.get("estimated_after_size_bytes") or 0) <= 0:
        blockers.append("candidate_compact_size_required")
    if int(candidate.get("estimated_before_size_bytes") or 0) <= int(candidate.get("estimated_after_size_bytes") or 0):
        blockers.append("candidate_compact_size_must_be_smaller_than_before")
    if default_probe.get("backup_relative_path_candidate"):
        backup_candidate_ready = True
    else:
        backup_candidate_ready = False
        blockers.append("backup_relative_path_candidate_required")
    if q23k.get("warnings"):
        warnings.extend(str(item) for item in _as_list(q23k.get("warnings")))

    final_ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "hot_root": str(hot_root),
        "q23m_runner_version": Q23M_RUNNER_VERSION,
        "required_confirmation": REQUIRED_CONFIRMATION,
        "actual_shrink_final_ready": final_ready,
        "final_readiness_state": "actual_legacy_latest_shrink_ready_for_explicit_operator_token" if final_ready else "actual_legacy_latest_shrink_blocked_no_write",
        "blockers": blockers,
        "warnings": warnings,
        "repo_status_short": repo_status,
        "q23k": {
            "legacy_latest_shrink_ready": q23k.get("legacy_latest_shrink_ready"),
            "legacy_latest_shrink_state": q23k.get("legacy_latest_shrink_state"),
            "blockers": q23k.get("blockers"),
            "q23i": q23k.get("q23i"),
            "q23j_display_default": q23k.get("q23j_display_default"),
        },
        "q23m_default_probe": {
            "success": default_probe.get("success"),
            "execution_state": default_probe.get("execution_state"),
            "blocked_reasons": sorted(actual_gate_blockers),
            "legacy_latest_shrink_executed": default_probe.get("legacy_latest_shrink_executed"),
            "latest_prediction_artifact_written": default_probe.get("latest_prediction_artifact_written"),
            "backup_written": default_probe.get("backup_written"),
            "runtime_artifact_write_enabled": default_probe.get("runtime_artifact_write_enabled"),
        },
        "candidate": {
            "source_artifact_mode": candidate.get("source_artifact_mode"),
            "source_artifact_relative_path": candidate.get("source_artifact_relative_path"),
            "distributed_reader_ready": candidate.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": candidate.get("distributed_stale_vs_legacy"),
            "candidate_read_model_ok": candidate.get("candidate_read_model_ok"),
            "candidate_read_model_record_count": candidate.get("candidate_read_model_record_count"),
            "candidate_read_model_blockers": candidate.get("candidate_read_model_blockers"),
            "original_record_count": candidate.get("original_record_count"),
            "compact_record_count": candidate.get("compact_record_count"),
            "estimated_before_size_bytes": candidate.get("estimated_before_size_bytes"),
            "estimated_after_size_bytes": candidate.get("estimated_after_size_bytes"),
            "estimated_shrink_bytes": candidate.get("estimated_shrink_bytes"),
            "estimated_after_to_before_ratio": candidate.get("estimated_after_to_before_ratio"),
            "legacy_latest_meta_before": candidate.get("legacy_latest_meta_before"),
        },
        "backup_relative_path_candidate": default_probe.get("backup_relative_path_candidate"),
        "backup_candidate_ready": backup_candidate_ready,
        "actual_shrink_command_candidate": _actual_shrink_command(hot_root=hot_root),
        "rollback_command_template": _rollback_command_template(hot_root=hot_root),
        "post_actual_validation_commands": [
            "python .\\tools\\diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model.py",
            "python .\\tools\\diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write.py",
            "git status --short",
        ],
        **_false_safety_flags(),
    }


def main() -> int:
    result = run_final_live_legacy_latest_shrink_readiness()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
