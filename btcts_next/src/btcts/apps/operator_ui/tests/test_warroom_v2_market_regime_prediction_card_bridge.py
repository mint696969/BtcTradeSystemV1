# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_regime_prediction_card_bridge.py
# desc: Guard RT WarRoom prediction cards bridge to the original WarRoom market-regime card shell.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.v2.rt_ui import prediction_cards_view as view  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
CARDS_VIEW = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py"
ORIGINAL_PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


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


def test_bridge_source_uses_original_market_regime_panel_not_v2_placeholder_matrix() -> None:
    source = CARDS_VIEW.read_text(encoding="utf-8-sig")
    original = ORIGINAL_PANEL.read_text(encoding="utf-8-sig")

    assert "warroom_market_regime_card_panel" in source
    assert "render_warroom_market_regime_card_shell" in source
    assert "preview_enabled=True" in source
    assert "hot_root=RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT" in source
    assert "D:/btc_ts_hot" in source
    assert "panels.warroom_v2.prediction_cards" not in source
    assert "warroom_v2_prediction_matrix_html" not in source

    assert "market_regime_cards_html" in original
    assert "mr-card" in original
    assert "mr-badge" in original
    assert "地合いカード詳細" in original


def test_bridge_returns_market_regime_first_and_future_rows_reserved(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_shell(**kwargs: object) -> None:
        calls.append(dict(kwargs))

    monkeypatch.setattr(view, "render_warroom_market_regime_card_shell", fake_shell)
    fake_st = FakeStreamlit()
    result = view.render_rt_prediction_cards(
        {
            "generated_at": "2026-07-08T00:00:00Z",
            "cards": [
                {
                    "title": "Manual review context",
                    "market_state": "ready",
                    "chart_summary": "rows=1",
                    "operator_note": "read only",
                    "stale_guard": "clear",
                }
            ],
        },
        fake_st,
    )

    assert calls == [{"preview_enabled": True, "hot_root": view.RT_MARKET_REGIME_CARD_PREVIEW_HOT_ROOT, "generated_at": "2026-07-08T00:00:00Z"}]
    assert result["market_regime_card_shell_rendered"] is True
    assert result["market_regime_first"] is True
    assert result["future_prediction_rows_reserved"] is True
    assert result["future_prediction_card_rows"][:3] == ["方向感", "反転候補", "ボラ警戒"]
    assert result["prediction_invoked"] is False
    assert result["classifier_invoked"] is False
    assert result["broker_action_allowed"] is False
    assert any("prediction_cards_scope=market_regime_first" in caption for caption in fake_st.captions)
    assert any("次の予測カード行 追加枠" in caption for caption in fake_st.captions)
    assert fake_st.tables
