# path: ./btc_trade_system/features/dash/ui_health.py
# desc: Health タブ（収集健全性のサマリ表示＋タイムライン）。状態色は get_status() が返す4段階でヘッダーに連携。

from __future__ import annotations

import time
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import streamlit as st
import matplotlib.pyplot as plt

from btc_trade_system.features.audit_dev import writer as W
from btc_trade_system.features.health.health_svc import read_health, read_health_timeline
from btc_trade_system.features.health import health_order
from btc_trade_system.features.settings import settings_svc  # 追加

# --- btcts_next(新構成) への接続（遅延import） ----------------------------

def _btcts_src_dir() -> Path:
    # repo_root/btcts_next/src を想定
    # ui_health.py -> .../btc_trade_system/features/dash/ui_health.py
    # repo_root は 4つ上: dash -> features -> btc_trade_system -> repo_root
    here = Path(__file__).resolve()
    repo = here.parents[3]
    return repo / "btcts_next" / "src"

def _import_btcts_control():
    """
    btcts.collector.control を返す。
    import 失敗時は btcts_next/src を sys.path に追加して再試行する。
    """
    try:
        from btcts.collector import control as C  # type: ignore
        return C
    except Exception:
        p = _btcts_src_dir()
        if p.exists():
            sp = str(p)
            if sp not in sys.path:
                sys.path.insert(0, sp)
        from btcts.collector import control as C  # type: ignore
        return C

def _env_dirs_text() -> str:
    # 実運用で迷子になりやすいので、Healthタブに常に表示する
    data = os.environ.get("BTC_TS_DATA_DIR", "")
    logs = os.environ.get("BTC_TS_LOGS_DIR", "")
    cfg  = os.environ.get("BTC_TS_CONFIG_DIR", "")
    return f"DATA_DIR={data or '-'} / LOGS_DIR={logs or '-'} / CONFIG_DIR={cfg or '-'}"

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

