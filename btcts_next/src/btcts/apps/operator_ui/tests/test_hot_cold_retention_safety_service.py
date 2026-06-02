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
    payload = build_hot_cold_retention_safety_payload(
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
        small_batch_summary={
            "preflight_rows": [
                {"age_hours_now": 149.0},
                {"age_hours_now": 150.0},
            ]
        },
    )
    assert payload["title"] == "Hot/Cold retention safety"
    assert payload["status_key"] == "blocked"
    assert payload["severity_key"] == "warning"
    assert payload["hot_retention_days"] == 10
    assert payload["min_delete_age_hours"] == MIN_DELETE_AGE_HOURS
    assert payload["delete_readiness_key"] == "blocked_previous_plan_younger_than_10_days"
    assert payload["copy_verification_key"] == "preflight_exact_size_verified"
    assert payload["counts"]["candidate_files"] == 0
    assert payload["counts"]["previous_selected_files"] == 4
    assert payload["counts"]["previous_deleted_files"] == 0
    assert payload["plan"]["previous_plan_abandoned_for_execute"] is True
    assert payload["policy"]["delete_candidates_must_be_older_than_10_days"] is True
    assert payload["policy"]["no_double_count_hot_cold_for_simulation_training"] is True
    assert payload["boundary"]["not_filesystem_scan"] is True
    assert payload["boundary"]["not_copy_executor"] is True
    assert payload["boundary"]["not_delete_executor"] is True
    assert payload["operator_next_step"] == "Rebuild dry-run plan with min_age_hours=240 before any delete."

    unknown = build_hot_cold_retention_safety_payload()
    assert unknown["status_key"] == "unknown"
    assert unknown["delete_readiness_key"] == "no_recent_preflight_summary"
    assert unknown["counts"]["candidate_files"] == 0

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
