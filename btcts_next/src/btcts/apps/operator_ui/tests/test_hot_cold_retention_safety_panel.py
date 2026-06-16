# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_panel.py
# desc: Verify Hot/Cold retention safety panel helpers stay read-only and payload-only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.hot_cold_retention_safety_panel import (  # noqa: E402
    build_hot_cold_retention_safety_caption,
    build_hot_cold_retention_safety_lines,
)


def _payload() -> dict:
    return {
        "title": "Hot/Cold retention safety",
        "status_key": "blocked",
        "severity_key": "warning",
        "hot_retention_days": 10,
        "min_delete_age_hours": 240.0,
        "copy_verification_key": "exact_size_verified",
        "delete_readiness_key": "no_execute_policy_changed",
        "counts": {
            "candidate_files": 0,
            "candidate_gb": 0.0,
            "newest_candidate_age_hours": None,
        },
        "plan": {
            "plan_hash": "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755",
            "plan_path": "tmp/work/operator_operational_readiness/outputs/abandoned_48h_plan.json",
        },
        "summary_lines": [
            "hot retention policy is 10 days",
            "previous 48h-style plan is abandoned for execute",
            "Health evidence panel is not copy/delete safety",
        ],
        "operator_next_step": "Rebuild dry-run plan with min_age_hours=240 before any delete.",
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


def main() -> int:
    caption = build_hot_cold_retention_safety_caption(_payload())
    assert "hot_cold_retention_safety" in caption
    assert "status=blocked" in caption
    assert "severity=warning" in caption
    assert "hot_retention_days=10" in caption
    assert "delete_readiness=no_execute_policy_changed" in caption
    assert "copy_verification=exact_size_verified" in caption
    assert "read_only_display=True" in caption
    assert "already_built_payload_only=True" in caption
    assert "not_filesystem_scan=True" in caption
    assert "not_copy_executor=True" in caption
    assert "not_delete_executor=True" in caption
    assert "not_runtime_state_writer=True" in caption
    assert "not_collector_state_mutation=True" in caption
    assert "not_market_engine_input=True" in caption
    assert "not_broker_or_order_automation=True" in caption
    assert "not_inference_or_training=True" in caption

    lines = build_hot_cold_retention_safety_lines(_payload())
    assert "title=Hot/Cold retention safety" in lines
    assert "status=blocked" in lines
    assert "hot_retention_days=10" in lines
    assert "min_delete_age_hours=240.0" in lines
    assert "candidate_files=0" in lines
    assert "candidate_gb=0.000000" in lines
    assert any(line.startswith("plan_hash=d70a1c26") for line in lines)
    assert "summary=previous 48h-style plan is abandoned for execute" in lines

    empty_caption = build_hot_cold_retention_safety_caption(None)
    assert "status=unknown" in empty_caption
    assert "boundary=unavailable" in empty_caption

    empty_lines = build_hot_cold_retention_safety_lines(None)
    assert "status=unknown" in empty_lines
    assert "candidate_files=0" in empty_lines

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
