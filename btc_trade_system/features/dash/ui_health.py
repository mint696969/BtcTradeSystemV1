# path: ./btc_trade_system/features/dash/ui_health.py
# desc: Health タブ（収集健全性のサマリ表示＋タイムライン）。状態色は get_status() が返す4段階でヘッダーに連携。

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import streamlit as st
import matplotlib.pyplot as plt

from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.features.health.health_svc import read_health
from btc_trade_system.features.health import health_order
from btc_trade_system.features.settings import settings_svc  # 追加

# --- add: CSS (every render) & card html builder ------------------------------------
def _inject_health_css():
    st.markdown("""
<style>
.health-card{border-radius:12px;padding:12px;margin-bottom:10px}
.health-hd{font-weight:700;margin-bottom:6px}
.health-grid{display:flex;gap:24px;flex-wrap:wrap}
.health-kv{min-width:86px}
.health-kv .k{font-size:12px;color:#6b7280;margin-bottom:2px}
.health-kv .v{font-size:20px;line-height:1.0}
.health-cap{font-size:12px;color:#6b7280;margin-top:4px}
</style>
""", unsafe_allow_html=True)

def _card_html(*, endpoint:str, level:str, age_txt:str,
               retries:int, cause:str, notes:str,
               border_color:str, fill_color:str, placeholder:bool)->str:
    # placeholder は値をダッシュ表示
    if placeholder:
        level_txt = "—"
        age_txt   = "—"
        retries   = 0
        cause     = "未収集"
        # 既定の薄灰を背景に
        fill_color = "#f3f4f6"
    else:
        level_txt = level or "OK"
    return f"""
<div class="health-card" style="border:2px solid {border_color}; background:{fill_color}; border-radius:12px;">
  <div class="health-hd">{endpoint}</div>
  <div class="health-grid">
    <div class="health-kv"><div class="k">状態</div><div class="v">{level_txt}</div></div>
    <div class="health-kv"><div class="k">遅延</div><div class="v">{age_txt}</div></div>
    <div class="health-kv"><div class="k">再試行</div><div class="v">{int(retries)}</div></div>
  </div>
  <div class="health-cap">原因: {cause or '-'}</div>
  {f'<div class="health-cap">メモ: {notes}</div>' if (notes and notes != '-') else ''}
</div>
"""

# ---------- ユーティリティ ----------

def _get_counts(h) -> Dict[str, int]:
    # h.counts を想定（dict）。無ければフォールバック。
    counts = getattr(h, "counts", None) or {}
    if counts:
        return {k: int(counts.get(k, 0)) for k in ("OK", "WARN", "CRIT")}
    # items から集計（念のため）
    items = getattr(h, "items", None) or []
    agg = {"OK": 0, "WARN": 0, "CRIT": 0}
    for iv in items:
        level = getattr(iv, "level", None) or (isinstance(iv, dict) and iv.get("level"))
        if level in agg:
            agg[level] += 1
    return agg

def _items_iter(h) -> Iterable[Dict[str, Any]]:
    """dataclass/obj or dict の両対応で items を辞書化して返す。"""
    items = getattr(h, "items", None) or []
    for iv in items:
        if isinstance(iv, dict):
            yield iv
        else:
            yield {
                "exchange": getattr(iv, "exchange", None),
                "topic": getattr(iv, "topic", None),
                "last_ok": getattr(iv, "last_ok", None),
                "age_sec": getattr(iv, "age_sec", None),
                "retries": getattr(iv, "retries", 0),
                "cause": getattr(iv, "cause", None),
                "notes": getattr(iv, "notes", None),
                "source": getattr(iv, "source", None),
                "level": getattr(iv, "level", None) or "OK",
            }

def _fmt_age(sec: Optional[float]) -> str:
    if sec is None:
        return "—"
    try:
        s = float(sec)
    except Exception:
        return "—"
    if s < 120:
        return f"{int(s)}s"
    if s < 3600:
        return f"{int(s // 60)}m"
    return f"{s / 3600:.1f}h"

