# path: ./tools/test_phase4a_prediction_system_ps_q21j_post_write_freshness_verification.py
# desc: Focused guard for PS-Q21J post-write freshness verification.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21j_post_write_freshness import (  # noqa: E402
    VERIFY_VERSION,
    build_post_write_freshness_verification,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21j_post_write_freshness.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21J_POST_WRITE_FRESHNESS_VERIFICATION_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21j_post_write_freshness_verification=true",
    "latest_prediction_artifact_fresh_visible=true",
    "producer_status_success_visible=true",
    "scheduler_and_producer_disabled_visible=true",
    "warroom_expected_data_freshness_badge_state=fresh",
    "read_only_verification_only=true",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _latest() -> dict:
    return {
        "run_identity": {
            "prediction_run_id": "prediction_system.ps_g_lite.v1:BTC_JPY:bitFlyer:2026-06-26T05:05:57Z",
            "generated_at": "2026-06-26T05:05:57Z",
            "market_uid": "BTC_JPY:bitFlyer",
        },
        "outputs": [{"horizon": 15}, {"horizon": 60}],
    }


def _status() -> dict:
    return {
        "producer_state": "manual_refresh_exported_status_written",
        "last_success_at": "2026-06-26T05:05:57Z",
        "last_success_generated_at": "2026-06-26T05:05:57Z",
        "last_failure_at": None,
        "last_blocker_count": 0,
        "last_warning_count": 1,
        "freshness_max_age_sec": 3600,
        "blockers": [],
        "warnings": ["prediction_result_warnings_present:19"],
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": True,
        "safe_flags": {
            "producer_enabled_false": True,
            "scheduler_enabled_false": True,
            "warroom_ui_trigger_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "would_send_to_broker_false": True,
        },
    }


def _meta(size: int) -> dict:
    return {"exists": True, "size_bytes": size, "mtime_utc": "2026-06-26T05:05:57Z"}


def test_spec_declares_post_write_verification_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_post_write_fresh_verification_passes_with_disabled_scheduler_producer() -> None:
    result = build_post_write_freshness_verification(
        latest_payload=_latest(),
        status_payload=_status(),
        latest_meta=_meta(5255167),
        status_meta=_meta(1958),
        now_utc="2026-06-26T05:06:20Z",
    )
    assert result["ok"] is True
    assert result["verify_version"] == VERIFY_VERSION
    assert result["verification_state"] == "post_write_fresh"
    assert result["generated_at"] == "2026-06-26T05:05:57Z"
    assert result["output_count"] == 2
    assert result["freshness_state"] == "fresh"
    assert result["post_write_status_success"] is True
    assert result["producer_enabled"] is False
    assert result["scheduler_enabled"] is False
    assert result["runtime_artifact_write_enabled"] is True
    assert result["safety_preserved"] is True
    assert result["warroom_expected_data_freshness_badge_state"] == "fresh"
    assert result["read_only_verification_only"] is True
    assert result["runtime_artifact_write_allowed"] is False
    assert result["prediction_artifact_write_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_stale_or_missing_status_fails_closed() -> None:
    status = dict(_status())
    status["scheduler_enabled"] = True
    result = build_post_write_freshness_verification(
        latest_payload=_latest(),
        status_payload=status,
        latest_meta=_meta(5255167),
        status_meta=_meta(1958),
        now_utc="2026-06-26T08:06:20Z",
    )
    assert result["ok"] is False
    assert result["verification_state"] == "post_write_verification_attention"
    assert result["freshness_state"] == "stale_or_unknown"
    assert result["safety_preserved"] is False


def test_tool_is_read_only_and_uses_hot_root_only() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "write_text(",
        "open(\"w",
        "subprocess.run(",
        "execute_export=True",
        "allow_runtime_artifact_write=True",
        "request_scheduler_enable=True",
        "send_order(",
        "place_order(",
        "BTC_TS_DATA_DIR",
    )
    for token in forbidden:
        assert token not in text, token
    assert "BTCTS_HOT_ROOT" in text
    assert "BTC_TS_HOT_ROOT" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_post_write_verification_and_safety_boundaries()
    test_post_write_fresh_verification_passes_with_disabled_scheduler_producer()
    test_stale_or_missing_status_fails_closed()
    test_tool_is_read_only_and_uses_hot_root_only()
    print('{"ok": true}')