def _build_rate_state(items: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    exchange ごとのレート状態を集約する。
    戻り値: {exchange: "none" | "soft" | "hard"}

    - topic=="rate" の item を対象とし、cause / level から判定する。
      cause: "rate_soft" / "rate_hard"（health_svc 側の仕様）
    - hard が一つでもあれば "hard"
    - hard が無く soft が一つでもあれば "soft"
    - それ以外は "none"
    """
    state: Dict[str, str] = {}
    for iv in items:
        if iv.get("topic") != "rate":
            continue
        ex = iv.get("exchange")
        if not ex:
            continue
        cause = (iv.get("cause") or "").lower()
        level = (iv.get("level") or "").upper()

        # 判定優先度: hard > soft
        if "rate_hard" in cause or level == "CRIT":
            state[ex] = "hard"
        elif "rate_soft" in cause or level == "WARN":
            # 既に hard が立っている場合は上書きしない
            if state.get(ex) != "hard":
                state[ex] = "soft"
        else:
            # 何も立てない（none 扱い）
            state.setdefault(ex, "none")
    return state

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

def render_collector_control() -> None:
    """
    Collector 状態表示＋起動/停止ボタン（btcts_next へ接続）
    - btcts.collector.control を使用
    - 出力先(DATA_DIR等)も併記して「今どこを見ているか」を固定表示
    """
    # まずENV表示（迷子防止）
    st.caption(_env_dirs_text())

    # btcts_next control を取得
    try:
        C = _import_btcts_control()
    except Exception as e:
        st.warning(f"btcts_next(control) の import に失敗: {e}")
        W.emit("ui.health.collector.import_fail", level="WARN", feature="health", payload={"err": str(e)})
        return

    # 状態取得（btcts.collector.control.status() を想定）
    try:
        stt = C.status()
        st_mode = getattr(stt, "mode", None) or "UNKNOWN"
        st_msg  = getattr(stt, "message", "") or ""
    except Exception as e:
        st.warning(f"collector status 読み取り失敗: {e}")
        W.emit("ui.health.collector.status_fail", level="WARN", feature="health", payload={"err": str(e)})
        st_mode = "UNKNOWN"
        st_msg = str(e)

    if str(st_mode).upper() == "RUNNING":
        badge_text = f"Collector RUNNING ({st_msg})"
        badge_color = "#2e7d32"
        button_label = "Collector 停止"
        will_start = False
    elif str(st_mode).upper() == "STOPPED":
        badge_text = "Collector STOPPED"
        badge_color = "#616161"
        button_label = "Collector 起動"
        will_start = True
    else:
        badge_text = f"Collector {st_mode}"
        badge_color = "#f9a825"
        button_label = "Collector 起動"
        will_start = True

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.9rem;">
              <span style="display:inline-block;width:0.6rem;height:0.6rem;border-radius:999px;background:{badge_color};"></span>
              <span>{badge_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _busy_key = "health.collector_toggle_busy"
    is_busy = bool(st.session_state.get(_busy_key))

    with col2:
        if st.button(
            button_label,
            key="collector_toggle",
            use_container_width=True,
            disabled=is_busy,
        ):
            st.session_state[_busy_key] = True
            try:
                if will_start:
                    with st.spinner("Collector を起動しています…"):
                        st2 = C.start()
                    st.toast("Collector を起動しました。", icon="✅")
                    W.emit("ui.health.collector.start", level="INFO", feature="health", payload={"result": repr(st2)})
                else:
                    with st.spinner("Collector を停止しています…"):
                        st2 = C.stop()
                    st.toast("Collector を停止しました。", icon="🛑")
                    W.emit("ui.health.collector.stop", level="INFO", feature="health", payload={"result": repr(st2)})

            except Exception as e:
                st.toast(f"Collector 操作に失敗: {e}", icon="⚠️")
                W.emit(
                    "ui.health.collector.toggle_error",
                    level="WARN",
                    feature="health",
                    payload={"err": str(e), "will_start": bool(will_start), "mode": str(st_mode)},
                )
            finally:
                st.session_state[_busy_key] = False

            _rerun = getattr(st, "experimental_rerun", None) or getattr(st, "rerun", None)
            if _rerun:
                _rerun()

# ---------- UI（薄い入口＋カード＋タイムライン） ----------

def render() -> None:
    st.subheader("ヘルス（収集健全性）")
    _inject_health_css()

    # 自動更新＋期間（左）と Collector 制御（右）を同じ行に配置
    left, right = st.columns([3, 2])

    with left:
        c1, c2 = st.columns([1.5, 1.0])
        with c1:
            auto = st.toggle("自動更新（このタブ）", value=False)
        with c2:
            # 1時間 / 24時間 / 10日 の 3択（デフォルトは 24時間）
            win_label = st.selectbox("期間", ["1時間", "24時間", "10日"], index=1)

    with right:
        # 既存の Collector 状態＋起動/停止ボタンを右側にまとめて表示
        render_collector_control()

    st.divider()

    window_s = {
        "1時間": 3600,          # 1h  =  1 * 3600
        "24時間": 86400,        # 24h = 24 * 3600
        "10日":  864000,        # 10d = 10 * 24 * 3600
    }[win_label]

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

    # 取引所ごとのレート状態（none / soft / hard）を事前に集約
    rate_state = _build_rate_state(items)

    # 並び替え＋プレースホルダ生成
    items, _order = _order_and_fill(items)

    # ---- カード（行×3列） ----
    per_row = 3
    for i in range(0, len(items), per_row):
        row = items[i : i + per_row]
        cols = st.columns(len(row))
        for c, iv in zip(cols, row):
            ex_name = iv.get("exchange", "?")
            topic = iv.get("topic", "?")
            ex = f"{ex_name}/{topic}"
            level = iv.get("level", "OK")
            age = iv.get("age_sec", None)
            retries = iv.get("retries", 0)
            cause = iv.get("cause") or "-"
            notes = iv.get("notes") or "-"

            placeholder = bool(iv.get("__placeholder__"))

            # 塗り（背景色）は「ヘルスレベル」に従う
            health_tone = (level or "OK").lower()
            fill = palette["card_fill"].get(health_tone, palette["card_fill"]["ok"])

            # 枠線は「レート状態」に従う（hard > soft > health）
            rs = rate_state.get(ex_name, "none")
            if rs == "hard":
                border_tone = "crit"
            elif rs == "soft":
                border_tone = "warn"
            else:
                border_tone = health_tone  # レート問題なし時はヘルスと揃える

            border = palette["card_border"].get(border_tone, palette["card_border"]["ok"])

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

    # ---- タイムライン（履歴ベース）----
    st.write(f"タイムライン（右端=現在／{win_label} の履歴）")

    try:
        timeline = read_health_timeline(window_s)
    except Exception as e:
        st.caption("タイムライン履歴の読み込みに失敗しました。")
        W.emit("tab.health.timeline_error", level="WARN", feature="health", payload={"err": str(e)})
        timeline = {}

    if not timeline:
        st.caption("履歴がありません（起動直後や collector 停止中など）。")
    else:
        for iv in items:
            ex_name = iv.get("exchange", "?")
            topic = iv.get("topic", "?")
            key = f"{ex_name}/{topic}"

            label = f"{ex_name}/{topic}"
            st.markdown(f"**{label}**")

            if iv.get("__placeholder__"):
                st.caption("未収集中")
                continue

            seq = timeline.get(key) or []
            if not seq:
                st.caption("この期間の履歴はありません。")
                continue

            # ポイント数が多すぎる場合は間引き（描画負荷の抑制）
            max_points = 200
            step = max(1, len(seq) // max_points)
            seq_s = seq[::step]

            xs_health: List[float] = []
            ys_health: List[float] = []
            colors_health: List[str] = []

            xs_rate: List[float] = []
            ys_rate: List[float] = []
            colors_rate: List[str] = []

            n = len(seq_s)
            if n == 1:
                # サンプルが1つだけなら、中央付近に1点だけ打つ
                xs_base = [window_s]
            else:
                xs_base = [window_s * i / (n - 1) for i in range(n)]

            for x, entry in zip(xs_base, seq_s):
                level = (entry.get("level") or "OK").lower()
                rate = entry.get("rate") or "none"

                # ヘルスレベル側（ベースの点）
                xs_health.append(x)
                ys_health.append(0.0)
                colors_health.append(palette["bar_fill"].get(level, palette["bar_fill"]["ok"]))

                # レート状態側（必要なら上書きの輪郭点）
                if rate and rate != "none":
                    xs_rate.append(x)
                    ys_rate.append(0.0)
                    if rate == "hard":
                        tone = "crit"
                    elif rate == "soft":
                        tone = "warn"
                    else:
                        tone = level
                    colors_rate.append(palette["card_border"].get(tone, palette["card_border"]["ok"]))

            fig, ax = plt.subplots(figsize=(8, 0.35), dpi=150)
            if xs_health:
                ax.scatter(xs_health, ys_health, s=10, c=colors_health)
            if xs_rate:
                # レート制御中のポイントは、輪郭付きの点として重ねる
                ax.scatter(xs_rate, ys_rate, s=30, facecolors="none", edgecolors=colors_rate, linewidths=0.8)

            ax.set_xlim(0, window_s)
            ax.set_yticks([])
            ax.set_xticks([])
            for s in ax.spines.values():
                s.set_visible(False)

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
