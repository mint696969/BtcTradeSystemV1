# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_render_status.py
# desc: Guard RT WarRoom reports the actual original market-regime renderer packet used for display.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
CARDS_VIEW = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py"


class FakeExpander:
    def __enter__(self) -> "FakeExpander":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class FakeStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.tables: list[list[dict[str, object]]] = []

    def caption(self, value: object) -> None:
        self.captions.append(str(value))

    def expander(self, *_args: object, **_kwargs: object) -> FakeExpander:
        return FakeExpander()

    def dataframe(self, rows: list[dict[str, object]], **_kwargs: object) -> None:
        self.tables.append(rows)


def test_original_market_regime_shell_returns_renderer_packet_for_rt_status() -> None:
    panel = PANEL.read_text(encoding="utf-8-sig")
    cards_view = CARDS_VIEW.read_text(encoding="utf-8-sig")

    assert "def render_warroom_market_regime_card_shell" in panel
    assert ") -> dict[str, Any]:" in panel
    assert "return dict(packet)" in panel

    assert "market_regime_packet = render_warroom_market_regime_card_shell" in cards_view
    assert "_render_market_regime_render_status" in cards_view
    assert "market_regime_preview_cards_used" in cards_view
    assert "market_regime_first_card_label" in cards_view


def test_market_regime_render_status_reports_live_preview_card_summary(monkeypatch) -> None:
    shell_calls: list[dict[str, object]] = []

    def fake_shell(**kwargs: object) -> dict[str, object]:
        shell_calls.append(dict(kwargs))
        return {
            "preview_cards_used": True,
            "source_snapshot_ok": True,
            "card_count": 8,
            "preview_disabled_reason": "",
            "cards": [
                {
                    "horizon": "現在",
                    "regime_label": "レンジ",
                    "confidence_percent": 70,
                    "freshness_badge": "LIVE",
                }
            ],
        }

    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards({"generated_at": "2026-07-08T00:00:00Z", "cards": []}, fake_st)

    assert shell_calls == [{"preview_enabled": True, "hot_root": view.RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT, "generated_at": "2026-07-08T00:00:00Z"}]
    assert result["market_regime_renderer_packet_available"] is True
    assert result["market_regime_preview_cards_used"] is True
    assert result["market_regime_source_snapshot_ok"] is True
    assert result["market_regime_card_count"] == 8
    assert result["market_regime_first_card_label"] == "レンジ"
    assert result["market_regime_first_card_confidence"] == 70
    assert result["market_regime_first_card_freshness"] == "LIVE"
    assert any("地合いカード: D-hot preview" in caption for caption in fake_st.captions)
    assert any("first=レンジ/70%/LIVE" in caption for caption in fake_st.captions)


def test_market_regime_render_status_reports_sample_fallback_when_packet_missing() -> None:
    fake_st = FakeStreamlit()
    summary = view._render_market_regime_render_status(None, fake_st)

    assert summary["packet_available"] is False
    assert summary["preview_cards_used"] is False
    assert summary["preview_disabled_reason"] == "renderer_packet_unavailable"
    assert any("地合いカード: sample/fallback" in caption for caption in fake_st.captions)
    assert any("reason=renderer_packet_unavailable" in caption for caption in fake_st.captions)
