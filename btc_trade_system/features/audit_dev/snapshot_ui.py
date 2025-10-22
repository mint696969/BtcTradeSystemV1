# path: ./btc_trade_system/features/audit_dev/snapshot_ui.py
# desc: 開発監査UIヘルパー（スナップショットのテキストエリア描画・REPO_MAP抜粋整形）

from __future__ import annotations
import streamlit as st

# 互換エイリアス（旧呼び出しが残っていても安全に無視）
def ensure_snapshot_textarea_css(*, text: str = "", include_label: bool = True) -> None:
    """
    スナップショットを“コード窓”(st.code)で表示。
    - 10行固定（スクロール可）は ensure_snapshot_code_css() が担保
    - ボックス内の先頭に [[snapshot]] を入れる（include_label=True のとき）
    - コピーアイコンは st.code で自動表示
    """
    ensure_snapshot_code_css()

    content = text or ""
    if include_label:
        content = f"[[snapshot]]\n{content}" if content else "[[snapshot]]"

    # language='text' にすると装飾の少ない等幅表示＋コピーアイコン
    st.code(content, language="text")

def repo_map_excerpt(snap_json: dict, mode: str) -> str:
    """スナップショットJSONから REPO_MAP 抜粋をMarkdown文字列で返す。欠損時は空文字。"""
    try:
        repo_map = snap_json.get("repo_map", {}) if isinstance(snap_json, dict) else {}
        if not repo_map:
            return ""

        total = int(repo_map.get("total", 0) or 0)
        items = repo_map.get("items") or []

        # --- 重複除去（path を大文字小文字無視＆区切り統一） ---
        seen = set()
        uniq_items = []
        for it in items:
            p = (it.get("path", "") or "").strip()
            key = p.lower().replace("\\", "/")
            if key and key not in seen:
                seen.add(key)
                uniq_items.append(it)

        show_n = 50 if (mode or "").upper() == "DEBUG" else 200
        head = uniq_items[:show_n]

        lines: list[str] = []
        lines.append("")
        lines.append("## REPO_MAP (excerpt)")
        # 表示件数はユニーク後ベースに合わせる
        lines.append(f"- showing: {min(len(uniq_items), show_n)}/{len(uniq_items)}")
        for it in head:
            pth = it.get("path", "")
            desc = it.get("desc", "")
            lines.append(f"- {pth} — {desc}")

        return "\n".join(lines)
    except Exception:
        return ""

# --- copyable code-box helpers -------------------------------------------------

def ensure_snapshot_code_css() -> None:
    """st.code を10行固定（空でも潰れない）＋縦横スクロールにするCSSを一度だけ注入。"""
    key = "_snap_code_css_done_v2"
    if st.session_state.get(key):
        return
    st.markdown(
        """
        <style>
        /* st.code（コピーアイコン付き）を“常に10行ぶんの高さ”で表示し、横/縦スクロールさせる */
        /* コンテナ側にも min-height を入れて、内容が空でも潰れないようにする */
        [data-testid="stCodeBlock"] {
            min-height: calc(1.45em * 10);
        }
        [data-testid="stCodeBlock"] pre {
            min-height: calc(1.45em * 10);   /* 空でも10行ぶんの高さを確保 */
            max-height: calc(1.45em * 10);   /* 伸びすぎ防止（常に10行ぶん）*/
            overflow: auto;                  /* 横/縦スクロール */
            white-space: pre;                /* 折り返さず横スクロール */
            margin: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.session_state[key] = True

def render_snapshot_code(text: str) -> None:
    """
    コピーアイコン付きの“コード窓”でスナップショットを表示。
    高さは10行固定。引数 text はそのままコピー対象になります。
    """
    ensure_snapshot_code_css()
    # st.code を使うと自動でコピーアイコンが付く
    st.code(text or "", language="")
