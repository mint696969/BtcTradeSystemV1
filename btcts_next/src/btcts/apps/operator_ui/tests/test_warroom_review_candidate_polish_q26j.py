# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_review_candidate_polish_q26j.py
# desc: PS-Q26J tests for operator-visible review-candidate polish. Display-only; no execution or trading guidance.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_REVIEW_CANDIDATE_POLISH_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    build_warroom_live_nowcast_q26j_review_candidate_polish_packet,
    build_warroom_live_nowcast_source_importance_packet,
    warroom_live_nowcast_operator_summary_rows,
    warroom_live_nowcast_source_layer_summary_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_REVIEW_CANDIDATE_POLISH_VERSION,
    build_latest_prediction_warroom_q26j_review_candidate_polish_packet,
    latest_prediction_warroom_q26e_telemetry_footer_text,
)


def test_q26j_nowcast_operator_visible_review_candidate_text_polished() -> None:
    packet = build_warroom_live_market_nowcast_packet(sources={}, fragment_enabled=True)
    assert packet["operator_note"] == "現在状態nowcastです。未来予測でも売買指示でもありません。"
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang="ja")
    rows = warroom_live_nowcast_operator_summary_rows(summary)
    layering = build_warroom_live_nowcast_source_importance_packet(packet, summary, lang="ja")
    layer_rows = warroom_live_nowcast_source_layer_summary_rows(layering)
    joined = "\n".join(str(row) for row in [*rows, *layer_rows])
    assert "current-state guidance only" not in joined
    assert "display-only current-state layer" not in joined
    assert "表示専用の現在状態レイヤー" in joined
    assert "現在状態の確認のみ" in joined
    loc = build_warroom_live_nowcast_q26j_review_candidate_polish_packet()
    assert loc["polish_version"] == WARROOM_LIVE_NOWCAST_REVIEW_CANDIDATE_POLISH_VERSION
    assert loc["operator_visible_review_candidates_polished"] is True
    assert loc["read_only"] is True
    assert loc["display_only"] is True
    assert loc["trade_guidance_added"] is False
    assert loc["broker_private_api_allowed"] is False
    assert loc["would_send_to_broker"] is False


def test_q26j_prediction_footer_false_fragments_polished() -> None:
    footer = latest_prediction_warroom_q26e_telemetry_footer_text({"freshness_state": "fresh", "prediction_row_count": 3, "generated_at": "2026-07-01T00:00:00Z"}, lang="en")
    assert "view_artifact_write_allowed=false" not in footer
    assert "autotrade=false" not in footer
    assert "broker=false" not in footer
    assert "view artifact write=none" in footer
    assert "AutoTrade=none" in footer
    assert "broker=none" in footer
    loc = build_latest_prediction_warroom_q26j_review_candidate_polish_packet()
    assert loc["polish_version"] == WARROOM_PREDICTION_REVIEW_CANDIDATE_POLISH_VERSION
    assert loc["telemetry_footer_false_fragments_polished"] is True
    assert loc["read_only"] is True
    assert loc["display_only"] is True
    assert loc["trade_guidance_added"] is False
    assert loc["broker_private_api_allowed"] is False
    assert loc["would_send_to_broker"] is False
