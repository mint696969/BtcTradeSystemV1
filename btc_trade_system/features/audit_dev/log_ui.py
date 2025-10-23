# path: ./btc_trade_system/features/audit_dev/log_ui.py
# desc: 開発監査ログのビュー部品。モード別フィルタで直近24hの最大50行をJST表示、10行固定窓に出す。DLはJSTで最大500行。

from __future__ import annotations
import json, io
from pathlib import Path
from typing import Iterable, List, Tuple
from datetime import datetime, timezone, timedelta

import streamlit as st

from btc_trade_system.common.paths import logs_dir

# ---- 表示スタイル（10行固定・縦横スクロール） ----
def _ensure_log_code_css() -> None:
    # rerunで<style>が消える環境があるため、毎回注入
    st.markdown(
        """
        <style>
        :root { --log-line: 1.45em; }
        [data-testid="stCode"], [data-testid="stCodeBlock"]{ min-height: calc(var(--log-line)*10) !important; }
        [data-testid="stCode"] pre, [data-testid="stCode"] code,
        [data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code{
            min-height: calc(var(--log-line)*10) !important;
            max-height: calc(var(--log-line)*10) !important;
            overflow: auto !important;
            white-space: pre !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---- ログ読み込み＆フィルタ ----
_LEVEL_RANK = {"DEBUG":10,"INFO":20,"WARN":30,"WARNING":30,"ERROR":40,"CRIT":50,"CRITICAL":50}
def _mode_min_level(mode:str) -> int:
    m = (mode or "OFF").upper()
    if m == "OFF":   return _LEVEL_RANK["ERROR"]  # 重篤のみ
    if m == "DEBUG": return _LEVEL_RANK["WARN"]   # 注意以上
    return 0  # BOOST=全件

_JST = timezone(timedelta(hours=9))

def _iter_tail(path: Path, max_bytes: int = int(1.5 * 1024 * 1024)) -> Iterable[str]:
    """末尾から最大 ~1.5MB を読み、行で返す（サイズは十分に軽量）。"""
    if not path.exists():
        return []
    size = path.stat().st_size
    with open(path, "rb") as rf:
        if size > max_bytes:
            rf.seek(size - max_bytes)
            blob = rf.read()
            # 途中行を切り捨てて先頭の完全行へ
            p = blob.find(b"\n")
            if p != -1:
                blob = blob[p+1:]
        else:
            blob = rf.read()
    text = blob.decode("utf-8", "ignore")
    return text.splitlines()

def _parse_and_filter(lines: Iterable[str], mode:str, hours:int, limit:int, keyword: str = "") -> Tuple[List[str], List[dict]]:
    """UI表示用テキスト行（JST）と、DL用の構造行（JST変換済）を返す。keyword は表示フィルタのみ。"""
    min_rank = _mode_min_level(mode)
    now_utc = datetime.now(timezone.utc)
    since = now_utc - timedelta(hours=hours)
    kw = (keyword or "").lower()

    shown: List[str] = []
    kept: List[dict] = []

    for raw in reversed(list(lines)):  # 新しい順に見る
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        ts = rec.get("ts")
        lvl = str(rec.get("level","")).upper()
        if _LEVEL_RANK.get(lvl, 999) < min_rank:
            continue
        try:
            # ts: "YYYY-MM-DDTHH:MM:SS(.mmm)Z" をUTCとして解釈（ミリ秒あり/なし両対応）
            if ts and ts.endswith("Z"):
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                except ValueError:
                    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            else:
                dt = datetime.fromisoformat(ts).astimezone(timezone.utc) if ts else now_utc
        except Exception:
            dt = now_utc

        if dt < since:
            continue

        # --- キーワード（表示のみ）：event / feature / level / payload に部分一致 ---
        if kw:
            hay = []
            hay.append(str(rec.get("event","")))
            hay.append(str(rec.get("feature","")))
            hay.append(lvl)
            payload = rec.get("payload")
            if isinstance(payload, (str, int, float, bool)):
                hay.append(str(payload))
            elif isinstance(payload, dict):
                if "note" in payload:
                    hay.append(str(payload.get("note")))
                try:
                    hay.append(json.dumps(payload, ensure_ascii=False))
                except Exception:
                    pass
            if kw not in (" ".join(hay)).lower():
                continue

        jst = dt.astimezone(_JST)
        # 表示は1行テキスト（JST）
        event = rec.get("event","")
        feature = rec.get("feature","")
        msg = rec.get("payload", None)
        msg_short = ""
        if isinstance(msg, (str,int,float,bool)):
            msg_short = str(msg)
        elif isinstance(msg, dict) and "note" in msg:
            msg_short = str(msg.get("note"))
        # YYYY-MM-DD HH:MM:SS JST [LEVEL] feature event - note
        line = f'{jst.strftime("%Y-%m-%d %H:%M:%S")} JST [{lvl}] {feature} {event}'
        if msg_short:
            line += f" - {msg_short}"
        shown.append(line)

        # DLはJSONだが ts を JST に差し替え（ts_jst キーで保持）
        rec_dl = dict(rec)
        rec_dl["ts_jst"] = jst.strftime("%Y-%m-%d %H:%M:%S")
        kept.append(rec_dl)

        if len(shown) >= limit:  # 最大50
            break
    return shown, kept

def _download_blob(rows: List[dict], max_rows: int) -> bytes:
    buf = io.StringIO()
    n = 0
    for rec in rows[:max_rows]:
        buf.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
        n += 1
    return buf.getvalue().encode("utf-8")

def render_log_panel(mode: str) -> None:
    """
    監査タブ最下部用のログビュー。
    共通条件: 最新から24時間・最大50行をJSTで1窓に表示（10行固定）。DLはモード別フィルタでJST、最大500行。
    """

    # --- Auto refresh（リアルタイム表示用。既定ON / 2秒） ---
    try:
        # streamlit の autorefresh（未実装版でも例外で無視）
        from streamlit import experimental_rerun  # noqa: F401
        from streamlit import autorefresh as st_autorefresh  # type: ignore[attr-defined]
    except Exception:
        st_autorefresh = None  # type: ignore

    # UIで切替可能（既定ON）。重い環境ではOFFにできる。
    st.session_state.setdefault("log_autorefresh", True)
    with st.container():
        col_a, col_b = st.columns([1.2, 6])
        with col_a:
            st.checkbox("Auto refresh (2s)", key="log_autorefresh")
        with col_b:
            # 最終更新時刻の表示（JST）
            st.caption("updated at " + datetime.now(_JST).strftime("%Y-%m-%d %H:%M:%S JST"))

    if st_autorefresh and st.session_state.get("log_autorefresh", True):
        try:
            st_autorefresh(interval=2000, key="log_panel_autorefresh")
        except Exception:
            pass

    # --- Filter（表示のみ適用。DLには影響させない） ---
    with st.expander("Filter (display only)", expanded=False):
        _kw = st.text_input(
            "keyword (event / feature / level / payload に部分一致)",
            value="",
            placeholder="例: error / ui / bybit など",
            label_visibility="collapsed",
        )
        keyword = (_kw or "").strip().lower()

    path = Path(logs_dir()) / "dev_audit.jsonl"
    lines = list(_iter_tail(path))
    shown, kept = _parse_and_filter(lines, mode=mode, hours=24, limit=50, keyword=keyword)

    # 1行要約（任意）
    newest_age = "-"
    if kept:
        jst = kept[0].get("ts_jst")
        # age は大雑把に（UI上の安心材料）
        newest_age = f'newest={jst}'
    st.caption(f"last 24h: matched={len(shown)} (mode={mode}) / {newest_age}")

    _ensure_log_code_css()
    text = "\n".join(shown) if shown else "\u200b\n"  # 空でも10行枠を維持
    st.code(text, language="text")

    # ダウンロード（JST付きJSONL, 最大500行）
    blob = _download_blob(kept, max_rows=500)
    ts_tag = datetime.now(_JST).strftime("%Y%m%d_%H%M%S")
    file_name = f"dev_audit.{(mode or 'OFF').lower()}.{ts_tag}.jst.jsonl"
    st.download_button(
        label=f"ログをダウンロード（JST・最大500行）",
        data=blob,
        file_name=file_name,
        mime="application/json",
        use_container_width=True,
    )

    # --- Dev quick test: 監査ログへ即時書き込み（診断用） ---
    with st.expander("Dev quick test (emit)", expanded=False):
        col1, col2 = st.columns(2)
        from btc_trade_system.features.audit_dev import writer as _w
        with col1:
            if st.button("1行だけ emit", use_container_width=True):
                _w.emit("dev.ui.test.once", level="INFO", feature="audit_dev", note="ui test once")
                st.success("wrote 1 line")
        with col2:
            if st.button("20行 emit（軽め）", use_container_width=True):
                _w.set_mode("BOOST")  # 念のため表示と同じく緩める
                for i in range(20):
                    _w.emit("dev.ui.test.bulk", level="DEBUG", feature="audit_dev", i=i, note="ui test bulk")
                st.success("wrote 20 lines")
