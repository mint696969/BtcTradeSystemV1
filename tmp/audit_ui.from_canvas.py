# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: AuditタブのUI（開発監査表示専用）。BOOST切替時スナップショット生成対応・lint誤検出回避。ボタン色: OFF=白, DEBUG=黄, BOOST=赤。

from __future__ import annotations
import json
import time
from pathlib import Path

import streamlit as st

from ...common import paths
# services（features 平置きの正式ルート）
from btc_trade_system.features.dash.audit_svc import (
    get_audit_rows as svc_get_audit_rows,
)
# 開発監査のモード制御（writer 直結）
from btc_trade_system.features.audit_dev.writer import (
    get_mode as _dev_get_mode,
    set_mode as _dev_set_mode,
)

from btc_trade_system.common import boost_svc


def _log_file() -> Path:
    return paths.logs_dir() / "dev_audit.jsonl"


def _mode_next(m: str) -> str:
    chain = ["OFF", "DEBUG", "BOOST"]
    m = (m or "OFF").upper()
    return chain[(chain.index(m) + 1) % len(chain)] if m in chain else "OFF"


def _mode_color(m: str) -> str:
    m = (m or "OFF").upper()
    # OFF=白, DEBUG=黄, BOOST=赤
    return {"OFF": "#fff", "DEBUG": "#ffcc00", "BOOST": "#e33b3b"}.get(m, "#fff")


def _auto_interval_ms(m: str) -> int:
    """
    OFF: 0ms（自動更新しない）
    DEBUG: 2000ms
    BOOST: 1000ms
    """
    m = (m or "OFF").upper()
    return 0 if m == "OFF" else (2000 if m == "DEBUG" else 1000)


