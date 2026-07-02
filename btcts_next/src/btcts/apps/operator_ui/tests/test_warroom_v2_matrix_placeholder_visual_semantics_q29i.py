# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_matrix_placeholder_visual_semantics_q29i.py
# desc: PS-Q29I guards for WarRoom v2 matrix placeholder visual semantics.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.card_visual_semantics import (  # noqa: E402
    WARROOM_V2_CARD_VISUAL_SEMANTICS_VERSION,
    build_warroom_v2_card_visual_semantics_packet,
    warroom_v2_card_visual_semantics_css,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.prediction_cards import (  # noqa: E402
    build_warroom_v2_prediction_matrix_renderer_packet,
    warroom_v2_prediction_matrix_html,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
PREDICTION_CARDS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/prediction_cards.py"
SEMANTICS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/card_visual_semantics.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29I_WARROOM_V2_MATRIX_PLACEHOLDER_VISUAL_SEMANTICS_2026-07-02.md"


def _prediction_models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T07:00:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "prediction_cards"]


def test_q29i_visual_semantics_packet_separates_meanings() -> None:
    packet = build_warroom_v2_card_visual_semantics_packet({"background_tone": "caution", "evidence_quality": "CONFLICTED", "freshness_badge": "STALE"})
    assert packet["visual_semantics_version"] == WARROOM_V2_CARD_VISUAL_SEMANTICS_VERSION
    assert packet["background_class"] == "wv2-tone-caution"
    assert packet["evidence_class"] == "wv2-evidence-conflicted"
    assert packet["freshness_class"] == "wv2-freshness-stale"
    assert packet["background_color_never_encodes_freshness"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["freshness_not_encoded_by_border"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False


def test_q29i_css_contains_q27e_palette_and_evidence_classes() -> None:
    css = warroom_v2_card_visual_semantics_css()
    assert ".wv2-tone-good" in css and "#DCFAE6" in css
    assert ".wv2-tone-caution" in css and "#FEF7C3" in css
    assert ".wv2-tone-danger" in css and "#FEE4E2" in css
    assert ".wv2-tone-unknown" in css and "#F2F4F7" in css
    assert ".wv2-evidence-strong" in css
    assert ".wv2-evidence-conflicted" in css and "dashed" in css
    assert ".wv2-evidence-missing" in css and "dotted" in css


def test_q29i_prediction_renderer_reads_semantics_from_payload() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "build_warroom_v2_card_visual_semantics_packet(payload)" in text
    assert "warroom_v2_card_visual_semantics_css()" in text
    assert "wv2-tone-unknown wv2-evidence-missing" not in text
    packet = build_warroom_v2_prediction_matrix_renderer_packet(_prediction_models())
    assert packet["visual_semantics_from_payload"] is True
    assert packet["background_color_never_encodes_freshness"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["freshness_not_encoded_by_border"] is True
    assert packet["border_meaning"] == "evidence_quality"


def test_q29i_matrix_html_keeps_placeholder_unknown_missing_classes() -> None:
    html = warroom_v2_prediction_matrix_html(_prediction_models())
    assert "wv2-tone-unknown" in html
    assert "wv2-evidence-missing" in html
    assert "wv2-freshness-missing" in html
    assert "NO_DATA" in html


def test_q29i_no_route_legacy_or_runtime_ownership_changed() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in app_text
    assert "card_visual_semantics" not in legacy_text
    assert "prediction_warroom.v2" not in legacy_text
    for path in (PREDICTION_CARDS, SEMANTICS):
        text = path.read_text(encoding="utf-8-sig")
        for token in ("build_market_regime_source_snapshot(", "classify_market_regime_feature_bundle(", "send_to_broker(", "append_ledger(", "write_runtime_artifact("):
            assert token not in text


def test_q29i_doc_records_visual_semantics_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "background_color_never_encodes_freshness=true" in text
    assert "freshness_not_encoded_by_border=true" in text
    assert "freshness_encoded_by_badge_only=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
