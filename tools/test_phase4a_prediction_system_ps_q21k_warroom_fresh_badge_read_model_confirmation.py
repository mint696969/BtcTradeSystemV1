# path: ./tools/test_phase4a_prediction_system_ps_q21k_warroom_fresh_badge_read_model_confirmation.py
# desc: Focused guard for PS-Q21K WarRoom fresh badge read-model confirmation.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.verify_phase4a_prediction_system_ps_q21k_warroom_fresh_badge_read_model import (  # noqa: E402
    VERIFY_VERSION,
    build_warroom_fresh_badge_read_model_confirmation,
)

TOOL = REPO_ROOT / "tools/verify_phase4a_prediction_system_ps_q21k_warroom_fresh_badge_read_model.py"
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q21K_WARROOM_FRESH_BADGE_READ_MODEL_CONFIRMATION_2026-06-26.md"

REQUIRED_MARKERS = (
    "ps_q21k_warroom_fresh_badge_read_model_confirmation=true",
    "read_model_to_display_panel_packet_verified=true",
    "data_freshness_badge_non_stale_visible=true",
    "refresh_live_badge_active_visible=true",
    "panel_and_data_freshness_separated=true",
    "read_only_verification_only=true",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enablement_allowed=false",
    "producer_enablement_allowed=false",
    "warroom_ui_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _read_model() -> dict:
    return {
        "ok": True,
        "read_model_version": "prediction_warroom.latest_prediction_warroom_read_model.ps_q19c.v1",
        "generated_at": "2026-06-26T05:05:57Z",
        "age_sec": 120,
        "freshness_state": "fresh",
        "record_count": 110,
        "warning_reason_codes": [],
        "blocker_reason_codes": [],
    }


def _display_packet() -> dict:
    return {
        "ok": True,
        "display_panel_state": "warroom_realtime_prediction_display_only_panel_mounted",
        "generated_at": "2026-06-26T05:05:57Z",
        "age_sec": 120,
        "freshness_state": "fresh",
        "prediction_row_count": 24,
        "panel_failures": [],
        "prediction_artifact_write_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def _data_badge(*, state: str = "fresh") -> dict:
    return {
        "data_freshness_badge_version": "prediction_warroom.warroom_prediction_data_freshness_badge.ps_q21e.v1",
        "data_freshness_badge_state": "prediction_data_fresh" if state == "fresh" else "prediction_data_delayed",
        "data_freshness_badge_fresh": state == "fresh",
        "data_freshness_badge_delayed": state == "delayed",
        "data_freshness_badge_attention": False,
        "data_freshness_badge_message": "🟢 予測データ fresh | age=120s | rows=24 | generated_at=2026-06-26T05:05:57Z",
        "data_freshness_badge_generated_at": "2026-06-26T05:05:57Z",
        "data_freshness_badge_age_sec": "120",
        "data_freshness_badge_prediction_row_count": "24",
    }


def _live_badge() -> dict:
    return {
        "refresh_live_badge_version": "prediction_warroom.warroom_prediction_refresh_live_badge.ps_q21d.v1",
        "refresh_live_badge_active": True,
        "refresh_live_badge_state": "prediction_refresh_live",
        "refresh_live_badge_message": "🟢 予測パネル更新中",
    }


def test_spec_declares_warroom_badge_confirmation_and_safety_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_fresh_read_model_display_panel_badge_confirmation_passes() -> None:
    result = build_warroom_fresh_badge_read_model_confirmation(
        read_model=_read_model(),
        display_packet=_display_packet(),
        data_badge_packet=_data_badge(state="fresh"),
        live_badge_packet=_live_badge(),
    )
    assert result["ok"] is True
    assert result["verify_version"] == VERIFY_VERSION
    assert result["verification_state"] == "warroom_read_model_badge_fresh_or_delayed_non_stale"
    assert result["read_model_ok"] is True
    assert result["display_panel_ok"] is True
    assert result["data_freshness_badge_fresh"] is True
    assert result["data_freshness_badge_non_stale"] is True
    assert result["refresh_live_badge_active"] is True
    assert result["warroom_expected_operator_visible_state"] == "fresh"
    assert result["safety_preserved"] is True
    assert result["read_only_verification_only"] is True
    assert result["prediction_artifact_write_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["would_send_to_broker"] is False


def test_delayed_badge_is_non_stale_but_operator_state_delayed() -> None:
    result = build_warroom_fresh_badge_read_model_confirmation(
        read_model={**_read_model(), "freshness_state": "delayed", "age_sec": 1200},
        display_packet={**_display_packet(), "freshness_state": "delayed", "age_sec": 1200},
        data_badge_packet=_data_badge(state="delayed"),
        live_badge_packet=_live_badge(),
    )
    assert result["ok"] is True
    assert result["data_freshness_badge_delayed"] is True
    assert result["data_freshness_badge_non_stale"] is True
    assert result["warroom_expected_operator_visible_state"] == "delayed"


def test_attention_badge_or_disabled_safety_fails_closed() -> None:
    panel = _display_packet()
    panel["would_send_to_broker"] = True
    result = build_warroom_fresh_badge_read_model_confirmation(
        read_model=_read_model(),
        display_packet=panel,
        data_badge_packet={**_data_badge(state="fresh"), "data_freshness_badge_fresh": False, "data_freshness_badge_attention": True},
        live_badge_packet=_live_badge(),
    )
    assert result["ok"] is False
    assert result["verification_state"] == "warroom_read_model_badge_attention"
    assert result["data_freshness_badge_non_stale"] is False
    assert result["safety_preserved"] is False


def test_tool_is_read_only_and_uses_display_panel_packet() -> None:
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
    )
    for token in forbidden:
        assert token not in text, token
    assert "load_latest_prediction_warroom_read_model" in text
    assert "build_latest_prediction_warroom_display_panel_packet" in text
    assert "latest_prediction_warroom_data_freshness_badge_packet" in text
    assert "latest_prediction_warroom_refresh_live_badge_packet" in text
    assert "print(json.dumps" in text


if __name__ == "__main__":
    test_spec_declares_warroom_badge_confirmation_and_safety_boundaries()
    test_fresh_read_model_display_panel_badge_confirmation_passes()
    test_delayed_badge_is_non_stale_but_operator_state_delayed()
    test_attention_badge_or_disabled_safety_fails_closed()
    test_tool_is_read_only_and_uses_display_panel_packet()
    print('{"ok": true}')
