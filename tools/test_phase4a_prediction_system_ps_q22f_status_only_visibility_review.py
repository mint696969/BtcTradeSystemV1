# path: ./tools/test_phase4a_prediction_system_ps_q22f_status_only_visibility_review.py
# desc: Focused guard for PS-Q22F status-only visibility review.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review import Q22E_STATUS_VERSION, build_status_only_visibility_review  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q22F_STATUS_ONLY_VISIBILITY_REVIEW_2026-06-27.md"
TOOL = REPO_ROOT / "tools/diagnose_phase4a_prediction_system_ps_q22f_status_only_visibility_review.py"


def _status(**overrides: object) -> dict:
    data = {
        "producer_version": Q22E_STATUS_VERSION,
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_success_generated_at": "2026-06-27T06:06:37Z",
        "last_prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-27T06:06:37Z",
        "last_target_file_size_bytes": 5425754,
        "blockers": [],
    }
    data.update(overrides)
    return data


def _q21x(**overrides: object) -> dict:
    data = {"shadow_preflight_ready_for_one_shot": True, "shadow_preflight_blockers": [], "latest_prediction_non_stale": True, "latest_status_success_observed": True, "disabled_boundary_preserved": True}
    data.update(overrides)
    return data


def test_spec_declares_q22e_visibility_review_contract() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in (
        "ps_q22f_status_only_visibility_review=true",
        "read_only_no_write=true",
        "q22e_status_only_write_observed=true",
        "q22e_status_preserved_q21x_success_marker=true",
        "latest_prediction_artifact_written=false",
        "recurring_enablement_allowed_now=false",
    ):
        assert marker in text, marker


def test_review_ready_when_q22e_status_and_q21x_ready() -> None:
    result = build_status_only_visibility_review(
        latest_meta={"exists": True, "mtime_utc": "2026-06-27T06:06:37Z", "size_bytes": 5425754},
        status_meta={"exists": True, "mtime_utc": "2026-06-27T06:08:52Z", "size_bytes": 2310},
        status_payload=_status(),
        q21x_packet=_q21x(),
    )
    assert result["review_state"] == "q22e_status_only_visibility_review_ready_no_write"
    assert result["review_blockers"] == []
    assert result["status_only_write_observed"] is True
    assert result["preserves_q21x_success_marker"] is True
    assert result["q21x_shadow_preflight_ready_for_one_shot"] is True
    assert result["safety"]["status_artifact_written"] is False


def test_review_blocks_on_scaffold_status() -> None:
    result = build_status_only_visibility_review(
        latest_meta={"exists": True, "mtime_utc": "2026-06-27T06:06:37Z"},
        status_meta={"exists": True, "mtime_utc": "2026-06-27T06:08:52Z"},
        status_payload=_status(producer_version="prediction_warroom_non_ui_scheduled_producer_runner.ps_q16b.v1", producer_state="producer_disabled_status_ready", last_success_generated_at=None, last_prediction_run_id=None),
        q21x_packet=_q21x(shadow_preflight_ready_for_one_shot=False, latest_status_success_observed=False),
    )
    assert result["review_state"] == "q22e_status_only_visibility_review_blocked"
    assert "q22e_status_version_required" in result["review_blockers"]
    assert "q21x_success_marker_producer_state_required" in result["review_blockers"]
    assert "last_success_generated_at_required" in result["review_blockers"]
    assert "last_prediction_run_id_required" in result["review_blockers"]


def test_tool_is_read_only() -> None:
    text = TOOL.read_text(encoding="utf-8")
    for token in ("write_text(", "open(\"w", "_write_json_atomic", "Enable-ScheduledTask", "New-ScheduledTaskTrigger", "Start-ScheduledTask", "send_order(", "place_order("):
        assert token not in text, token


if __name__ == "__main__":
    test_spec_declares_q22e_visibility_review_contract()
    test_review_ready_when_q22e_status_and_q21x_ready()
    test_review_blocks_on_scaffold_status()
    test_tool_is_read_only()
    print(json.dumps({"ok": True}))
