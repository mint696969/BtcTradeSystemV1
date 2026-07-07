# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_market_strip_header_compaction.py
# desc: Structural guard for WarRoom Market strip one-line compact section header.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
MARKET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_strip_view.py"


def test_market_strip_header_merges_section_label_and_read_only_caption() -> None:
    page = PAGE.read_text(encoding="utf-8-sig")
    market = MARKET.read_text(encoding="utf-8-sig")

    assert 'render_compact_section_label(st, index=1, title="Market strip", note="manual-trade market essentials　　市場データ: 手動取引用の必須情報 / コンパクト表示 / 読み取り専用 / broker送信なし")' in page
    assert 'render_compact_section_label(st, index=1, title="Market strip", note="manual-trade market essentials")' not in page
    assert 'st_api.caption("市場データ: 手動取引用の必須情報 / コンパクト表示 / 読み取り専用 / broker送信なし")' not in market
    assert 'cols = st_api.columns(8)' in market

def test_market_strip_context_caption_is_inside_details_accordion_bottom() -> None:
    market = MARKET.read_text(encoding="utf-8-sig")

    context_pos = market.index("compact_context =")
    expander_pos = market.index('with st_api.expander("市場データの詳細", expanded=False):', context_pos)
    dataframe_pos = market.index("st_api.dataframe(", expander_pos)
    caption_pos = market.index("st_api.caption(compact_context)", dataframe_pos)
    return_pos = market.index("return {", caption_pos)
    assert context_pos < expander_pos < dataframe_pos < caption_pos < return_pos

    before_expander = market[context_pos:expander_pos]
    assert "st_api.caption(compact_context)" not in before_expander
