# path: ./btc_trade_system/features/dash/audit_ui.py
# desc: AuditタブのUI（表示専用）— svc_audit で集計・検索したデータを描画

from __future__ import annotations
from ...common import paths
import streamlit as st
# services（features 平置きの正式ルート）
from btc_trade_system.features.dash.audit_svc import get_audit_rows

import json
from collections import deque
from pathlib import Path
from typing import Iterable

def _log_file() -> Path:
    # logs/audit.jsonl を返す（環境変数に依存せず paths で解決）
    return paths.logs_dir() / "audit.jsonl"

def _iter_lines(p: Path) -> Iterable[str]:
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield line

def get_audit_rows(
    max_lines: int = 500,
    *,
    level: str | None = None,
    q: str | None = None,
    exchange: str | None = None,
    component: str | None = None,
) -> list[dict]:
    """
    logs/audit.jsonl の末尾から新しい順に最大 max_lines を返す。
    level は大文字(INFO/WARN/ERROR/CRIT)で一致、q/交換/コンポーネントは部分一致(大小無視)。
    """
    p = _log_file()
    buf: deque[dict] = deque(maxlen=max(100, int(max_lines) * 3))  # フィルタ後に目減りしにくいよう余裕を持つ

    for line in _iter_lines(p):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        buf.append(obj)

    rows = list(reversed(buf))  # 新しい順
    if not rows:
        return []

    # 正規化（欠損に強い）
    def norm(s): return (s or "").strip()
    L = level.upper() if isinstance(level, str) else None
    ql = (q or "").lower()
    exl = (exchange or "").lower()
    col = (component or "").lower()

    out: list[dict] = []
    for r in rows:
        r_level = norm(r.get("level")).upper()
        r_exchange = norm(r.get("exchange"))
        r_component = norm(r.get("component") or r.get("feature") or r.get("module"))
        r_text = " ".join([
            norm(r.get("event")), norm(r.get("feature")), r_exchange, r_component,
            norm(r.get("actor")), norm(r.get("site")), norm(r.get("session")),
            json.dumps(r.get("payload"), ensure_ascii=False) if isinstance(r.get("payload"), (dict, list)) else norm(r.get("payload")),
            norm(r.get("message")),
        ]).lower()

        if L and r_level != L:
            continue
        if exl and exl not in r_exchange.lower():
            continue
        if col and col not in r_component.lower():
            continue
        if ql and ql not in r_text:
            continue

        out.append(r)

        if len(out) >= max_lines:
            break

    return out

def render():
    st.subheader("監査ログ")
    st.caption("Tail: PowerShell →  Get-Content .\\logs\\audit.jsonl -Tail 50 -Wait")
    c1, c2, c3, c4, c5 = st.columns([2,1,1,1,1])
    with c1:
        q = st.text_input("キーワード", "", placeholder="event=/feature=/payload 内を部分一致（例: RATE_LIMIT）")
    with c2:
        level = st.selectbox("レベル", ["ALL","INFO","WARN","ERROR","CRIT"], index=0)
    with c3:
        exchange = st.text_input("exchange", "", placeholder="binance / bitflyer / ...")
    with c4:
        component = st.text_input("component", "", placeholder="collector / dashboard / ...")
    with c5:
        limit = st.selectbox("件数", [200,500,1000], index=1)

    # --- 呼び出しパラメータ修正 ---
    rows = get_audit_rows(
        max_lines=int(limit),
        level=None if level == "ALL" else level,
        q=(q or None),
        exchange=(exchange or None),
        component=(component or None),
    )

    def _match(r: dict) -> bool:
        if level != "ALL" and (r.get("level") or "").upper() != level:
            return False
        if exchange and exchange.lower() not in (r.get("exchange","") or "").lower():
            return False
        if component and component.lower() not in (r.get("component","") or "").lower():
            return False
        if q:
            s = " ".join([
                r.get("event",""), r.get("feature",""), r.get("exchange",""),
                r.get("component",""), r.get("actor",""), r.get("site",""),
                r.get("session",""), str(r.get("payload","")),
            ]).lower()
            return q.lower() in s
        return True

    rows = [r for r in rows if _match(r)]
    st.caption(f"{len(rows)} 件")
    # 実際の読み取り元パスを明示（迷子防止）
    try:
        st.caption(f"source: {(_log_file())}")
    except Exception:
        pass

    if rows:
        import pandas as pd
        import numpy as np
        import json as _json

        df = pd.DataFrame(rows)

        # “あれば表示”の優先順（存在しない列は自動で落ちる）
        prefer = [
            "ts","level","feature","event",
            "exchange","topic","actor","site","session",
            "latency_ms","rows","cause","retries",
            "payload"
        ]
        show_cols = [c for c in prefer if c in df.columns]
        if show_cols:
            df = df[show_cols]

        # Arrow 互換のための型整形（混在型を排除）
        if "latency_ms" in df.columns:
            # 数値列は NaN を保持できる pandas の nullable 型に
            df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce").astype("Int64")
        if "rows" in df.columns:
            df["rows"] = pd.to_numeric(df["rows"], errors="coerce").astype("Int64")
        if "retries" in df.columns:
            df["retries"] = pd.to_numeric(df["retries"], errors="coerce").astype("Int64")
        # payload が dict/list の場合は JSON 文字列に正規化（Arrow で詰まらないように）
        if "payload" in df.columns:
            df["payload"] = df["payload"].apply(
                lambda x: _json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else ("" if x is None else x)
            )

        # 新 API 推奨パラメータに変更
        st.dataframe(df, width="stretch", hide_index=True, height=480)

    else:
        st.info("audit.jsonl が無いか、条件に一致する行がありません。")
