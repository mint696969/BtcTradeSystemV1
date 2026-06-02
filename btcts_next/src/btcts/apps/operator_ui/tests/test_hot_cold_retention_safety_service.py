# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_service.py
# desc: Verify Hot/Cold retention safety service builds display payloads without scan/copy/delete behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.hot_cold_retention_safety_service import (  # noqa: E402
    MIN_DELETE_AGE_HOURS,
    build_hot_cold_retention_safety_payload,
)


def main() -> int:
    ten_day = build_hot_cold_retention_safety_payload(
        ten_day_plan_review_summary={
            "ok": True,
            "min_age_hours": 240.0,
            "plan_hash": "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6",
            "plan_path": "tmp/work/operator_operational_readiness/outputs/explicit_10day_plan.json",
            "candidate_delete_files": 0,
            "candidate_delete_gb": 0.0,
            "review_counts": {"candidate_delete_files": 0, "candidate_delete_gb": 0.0},
            "review_exclusions": {"too_new": {"files": 56, "gb": 126.353368}},
        }
    )
    assert ten_day["title"] == "Hot/Cold retention safety"
    assert ten_day["status_key"] == "safe_no_delete_candidates"
    assert ten_day["severity_key"] == "info"
    assert ten_day["hot_retention_days"] == 10
    assert ten_day["min_delete_age_hours"] == MIN_DELETE_AGE_HOURS
    assert ten_day["delete_readiness_key"] == "no_candidates_older_than_10_days"
    assert ten_day["copy_verification_key"] == "reviewed_10day_dry_run_plan"
    assert ten_day["counts"]["candidate_files"] == 0
    assert ten_day["counts"]["candidate_gb"] == 0.0
    assert ten_day["counts"]["too_new_files"] == 56
    assert ten_day["counts"]["too_new_gb"] == 126.353368
    assert ten_day["plan"]["previous_plan_abandoned_for_execute"] is True
    assert ten_day["policy"]["delete_candidates_must_be_older_than_10_days"] is True
    assert ten_day["policy"]["no_double_count_hot_cold_for_simulation_training"] is True
    assert ten_day["boundary"]["not_filesystem_scan"] is True
    assert ten_day["boundary"]["not_copy_executor"] is True
    assert ten_day["boundary"]["not_delete_executor"] is True
    assert ten_day["operator_next_step"] == "No D-hot files are currently eligible for 10-day retention delete. Keep monitoring."

    legacy = build_hot_cold_retention_safety_payload(
        pre_execute_summary={
            "ok": True,
            "execute": False,
            "dry_run": True,
            "plan_hash": "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755",
            "plan_path": "tmp/work/operator_operational_readiness/outputs/old_48h_plan.json",
            "counts": {
                "selected_files": 4,
                "selected_gb": 7.296484,
                "deleted_files": 0,
            },
        },
        small_batch_summary={"preflight_rows": [{"age_hours_now": 149.0}, {"age_hours_now": 150.0}]},
    )
    assert legacy["status_key"] == "blocked"
    assert legacy["severity_key"] == "warning"
    assert legacy["delete_readiness_key"] == "blocked_previous_plan_younger_than_10_days"
    assert legacy["copy_verification_key"] == "preflight_exact_size_verified"
    assert legacy["counts"]["candidate_files"] == 0
    assert legacy["counts"]["previous_selected_files"] == 4
    assert legacy["counts"]["previous_deleted_files"] == 0

    unknown = build_hot_cold_retention_safety_payload()
    assert unknown["status_key"] == "unknown"
    assert unknown["delete_readiness_key"] == "no_recent_preflight_summary"
    assert unknown["counts"]["candidate_files"] == 0

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
