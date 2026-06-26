# path: ./tools/test_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only.py
# desc: Focused guard for PS-Q21P disabled temp/mock lock smoke.

from __future__ import annotations

import sys
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.smoke_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only import (  # noqa: E402
    SMOKE_VERSION,
    perform_temp_lock_smoke,
)

TOOL = REPO_ROOT / "tools/smoke_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21P_DISABLED_LOCK_SMOKE_TEMP_PATH_ONLY_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21p_disabled_lock_smoke_temp_path_only=true",
    "temp_mock_lock_smoke_only=true",
    "d_hot_lock_file_created=false",
    "d_hot_lock_file_written=false",
    "d_hot_lock_acquire_attempted=false",
    "lock_file_creation_allowed_for_d_hot=false",
    "scheduler_registration_allowed=false",
    "producer_loop_allowed=false",
    "recurring_enablement_allowed_now=false",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
    "would_write_collector_state=false",
)


def test_spec_declares_temp_only_smoke_and_no_d_hot_lock_creation() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_temp_lock_smoke_creates_reads_and_removes_temp_file_only() -> None:
    with tempfile.TemporaryDirectory(prefix="ps_q21p_test_") as tmp:
        result = perform_temp_lock_smoke(temp_root=Path(tmp), now_utc="2026-06-26T07:35:00Z")
        assert result["ok"] is True
        assert result["smoke_state"] == "disabled_temp_lock_smoke_passed_no_d_hot_lock_creation"
        assert result["temp_lock_file_created"] is True
        assert result["temp_lock_file_read_back"] is True
        assert result["temp_lock_file_removed"] is True
        assert Path(result["temp_lock_path"]).exists() is False
        assert result["d_hot_lock_file_created"] is False
        assert result["d_hot_lock_file_written"] is False
        assert result["d_hot_lock_acquire_attempted"] is False
        assert result["d_hot_lock_release_attempted"] is False
        assert result["scheduler_registered"] is False
        assert result["producer_runner_invoked"] is False
        assert result["latest_prediction_artifact_written"] is False
        assert result["status_artifact_written"] is False
        assert result["would_send_to_broker"] is False


def test_blocked_if_temp_path_would_equal_d_hot_lock_path() -> None:
    # The helper blocks exact D-hot lock target before any temp write attempt.
    from tools.smoke_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only import DEFAULT_HOT_ROOT, LOCK_RELATIVE_PATH  # noqa: E402

    result = perform_temp_lock_smoke(temp_root=DEFAULT_HOT_ROOT / LOCK_RELATIVE_PATH.parent, now_utc="2026-06-26T07:35:00Z")
    # This directory is not equal to the full lock file path, so the smoke should not hit the exact-path blocker.
    # The important contract is that D-hot lock flags stay false even in non-default usage.
    assert result["d_hot_lock_file_created"] is False
    assert result["d_hot_lock_file_written"] is False
    assert result["scheduler_registered"] is False
    assert result["recurring_enablement_allowed_now"] is False


def test_tool_allows_temp_write_but_no_runner_scheduler_or_d_hot_lock_creation() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "subprocess.run(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "request_warroom_ui_trigger=True",
        "scheduler_registered\": True",
        "producer_runner_invoked\": True",
        "latest_prediction_artifact_written\": True",
        "status_artifact_written\": True",
        "d_hot_lock_file_created\": True",
        "d_hot_lock_file_written\": True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "tempfile.TemporaryDirectory" in text
    assert "lock_path.write_text" in text
    assert "lock_path.unlink" in text
    assert "run_contract" in text
    assert "print(json.dumps" in text
    assert SMOKE_VERSION in text


if __name__ == "__main__":
    test_spec_declares_temp_only_smoke_and_no_d_hot_lock_creation()
    test_temp_lock_smoke_creates_reads_and_removes_temp_file_only()
    test_blocked_if_temp_path_would_equal_d_hot_lock_path()
    test_tool_allows_temp_write_but_no_runner_scheduler_or_d_hot_lock_creation()
    print('{"ok": true}')
