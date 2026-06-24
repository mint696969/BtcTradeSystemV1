# path: ./tools/test_phase4a_prediction_system_ps_q18au_observation_cleanup_quick_status.py
# desc: Unit tests for PS-Q18AU WarRoom observation cleanup quick status.

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    _prediction_warroom_latest_prediction_observation_cleanup_summary_packet,
    _prediction_warroom_latest_prediction_observation_cleanup_summary_rows,
)


def test_ps_q18au_quick_status_packet_is_display_only_and_searchable() -> None:
    q18aj = {
        "auto_refresh_enabled": True,
        "fragment_refresh_enabled": True,
        "broad_page_reload_disabled": True,
        "refresh_heartbeat_utc": "2026-06-24T07:05:55Z",
    }
    q18ak = {
        "freshness_state": "stale",
        "safe_fallback_reason_codes": ["source_generated_at_stale"],
        "observed_now_utc": "2026-06-24T07:05:55Z",
        "source_age_sec": 150000,
    }
    packet = _prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet=q18aj,
        q18ak_packet=q18ak,
    )
    text = packet["operator_plain_text"]
    assert packet["ok"] is True
    assert packet["observation_cleanup_state"] == "operator_quick_status_visible_display_only"
    assert packet["latest_prediction_observation_status"] == "ready_for_operator_review"
    assert packet["q18aq_manual_resmoke_result"] == "pass"
    assert packet["q18aj_auto_refresh_enabled"] is True
    assert packet["q18aj_broad_page_reload_disabled"] is True
    assert packet["q18ak_freshness_state"] == "stale"
    assert packet["q18ak_safe_fallback_reason_codes"] == ["source_generated_at_stale"]
    assert "PS_Q18AU_OBSERVATION_QUICK_STATUS" in text
    assert "freshness_state=stale" in text
    assert "safe_fallback_reason_codes=source_generated_at_stale" in text
    assert "refresh_heartbeat_utc=2026-06-24T07:05:55Z" in text
    assert "implementation_gate=blocked_not_ready_to_enable" in text
    assert packet["real_rendering_enabled"] is False
    assert packet["component_runtime_binding_allowed"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_ps_q18au_quick_status_rows_keep_operator_read_order() -> None:
    packet = _prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet={"auto_refresh_enabled": True, "refresh_heartbeat_utc": "hb"},
        q18ak_packet={"freshness_state": "stale", "safe_fallback_reason_codes": ["source_generated_at_stale"]},
    )
    rows = _prediction_warroom_latest_prediction_observation_cleanup_summary_rows(packet)
    assert [row["observation_item"] for row in rows[:3]] == ["read_order", "manual_resmoke", "auto_refresh"]
    assert any(row["observation_item"] == "freshness_state" and row["value"] == "stale" for row in rows)
    assert any(row["observation_item"] == "autotrade_broker" and row["value"] == "false" for row in rows)
