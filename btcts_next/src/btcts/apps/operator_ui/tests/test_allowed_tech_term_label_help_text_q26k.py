# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_allowed_tech_term_label_help_text_q26k.py
# desc: PS-Q26K tests for allowed technical term helper wording. Display-only; preserves legacy searchable compatibility.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION,
    build_warroom_q26k_allowed_tech_term_label_help_text_packet,
    warroom_allowed_tech_term_help_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
    build_latest_prediction_summary_widget_q18aj_q26k_allowed_tech_term_help_text_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
    build_latest_prediction_summary_widget_q18ak_q26k_allowed_tech_term_help_text_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
)


def test_q26k_warroom_allowed_term_glossary_and_safety() -> None:
    rows = warroom_allowed_tech_term_help_rows()
    joined = json.dumps(rows, ensure_ascii=False)
    for term in ("heartbeat", "fallback", "runtime binding", "AutoTrade", "broker", "artifact", "fragment"):
        assert term in joined
    assert "画面更新確認時刻" in joined
    assert "安全側の表示理由" in joined
    assert "実データprops接続" in joined
    assert "枠内だけの表示更新" in joined
    packet = build_warroom_q26k_allowed_tech_term_label_help_text_packet()
    assert packet["help_text_version"] == WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION
    assert packet["allowed_technical_terms_preserved"] is True
    assert packet["japanese_helper_wording_added"] is True
    assert packet["legacy_searchable_compatibility_preserved"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q26k_q18aj_q18ak_helper_wording_and_legacy_searchable_preserved() -> None:
    q18aj = build_latest_prediction_summary_widget_q18aj_q26k_allowed_tech_term_help_text_packet()
    q18ak = build_latest_prediction_summary_widget_q18ak_q26k_allowed_tech_term_help_text_packet()
    assert q18aj["help_text_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_ALLOWED_TECH_TERM_HELP_TEXT_VERSION
    assert q18ak["help_text_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_ALLOWED_TECH_TERM_HELP_TEXT_VERSION
    joined = q18aj["sample_rows_joined"] + "\n" + q18ak["sample_rows_joined"]
    assert "heartbeat（画面更新確認時刻）" in joined
    assert "予測artifact（生成済み予測ファイル）" in joined
    assert "fallbackは安全側の表示理由" in joined
    assert "fragment path（枠内更新経路）" in joined
    assert "AutoTrade triggerとbroker/private API（売買接続）" in joined
    assert "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" in latest_prediction_summary_widget_q18aj_searchable_plain_text({})
    assert "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" in latest_prediction_summary_widget_q18ak_searchable_plain_text({})
    assert q18aj["trade_guidance_added"] is False
    assert q18ak["trade_guidance_added"] is False
    assert q18aj["would_send_to_broker"] is False
    assert q18ak["would_send_to_broker"] is False
