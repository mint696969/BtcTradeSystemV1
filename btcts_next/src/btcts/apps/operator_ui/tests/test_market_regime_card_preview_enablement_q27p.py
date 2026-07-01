# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_preview_enablement_q27p.py
# desc: PS-Q27P tests for WarRoom market-regime preview enablement decision. Default off; explicit checkbox/read-only root required.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_PREVIEW_ENABLEMENT_VERSION,
    WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
    build_warroom_market_regime_card_preview_enablement_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def test_q27p_enablement_default_is_off_and_sample_only() -> None:
    packet = build_warroom_market_regime_card_preview_enablement_packet(generated_at="2026-07-01T18:20:03Z")
    assert packet["enablement_version"] == WARROOM_MARKET_REGIME_CARD_PREVIEW_ENABLEMENT_VERSION
    assert packet["preview_enabled_requested"] is False
    assert packet["operator_confirmed_read_only"] is False
    assert packet["preview_enabled_effective"] is False
    assert packet["disabled_reason"] == "preview_checkbox_off"
    assert packet["render_kwargs"] == {"preview_enabled": False, "hot_root": None, "generated_at": "2026-07-01T18:20:03Z"}
    assert packet["disabled_path_reads_root"] is False
    assert packet["warroom_page_preview_default_on"] is False


def test_q27p_enablement_requires_operator_confirmation() -> None:
    packet = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=True,
        operator_confirmed_read_only=False,
        hot_root=WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
        generated_at="2026-07-01T18:20:03Z",
    )
    assert packet["preview_enabled_requested"] is True
    assert packet["operator_confirmed_read_only"] is False
    assert packet["preview_enabled_effective"] is False
    assert packet["disabled_reason"] == "operator_read_only_confirmation_required"
    assert packet["render_kwargs"]["preview_enabled"] is False
    assert packet["render_kwargs"]["hot_root"] is None


def test_q27p_enablement_on_uses_explicit_hot_root_read_only() -> None:
    packet = build_warroom_market_regime_card_preview_enablement_packet(
        preview_enabled=True,
        operator_confirmed_read_only=True,
        hot_root=WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
        generated_at="2026-07-01T18:20:03Z",
    )
    assert packet["preview_enabled_effective"] is True
    assert packet["disabled_reason"] == ""
    assert packet["explicit_source_root_required"] is True
    assert packet["explicit_source_root_read_allowed"] is True
    assert packet["render_kwargs"] == {
        "preview_enabled": True,
        "hot_root": WARROOM_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT_HINT,
        "generated_at": "2026-07-01T18:20:03Z",
    }
    assert packet["runtime_artifact_write_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q27p_warroom_page_has_checkbox_default_off_and_no_auto_preview() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "WARROOM_MARKET_REGIME_CARD_PREVIEW_ENABLEMENT_VERSION" in page_text
    assert "warroom_market_regime_card_preview_enabled_q27p" in page_text
    assert "value=False" in page_text
    assert "render_kwargs" in page_text
    assert "render_warroom_market_regime_card_shell(" in page_text
    assert '**market_regime_preview_enablement_packet["render_kwargs"]' in page_text
    assert "preview_enabled=True" not in page_text
    assert "send_to_broker(" not in page_text
    assert "append_ledger(" not in page_text


def test_q27p_panel_remains_display_only_receiver() -> None:
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "build_warroom_market_regime_card_preview_switch_packet" in panel_text
    assert "default_sample_only_when_disabled" in panel_text
    assert "preview_enabled: bool = False" in panel_text
    for token in ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_status_artifact("):
        assert token not in panel_text
