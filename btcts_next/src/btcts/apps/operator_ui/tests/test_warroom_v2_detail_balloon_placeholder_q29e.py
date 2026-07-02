# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_detail_balloon_placeholder_q29e.py
# desc: PS-Q29E guards for WarRoom v2 card detail-balloon placeholder renderer.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2 import (  # noqa: E402
    WARROOM_V2_CARD_DETAIL_BALLOON_RENDERER_VERSION,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.card_detail_balloon import (  # noqa: E402
    build_warroom_v2_card_detail_balloon_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
PREDICTION_CARDS = RENDERER_DIR / "prediction_cards.py"
PLACEHOLDERS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/placeholder_read_models.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29E_WARROOM_V2_DETAIL_BALLOON_PLACEHOLDER_2026-07-02.md"


def _first_prediction_card() -> dict:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T05:40:00Z")
    for model in packet["read_models"]:
        if model["payload"].get("zone") == "prediction_cards":
            return model
    raise AssertionError("prediction card placeholder not found")


def test_q29e_detail_balloon_packet_exposes_placeholder_sections() -> None:
    model = _first_prediction_card()
    packet = build_warroom_v2_card_detail_balloon_packet(model)
    assert packet["detail_balloon_version"] == WARROOM_V2_CARD_DETAIL_BALLOON_RENDERER_VERSION
    assert packet["placeholder_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["display_only"] is True
    labels = [section["label"] for section in packet["sections"]]
    assert labels == ["理由", "参照", "警告", "無効化条件"]
    assert all(section["lines"] for section in packet["sections"])


def test_q29e_prediction_cards_delegate_detail_rendering() -> None:
    text = PREDICTION_CARDS.read_text(encoding="utf-8-sig")
    assert "render_warroom_v2_card_detail_balloon" in text
    assert 'with st.expander("詳細"' not in text
    assert "placeholder detail balloon" not in text


def test_q29e_placeholder_read_models_include_detail_fields() -> None:
    model = _first_prediction_card()
    payload = model["payload"]
    assert payload["detail_lines"]
    assert payload["source_lines"]
    assert payload["warning_lines"]
    assert payload["invalidation_lines"]
    assert payload["placeholder_only"] is True
    assert payload["runtime_connected"] is False
    assert payload["push_connected"] is False


def test_q29e_renderer_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
    assert len(PLACEHOLDERS.read_text(encoding="utf-8-sig").splitlines()) <= 140


def test_q29e_legacy_warroom_is_not_changed_to_own_detail_balloon() -> None:
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert "card_detail_balloon" not in legacy_text
    assert "WARROOM_V2_CARD_DETAIL_BALLOON" not in legacy_text


def test_q29e_doc_records_detail_balloon_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "not_connecting_dhot=true" in text
    assert "not_invoking_classifier=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
    assert "not_changing_legacy_warroom=true" in text