def _timeline(ax, status: str, age_sec: Optional[float], window_s: int, palette: dict) -> None:
    """右端=現在。未更新区間（age）を右側に塗る。"""
    if ax is None:
        return
    age = max(0.0, float(age_sec or 0.0))
    age = min(age, float(window_s))
    ok_len = max(0.0, window_s - age)

    # パレット連動
    ok_color = palette["bar_fill"].get("ok", "#d1fae5")
    miss_color = palette["bar_fill"].get((status or "OK").lower(), "#d1fae5")

    ax.barh([0], [ok_len], color=ok_color, height=0.5)
    ax.barh([0], [age], left=[ok_len], color=miss_color, height=0.5)
    ax.set_xlim(0, window_s)
    ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([])
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)

def _order_and_fill(items: list[dict]) -> tuple[list[dict], list[str]]:
    """
    health.yaml の order に合わせて items を並べ替え、
    order に載っているが items に存在しない exchange は
    プレースホルダ（__placeholder__=True）を追加する。
    戻り値: (ordered_items, order)
    """
    # items から実在する取引所集合
    present = []
    seen = set()
    for iv in items:
        ex = iv.get("exchange")
        if not ex:
            continue
        present.append(iv)
        seen.add(ex)

    # order の取得（失敗時は items 側の exchange をアルファベット順）
    try:
        order = health_order.load_order()
        # load_order() が list[str] を返す前提（無ければ例外）
        if not isinstance(order, (list, tuple)) or not order:
            raise ValueError("empty order")
        order = list(order)
    except Exception:
        order = sorted(list(seen))

    # 既存 item を order 順に並べる（同一 exchange 内は既存順）
    by_ex = {}
    for iv in present:
        by_ex.setdefault(iv.get("exchange"), []).append(iv)

    ordered: list[dict] = []
    for ex in order:
        if ex in by_ex:
            ordered.extend(by_ex[ex])
        else:
            # プレースホルダを 1 枚だけ入れる（カード/タイムライン共通で扱える最小構造）
            ordered.append({
                "exchange": ex,
                "topic": "-",
                "last_ok": None,
                "age_sec": None,
                "retries": 0,
                "cause": "未収集",
                "notes": None,
                "source": "placeholder",
                "level": "OK",         # 見た目の崩れ回避のため OK とする（枠色は後で調整可）
                "__placeholder__": True,
            })

    # order に載っていない余剰 exchange（もしあれば）は末尾へ（現状維持）
    for ex, rows in by_ex.items():
        if ex not in order:
            ordered.extend(rows)

    return ordered, order

# ---------- タブ状態（ヘッダー色） ----------

def get_status() -> str:
    """
    "normal" | "warn" | "crit" | "urgent"
    - urgent は将来拡張（長時間 CRIT 継続や致命的障害で昇格）
    """
    try:
        h = read_health()
        counts = _get_counts(h)
    except Exception as e:
        W.emit("tab.health.status_error", level="WARN", feature="health", payload={"err": str(e)})
        return "warn"

    if counts.get("CRIT", 0) > 0:
        return "crit"
    if counts.get("WARN", 0) > 0:
        return "warn"
    return "normal"

def _get_palette():
    """
    monitoring.yaml → palette を取得。無ければ既定色を返す。
    """
    try:
        mon = settings_svc.load_yaml("monitoring") or {}
    except Exception:
        mon = {}

    pal = mon.get("palette") or {}
    # 既定色（UIの見えを大きく変えないニュートラル寄り）
    defaults = {
        "card_border": {"ok": "#10b981", "warn": "#f59e0b", "crit": "#ef4444"},
        "bar_fill":    {"ok": "#d1fae5", "warn": "#fef3c7", "crit": "#fee2e2"},
        "card_fill":   {"ok": "#ecfdf5", "warn": "#fffbeb", "crit": "#fef2f2"},  # 追加
    }
    # マージ対象キーにも card_fill を追加
    for k in ("card_border", "bar_fill", "card_fill"):
        pal[k] = {**defaults[k], **(pal.get(k) or {})}
    return pal

