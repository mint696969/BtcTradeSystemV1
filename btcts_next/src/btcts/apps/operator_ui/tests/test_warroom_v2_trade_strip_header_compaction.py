# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_trade_strip_header_compaction.py
# desc: Structural guard for WarRoom Trade strip one-line header and diagnostics-in-accordion layout.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
TRADE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/trade_strip_view.py"


def test_trade_strip_header_merges_section_label_and_read_only_caption() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    trade = TRADE.read_text(encoding="utf-8-sig")

    assert 'render_compact_section_label(st, index=2, title="Trade strip", note="orders / position / PnL　　取引データ: 注文 / 建玉 / 確定時刻 / 損益 / コンパクト表示 / 読み取り専用")' in page
    assert 'render_compact_section_label(st, index=2, title="Trade strip", note="orders / position / PnL")' not in page
    assert 'st_api.caption("取引データ: 注文 / 建玉 / 確定時刻 / 損益 / コンパクト表示 / 読み取り専用")' not in trade
    assert 'cols = st_api.columns(8)' in trade


def test_trade_strip_connection_context_is_inside_details_accordion_bottom() -> None:
    trade = TRADE.read_text(encoding="utf-8-sig")

    context_pos = trade.index("trade_context =")
    expander_pos = trade.index('with st_api.expander("取引データの詳細", expanded=False):', context_pos)
    dataframe_pos = trade.index("st_api.dataframe(", expander_pos)
    caption_pos = trade.index("st_api.caption(trade_context)", dataframe_pos)
    return_pos = trade.index("return {", caption_pos)
    assert context_pos < expander_pos < dataframe_pos < caption_pos < return_pos

    before_expander = trade[context_pos:expander_pos]
    assert "st_api.caption(trade_context)" not in before_expander
    assert "データ源=" in trade
    assert "order_intent_submitted=false" in trade