def render():
    st.markdown("<div id='audit-area'>", unsafe_allow_html=True)

    # dev_mode の初期化を必ず実施（KeyError防止）
    if "dev_mode" not in st.session_state:
        try:
            st.session_state.dev_mode = _dev_get_mode()
        except Exception:
            st.session_state.dev_mode = "OFF"

    c0, c1 = st.columns([1.2, 6.8])

    # --- 左：モードボタン（このブロックだけにCSSを限定） ---
    with c0:
        cur = (st.session_state.get("dev_mode", "OFF") or "OFF").upper()

        # ---- dev-mode ボタン（確実に色が当たるよう “後方兄弟(~)” と data-testid で限定）----
        # Streamlit は各ウィジェットを独立ブロックに描画するため、
        # 直前の <div> とボタンの間に内部ブロックが入る場合がある。
        # そのため「隣接(+ )」ではなく「後方兄弟(~)」セレクタで確実にヒットさせる。
        st.markdown("<div id='dev-mode-anchor'></div>", unsafe_allow_html=True)

        clicked = st.button(cur, use_container_width=True, key="dev_mode_btn")

        # OFF=白(黒字/薄グレー枠), DEBUG=黄, BOOST=赤
        col = _mode_color(cur)
        bg = "#fff" if cur == "OFF" else col
        fg = "#111" if cur == "OFF" else "#fff"
        bd = "#ddd" if cur == "OFF" else col
        bd_hover = "#ccc" if cur == "OFF" else col

        css = f"""
        <style>
        /* dev-mode-anchor 以降に現れる “このボタン” だけに配色を当てる */
        #dev-mode-anchor ~ div [data-testid="stButton"] > button,
        #dev-mode-anchor ~ div button[data-testid^="baseButton"] {{
          height:40px; line-height:40px; margin-top:4px;
          background:{bg} !important;
          background-color:{bg} !important;
          border-color:{bd} !important;
          color:{fg} !important;
          border-width:1px !important; border-style:solid !important; border-radius:8px !important;
          box-shadow:none !important; text-shadow:none !important;
        }}
        #dev-mode-anchor ~ div [data-testid="stButton"] > button:hover,
        #dev-mode-anchor ~ div button[data-testid^="baseButton"]:hover {{
          background:{bg} !important;
          background-color:{bg} !important;
          border-color:{bd_hover} !important;
          color:{fg} !important;
          opacity:0.96;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

        # ▼ クリックでモードを遷移させ、保存 → 画面を再実行
        if clicked:
            nxt = _mode_next(cur)
            err = None
            try:
                _dev_set_mode(nxt)
                st.session_state.dev_mode = nxt
                if nxt == "BOOST":
                    # ここでは UI 要素を追加/削除しない（メッセージだけ）。rerun 後に描画。
                    boost_svc.export_snapshot(force=True)
                    st.session_state["handover_text"] = boost_svc.build_handover_text()
            except Exception as e:
                err = e

            if err is None:
                st.rerun()
            else:
                st.warning(f"モード更新に失敗しました: {err!r}")

    # --- 右：タイトル＆案内 ---
    with c1:
        st.markdown(
            "<div style='display:flex;align-items:center;height:40px;'><span style='font-size:1.2rem;font-weight:600;'>開発監査ログ（dev_audit.jsonl）</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="white-space:nowrap;color:var(--text-color-secondary,#6c757d);font-size:0.9rem;">
              Tail（PowerShell）: Get-Content D:\\BtcTS_V1\\logs\\dev_audit.jsonl -Tail 50 -Wait
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- GPT 引き継ぎパネル（※必ず render() 内に置く） ---
    with st.expander(
        "GPT引き継ぎ（BOOSTスナップショットから自動生成）",
        expanded=(st.session_state.get("dev_mode", "OFF") == "BOOST"),
    ):
        # 1) 最新テキスト（初回はスナップショットから生成）
        try:
            if "handover_text" not in st.session_state:
                st.session_state["handover_text"] = boost_svc.build_handover_text()
        except Exception:
            st.session_state["handover_text"] = "# Handover text is not available."

        st.text_area(
            "コピペ用テキスト",
            st.session_state["handover_text"],
            height=220,
            key="handover_text",
        )

        # 2) アクション（再生成 / handover_gpt.txt を更新して即DL / snapshot DL）
        cA, cB, cC = st.columns([1.3, 1.6, 1.3])

        # 2-1) スナップショットを強制再生成 → テキストを即反映
        with cA:
            if st.button("スナップショット再生成", key="btn_force_snapshot"):
                try:
                    boost_svc.export_snapshot(force=True)
                    st.session_state["handover_text"] = boost_svc.build_handover_text()
                    st.success("スナップショットを再生成しました。")
                except Exception as e:
                    st.warning(f"スナップショット生成に失敗: {e!r}")

        # 2-2) handover_gpt.txt を生成して、その場でダウンロード
        with cB:
            if st.button("handover_gpt.txt を更新してDL", key="btn_export_handover"):
                try:
                    p = boost_svc.export_handover_text(force=True)
                    b = Path(p).read_bytes()
                    st.download_button(
                        "handover_gpt.txt をダウンロード",
                        data=b,
                        file_name="handover_gpt.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key=f"dl_handover_{int(time.time()*1000)}",
                    )

                    st.caption(f"source: {p}（{len(b)} bytes）")
                except Exception as e:
                    st.warning(f"handover_gpt.txt の生成に失敗しました: {e!r}")

        # 2-3) 直近の boost_snapshot.json もDL
        with cC:
            try:
                snap_p = Path(boost_svc.export_snapshot(force=False))
                if snap_p.exists():
                    st.download_button(
                        "boost_snapshot.json をDL",
                        data=snap_p.read_bytes(),
                        file_name="boost_snapshot.json",
                        mime="application/json",
                        use_container_width=True,
                        key=f"dl_snapshot_{int(time.time()*1000)}",
                    )

                    st.caption(f"snapshot: {snap_p}（{snap_p.stat().st_size} bytes）")
            except Exception:
                pass

        # --- 自動更新（BOOST=1s / DEBUG=2s / OFF=なし） ---
        cur_mode = st.session_state.get("dev_mode", "OFF")
        interval = _auto_interval_ms(cur_mode)
        if interval > 0:
            st.caption(f"Auto refresh: {interval} ms")
            _auto_js = f"""
            <script>
            (function(){{
              var ms = {interval};
              if (ms > 0) {{
                setTimeout(function() {{
                  if (document.visibilityState === 'visible') {{
                    window.location.reload();
                  }}
                }}, ms);
              }}
            }})();
            </script>
            """
            st.markdown(_auto_js, unsafe_allow_html=True)

    # --- フィルタ & テーブル ---
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
    with c1:
        q = st.text_input("キーワード", "", placeholder="event=/feature=/payload 内を部分一致（例: RATE_LIMIT）")
    with c2:
        level = st.selectbox("レベル", ["ALL", "INFO", "WARN", "ERROR", "CRIT"], index=0)
    with c3:
        exchange = st.text_input("exchange", "", placeholder="binance / bitflyer / ...")
    with c4:
        component = st.text_input("component", "", placeholder="collector / dashboard / ...")
    with c5:
        limit = st.selectbox("件数", [200, 500, 1000], index=1)

    rows = svc_get_audit_rows(
        max_lines=int(limit),
        level=None if level == "ALL" else level,
        q=(q or None),
    )

    def _match(r: dict) -> bool:
        if level != "ALL" and (r.get("level") or "").upper() != level:
            return False
        if exchange and exchange.lower() not in (r.get("exchange", "") or "").lower():
            return False
        if component and component.lower() not in (r.get("component", "") or "").lower():
            return False
        if q:
            s = " ".join(
                [
                    r.get("event", ""),
                    r.get("feature", ""),
                    r.get("exchange", ""),
                    r.get("component", ""),
                    r.get("actor", ""),
                    r.get("site", ""),
                    r.get("session", ""),
                    str(r.get("payload", "")),
                ]
            ).lower()
            return q.lower() in s
        return True

    rows = [r for r in rows if _match(r)]
    st.caption(f"{len(rows)} 件")
    try:
        st.caption(f"source: {(_log_file())}")
    except Exception:
        pass

    if rows:
        import pandas as pd
        import json as _json

        df = pd.DataFrame(rows)
        prefer = [
            "ts", "level", "feature", "event", "exchange", "topic", "actor", "site", "session",
            "latency_ms", "rows", "retries", "payload",
        ]
        show_cols = [c for c in prefer if c in df.columns]
        if show_cols:
            df = df[show_cols]

        for col in ("latency_ms", "rows", "retries"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        if "payload" in df.columns:
            df["payload"] = df["payload"].apply(
                lambda x: _json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else ("" if x is None else x)
            )

        st.dataframe(df, use_container_width=True, hide_index=True, height=480)
    else:
        st.info("dev_audit.jsonl が無いか、条件に一致する行がありません。")

    # 開始時に開いた div をここで閉じる（※関数外に出さない）
    st.markdown("</div>", unsafe_allow_html=True)
