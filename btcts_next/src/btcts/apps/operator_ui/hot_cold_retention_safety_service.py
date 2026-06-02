# path: ./btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py
# desc: Build lightweight Hot/Cold retention safety payloads for Operator UI Health snapshots.

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HOT_RETENTION_DAYS = 10
MIN_DELETE_AGE_HOURS = 240.0
PREVIOUS_PLAN_HASH = "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755"
PREVIOUS_CONFIRM_TOKEN = "DELETE_D_HOT_BATCH_d70a1c26dc5195a2"
PRE_EXEC_VERIFY_OUTPUT_REL = Path(
    "tmp/work/operator_operational_readiness/outputs/"
    "hot_cold_first_batch_pre_execute_verification_v1_20260602T064046.474691Z.json"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def _read_pre_execute_verification() -> dict[str, Any] | None:
    return _read_json_file(_repo_root() / PRE_EXEC_VERIFY_OUTPUT_REL)


def _read_referenced_small_batch_output(summary: Mapping[str, Any]) -> dict[str, Any] | None:
    raw_path = str(summary.get("small_batch_output_path") or "").strip()
    if not raw_path:
        return None
    path = Path(raw_path)
    if not path.is_absolute():
        path = _repo_root() / path
    return _read_json_file(path)


def _selected_age_summary(small_batch: Mapping[str, Any] | None) -> dict[str, Any]:
    rows = (_as_mapping(small_batch).get("preflight_rows") or []) if small_batch else []
    ages: list[float] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        raw_age = row.get("age_hours_now")
        try:
            ages.append(float(raw_age))
        except (TypeError, ValueError):
            continue
    if not ages:
        return {
            "selected_age_known": False,
            "min_selected_age_hours": None,
            "newest_selected_age_hours": None,
            "blocked_under_10day_policy": True,
        }
    min_age = min(ages)
    return {
        "selected_age_known": True,
        "min_selected_age_hours": min_age,
        "newest_selected_age_hours": min_age,
        "blocked_under_10day_policy": min_age < MIN_DELETE_AGE_HOURS,
    }


def build_hot_cold_retention_safety_payload(
    *,
    pre_execute_summary: Mapping[str, Any] | None = None,
    small_batch_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a display-only safety payload from already-created summaries. Does not scan hot/cold roots."""
    pre = _as_mapping(pre_execute_summary)
    small = _as_mapping(small_batch_summary)
    counts = _as_mapping(pre.get("counts"))
    age_summary = _selected_age_summary(small)

    plan_hash = str(pre.get("plan_hash") or PREVIOUS_PLAN_HASH)
    selected_files = int(counts.get("selected_files") or 0)
    selected_gb = float(counts.get("selected_gb") or 0.0)
    deleted_files = int(counts.get("deleted_files") or 0)
    dry_run = pre.get("dry_run") is True
    execute = pre.get("execute") is True
    plan_hash_ok = plan_hash == PREVIOUS_PLAN_HASH
    previous_plan_present = bool(pre)
    blocked_under_10day = bool(age_summary.get("blocked_under_10day_policy", True))

    status_key = "blocked"
    severity_key = "warning"
    delete_readiness_key = "blocked_rebuild_10day_plan"
    copy_verification_key = "unknown"

    if previous_plan_present and dry_run and not execute and plan_hash_ok and deleted_files == 0:
        copy_verification_key = "preflight_exact_size_verified"
        if blocked_under_10day:
            delete_readiness_key = "blocked_previous_plan_younger_than_10_days"
        else:
            delete_readiness_key = "requires_new_10day_plan_review"
    elif not previous_plan_present:
        status_key = "unknown"
        severity_key = "unknown"
        delete_readiness_key = "no_recent_preflight_summary"

    summary_lines = [
        "hot retention policy is 10 days",
        "delete candidates must be older than 240 hours",
        "previous 48h-style execute path is abandoned under 10-day policy",
        "Health render path does not scan D/E and does not copy/delete",
        "simulation/training must use a duplicate-safe logical dataset view",
    ]
    if previous_plan_present:
        summary_lines.append(f"previous_plan_hash={plan_hash}")
        summary_lines.append(f"previous_selected_files={selected_files}")
        summary_lines.append(f"previous_selected_gb={selected_gb:.6f}")
        if age_summary.get("selected_age_known"):
            summary_lines.append(
                f"previous_newest_selected_age_hours={float(age_summary['newest_selected_age_hours']):.3f}"
            )

    return {
        "title": "Hot/Cold retention safety",
        "status_key": status_key,
        "severity_key": severity_key,
        "hot_retention_days": HOT_RETENTION_DAYS,
        "min_delete_age_hours": MIN_DELETE_AGE_HOURS,
        "copy_verification_key": copy_verification_key,
        "delete_readiness_key": delete_readiness_key,
        "counts": {
            "candidate_files": 0,
            "candidate_gb": 0.0,
            "newest_candidate_age_hours": None,
            "previous_selected_files": selected_files,
            "previous_selected_gb": selected_gb,
            "previous_deleted_files": deleted_files,
            "previous_newest_selected_age_hours": age_summary.get("newest_selected_age_hours"),
        },
        "plan": {
            "plan_hash": plan_hash,
            "plan_path": str(pre.get("plan_path") or ""),
            "previous_plan_hash": PREVIOUS_PLAN_HASH,
            "previous_confirm_token": PREVIOUS_CONFIRM_TOKEN,
            "previous_plan_abandoned_for_execute": True,
        },
        "policy": {
            "hot_retention_days": HOT_RETENTION_DAYS,
            "min_delete_age_hours": MIN_DELETE_AGE_HOURS,
            "delete_candidates_must_be_older_than_10_days": True,
            "completed_files_only": True,
            "no_double_count_hot_cold_for_simulation_training": True,
        },
        "operator_next_step": "Rebuild dry-run plan with min_age_hours=240 before any delete.",
        "summary_lines": summary_lines,
        "boundary": {
            "read_only_display": True,
            "already_built_payload_only": True,
            "not_filesystem_scan": True,
            "not_copy_executor": True,
            "not_delete_executor": True,
            "not_runtime_state_writer": True,
            "not_collector_state_mutation": True,
            "not_market_engine_input": True,
            "not_broker_or_order_automation": True,
            "not_inference_or_training": True,
        },
    }


def load_hot_cold_retention_safety_payload() -> dict[str, Any]:
    """Load a bounded precomputed preflight summary and build a display payload. Does not scan D/E."""
    pre = _read_pre_execute_verification()
    small = _read_referenced_small_batch_output(pre or {}) if pre else None
    return build_hot_cold_retention_safety_payload(
        pre_execute_summary=pre,
        small_batch_summary=small,
    )
