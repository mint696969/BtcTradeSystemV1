# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_status_density_reduction_q27t.py
# desc: PS-Q27T guard. Reduces WarRoom market-regime status/caption density while preserving compact UI and card specs.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import build_warroom_market_regime_card_preview_enablement_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_market_regime_card_panel import build_warroom_market_regime_card_preview_switch_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27T_WARROOM_MARKET_REGIME_STATUS_DENSITY_REDUCTION_2026-07-02.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def test_q27t_doc_records_density_reduction_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q27t_warroom_market_regime_status_density_reduction=true" in text
    assert "redundant_status_copy_removed=true" in text
    assert "preview_checkbox_label_compacted=true" in text
    assert "panel_caption_removed=true" in text
    assert "card_body_three_lines_unchanged=true" in text
    assert "would_send_to_broker=false" in text


def test_q27t_warroom_page_uses_short_checkbox_and_no_default_explainer_caption() -> None:
    text = PAGE.read_text(encoding="utf-8-sig")
    assert '"地合い preview"' in text
    assert "地合いカード preview を明示有効化" not in text
    assert "preview はデフォルトOFF" not in text
    assert "ON時のみ D-hot" not in text
    assert "warroom_market_regime_card_preview_enabled_q27p" in text
    assert "value=True" in text
    assert "preview_enabled=True" not in text


def test_q27t_panel_removes_card_level_caption_copy() -> None:
    text = PANEL.read_text(encoding="utf-8-sig")
    assert "st.caption(\"地合いカード: sample\")" not in text
    assert "st.caption(\"地合いカード: preview / read-only\")" not in text
    assert "地合いカード: sample" not in text
    assert "地合いカード: preview / read-only" not in text
    assert "st.markdown(market_regime_cards_html(packet[\"cards\"]), unsafe_allow_html=True)" in text


def test_q27t_preview_gate_packet_default_on_but_explicit_off_keeps_sample_fallback() -> None:
    default_on = build_warroom_market_regime_card_preview_enablement_packet(generated_at="2026-07-01T19:45:03Z")
    assert default_on["preview_enabled_effective"] is True
    assert default_on["render_kwargs"]["preview_enabled"] is True
    assert default_on["warroom_page_preview_default_on"] is True
    explicit_off = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=False,
        operator_confirmed_read_only=False,
        generated_at="2026-07-01T19:45:03Z",
    )
    assert explicit_off["preview_enabled_effective"] is False
    assert explicit_off["disabled_reason"] == "preview_checkbox_off"
    assert explicit_off["render_kwargs"]["preview_enabled"] is False
    assert explicit_off["render_kwargs"]["hot_root"] is None
    on = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=True,
        operator_confirmed_read_only=True,
        hot_root="D:/tmp/nonexistent-but-explicit",
        generated_at="2026-07-01T19:45:03Z",
    )
    assert on["preview_enabled_effective"] is True
    assert on["render_kwargs"]["preview_enabled"] is True


def test_q27t_card_specs_and_safety_flags_unchanged() -> None:
    packet = build_warroom_market_regime_card_preview_switch_packet(preview_enabled=False, hot_root=None, generated_at="2026-07-01T19:45:03Z")
    assert packet["sample_data_only"] is True
    assert packet["card_width_px"] == 208
    assert packet["cards_do_not_shrink"] is True
    assert packet["horizontal_scroll_required"] is True
    assert packet["freshness_encoded_by_badge_only"] is True
    assert packet["border_meaning"] == "evidence_quality"
    assert packet["detail_disclosure_mode"] == "card_overlay"
    assert all(len(card["card_lines"]) == 3 for card in packet["cards"])
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert packet[key] is False