# ---------- UI（薄い入口＋カード＋タイムライン） ----------

def render() -> None:
    st.subheader("ヘルス（収集健全性）")
    _inject_health_css()

    # 自動更新とウィンドウ
    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        auto = st.toggle("自動更新（このタブ）", value=False)
    with c2:
        win_label = st.selectbox("期間", ["5分", "10分", "30分", "60分"], index=1)
    window_s = {"5分": 300, "10分": 600, "30分": 1800, "60分": 3600}[win_label]

    if auto:
        st.caption("自動更新: 5秒ごと")
        time.sleep(5)
        _rerun = getattr(st, "experimental_rerun", None) or getattr(st, "rerun", None)
        if _rerun:
            _rerun()

    # データ取得
    try:
        h = read_health()
    except Exception as e:
        st.warning("Health 情報の取得に失敗しました。設定を確認してください。")
        W.emit("tab.health.read_error", level="WARN", feature="health", payload={"err": str(e)})
        return

    updated_at = getattr(h, "updated_at", None)
    counts = _get_counts(h)
    st.caption(f"updated_at: {updated_at or '-'} / OK={counts.get('OK',0)} WARN={counts.get('WARN',0)} CRIT={counts.get('CRIT',0)}")
    palette = _get_palette()

    items = list(_items_iter(h))
    if not items:
        st.info("status.json が見つからないか、対象エンドポイントが未登録です。")
        return

    # ★ 追加：並び替え＋プレースホルダ生成
    items, _order = _order_and_fill(items)

    # ---- カード（行×3列） ----
    per_row = 3
    for i in range(0, len(items), per_row):
        row = items[i : i + per_row]
        cols = st.columns(len(row))
        for c, iv in zip(cols, row):
            ex = f"{iv.get('exchange','?')}/{iv.get('topic','?')}"
            level = iv.get("level", "OK")
            age = iv.get("age_sec", None)
            retries = iv.get("retries", 0)
            cause = iv.get("cause") or "-"
            notes = iv.get("notes") or "-"

            placeholder = bool(iv.get("__placeholder__"))
            tone = (level or "OK").lower()
            border = palette["card_border"].get(tone, palette["card_border"]["ok"])
            fill   = palette["card_fill"].get(tone,  palette["card_fill"]["ok"])   # ← 追加

            with c:
                html = _card_html(
                    endpoint=ex,
                    level=level,
                    age_txt=_fmt_age(age),
                    retries=int(retries or 0),
                    cause=cause,
                    notes=notes,
                    border_color=border,
                    fill_color=fill,
                    placeholder=placeholder,
                )
                st.markdown(html, unsafe_allow_html=True)

    st.divider()

    # ---- タイムライン（1エンドポイント=1行の小さなバー）----
    st.write("タイムライン（右端=現在／右側の塗り＝未更新区間）")
    for iv in items:
        ex = f"{iv.get('exchange','?')}/{iv.get('topic','?')}"
        level = iv.get("level", "OK")
        age = iv.get("age_sec", None)
        st.markdown(f"**{ex}**")
        if iv.get("__placeholder__"):
            st.caption("未収集中")
            continue
        fig, ax = plt.subplots(figsize=(8, 0.35), dpi=150)
        _timeline(ax, level, age, window_s, palette)
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # ---- 詳細テーブル（簡易）----
    # DataFrame 依存を避け、Streamlitの自動テーブル化に任せる
    tbl: List[Dict[str, Any]] = []
    for iv in items:
        tbl.append({
            "endpoint": f"{iv.get('exchange','?')}/{iv.get('topic','?')}",
            "level": iv.get("level", "OK"),
            "age_sec": round(float(iv.get("age_sec") or 0.0), 3),
            "last_ok": iv.get("last_ok") or "-",
            "retries": int(iv.get("retries") or 0),
            "cause": iv.get("cause") or "-",
            "notes": iv.get("notes") or "-",
            "source": iv.get("source") or "-",
        })
    st.write(tbl)

    st.caption("※ 閾値や表示順は設定モーダル（⚙️）で調整。defaults→current の設計に準拠。")
