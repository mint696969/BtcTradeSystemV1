# path: btc_trade_system/features/settings/set_health.py
# desc: 「健全性」タブのUI（説明・SLOしきい値編集）。I/Oは settings_svc に委譲

from __future__ import annotations
import streamlit as st
from btc_trade_system.features.settings import settings_svc
from btc_trade_system.features.settings import ui_common as UI

# YAML I/O（PyYAML）
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

def _read_yaml(area: str) -> dict:
    try:
        return settings_svc.load_yaml(area) or {}
    except Exception:
        return {}

def _write_yaml(area: str, data: dict) -> None:
    try:
        # settings_svc 側で atomic+fsync / dev_audit emit まで面倒を見てくれる
        settings_svc.save_yaml(area, data)
    except Exception as e:
        st.error(f"write failed: {e}")

def _mark_dirty() -> None:
    st.session_state["__settings_dirty"] = True

def _exec_default():
    settings_svc.reset_to_default("health")
    settings_svc.reset_to_default("monitoring")

def _exec_save():
    n = apply_pending()
    if n == 0:
        st.toast("変更はありませんでした", icon="ℹ️")

def render():
    st.subheader("設定（健全性ビュー）")
    if yaml is None:
        st.error("PyYAML が見つかりません。 `pip install pyyaml` を実行してください。")
        return

    HEALTH_AREA = "health"
    MON_AREA    = "monitoring"

    # 実際の def/current のパス（settings_svc 側の単一ソースに合わせる）
    def_h, act_h = settings_svc.get_paths(HEALTH_AREA)
    def_m, act_m = settings_svc.get_paths(MON_AREA)

    y_health = _read_yaml(HEALTH_AREA)
    y_mon    = _read_yaml(MON_AREA)

    st.caption(
        f"適用対象（外部CONFIG）: {act_h.name}, {act_m.name} ／ 既定: {def_h.name}, {def_m.name}"
    )

    # --- カード順の編集 ---
    st.markdown("### カード順（左→右）")
    # order の既存値が無い場合のフォールバック（表示を空にしないため）
    DEFAULT_EXCH_ORDER: list[str] = ["bitflyer", "binance", "bybit", "okx"]
    current_order: list[str] = list(y_health.get("order") or [])
    default_order: list[str] = current_order or DEFAULT_EXCH_ORDER

    # 簡易UI：テキストで順序編集（カンマ区切り）
    order_text = st.text_input(
        "順序（カンマ区切り・例: binance,bybit,okx）",
        value=",".join(default_order),
        placeholder="binance,bybit,okx,bitflyer など",
        key="set.health.order_text",
        on_change=_mark_dirty,
    )

    new_order = [x.strip() for x in order_text.split(",") if x.strip()]

    if not new_order:
        new_order = DEFAULT_EXCH_ORDER

    st.divider()

    # --- しきい値（monitoring.yaml） ---
    st.markdown("### しきい値")
    # health.age_sec
    h = (y_mon.get("health") or {})
    age = h.get("age_sec") or {}
    lat = h.get("latency_ms") or {}
    slo = (y_mon.get("slo") or {})
    slo_ticker = (slo.get("ticker") or {})
    slo_orderbook = (slo.get("orderbook") or {})
    slo_trades = (slo.get("trades") or {})

    colA, colB = st.columns(2)
    with colA:
        st.markdown("**データ鮮度（age_sec）**")
        age_warn = st.number_input(
            "WARN（秒）",
            min_value=1, max_value=600,
            value=int(age.get("warn", 20)),
            key="set.health.age_warn_s",
            on_change=_mark_dirty,
        )

        age_crit = st.number_input(
            "CRIT（秒）",
            min_value=1, max_value=600,
            value=int(age.get("crit", 30)),
            key="set.health.age_crit_s",
            on_change=_mark_dirty,
        )

    with colB:
        st.markdown("**レイテンシ（latency_ms）**")
        lat_warn = st.number_input(
            "WARN（ms）",
            min_value=10, max_value=10000,
            value=int(lat.get("warn", 400)),
            key="set.health.lat_warn_ms",
            on_change=_mark_dirty,
        )
        lat_crit = st.number_input(
            "CRIT（ms）",
            min_value=10, max_value=10000,
            value=int(lat.get("crit", 1200)),
            key="set.health.lat_crit_ms",
            on_change=_mark_dirty,
        )

    st.markdown("**SLO（最大許容スタレ）**")
    col1, col2, col3 = st.columns(3)
    with col1:
        slo_ticker_max = st.number_input(
            "ticker.max_stale_s", min_value=1, max_value=3600,
            value=int(slo_ticker.get("max_stale_s", 5)),
            key="set.health.slo_ticker_max", on_change=_mark_dirty,
        )
    with col2:
        slo_ob_max = st.number_input(
            "orderbook.max_stale_s", min_value=1, max_value=3600,
            value=int(slo_orderbook.get("max_stale_s", 6)),
            key="set.health.slo_ob_max", on_change=_mark_dirty,
        )
    with col3:
        slo_trades_max = st.number_input(
            "trades.max_stale_s", min_value=1, max_value=3600,
            value=int(slo_trades.get("max_stale_s", 5)),
            key="set.health.slo_trades_max", on_change=_mark_dirty,
        )

    st.divider()

    # --- 色パレット（OK/WARN/CRIT） ---
    st.markdown("### 色パレット（ヘルス表示用）")

    # 既存値（なければ既定）
    pal = (y_mon.get("palette") or {})
    card_border = (pal.get("card_border") or {})
    bar_fill    = (pal.get("bar_fill") or {})
    card_fill   = (pal.get("card_fill") or {})   # ← add

    def _col(d: dict, k: str, default: str) -> str:
        v = d.get(k)
        if isinstance(v, str) and v.startswith("#") and len(v) in (4, 7):
            return v
        return default

    c1, c2 = st.columns(2)
    with c1:
        st.caption("カード枠（border-color）")
        cb_ok   = st.color_picker("OK（カード枠）",   _col(card_border, "ok",   "#10b981"), key="set.health.cb_ok",   on_change=_mark_dirty)   # teal-ish
        cb_warn = st.color_picker("WARN（カード枠）", _col(card_border, "warn", "#f59e0b"),  key="set.health.cb_warn", on_change=_mark_dirty)  # amber
        cb_crit = st.color_picker("CRIT（カード枠）", _col(card_border, "crit", "#ef4444"),  key="set.health.cb_crit", on_change=_mark_dirty)  # red
    with c2:
        st.caption("タイムライン/バー（塗り）")
        bf_ok   = st.color_picker("OK（バー）",   _col(bar_fill, "ok",   "#d1fae5"), key="set.health.bf_ok",   on_change=_mark_dirty)  # light green
        bf_warn = st.color_picker("WARN（バー）", _col(bar_fill, "warn", "#fef3c7"), key="set.health.bf_warn", on_change=_mark_dirty)  # light amber
        bf_crit = st.color_picker("CRIT（バー）", _col(bar_fill, "crit", "#fee2e2"), key="set.health.bf_crit", on_change=_mark_dirty)  # light red
        # カード内側（背景）の色
        st.caption("カード内側（背景）")
        cf1, cf2, cf3 = st.columns(3)
        cf_ok   = cf1.color_picker("OK（背景）",   _col(card_fill, "ok",   "#ecfdf5"), key="set.health.cf_ok",   on_change=_mark_dirty)
        cf_warn = cf2.color_picker("WARN（背景）", _col(card_fill, "warn", "#fffbeb"), key="set.health.cf_warn", on_change=_mark_dirty)
        cf_crit = cf3.color_picker("CRIT（背景）", _col(card_fill, "crit", "#fef2f2"), key="set.health.cf_crit", on_change=_mark_dirty)

    # --- 保存待ち（上部の「保存」で一括反映） ----------------------------
    # health_svc 側の読み取りに合わせ、monitoring.yaml は thresholds.* 配下へ集約
    pending = {
        "health": {"order": new_order},
        "monitoring": {
            "thresholds": {
                "default": {
                    "age_sec": {
                        # OK値は計算で決まるため書かない／WARN/CRITのみを保存
                        "warn": int(age_warn),
                        "crit": int(age_crit),
                    },
                    # latency_ms は現段階で health_svc の参照外なので保存対象から外す
                }
            },
            "slo": {
                "ticker":     {"max_stale_s": int(slo_ticker_max)},
                "orderbook":  {"max_stale_s": int(slo_ob_max)},
                "trades":     {"max_stale_s": int(slo_trades_max)},
            },
            "palette": {
                "card_border": {"ok": cb_ok, "warn": cb_warn, "crit": cb_crit},
                "bar_fill":    {"ok": bf_ok, "warn": bf_warn, "crit": bf_crit},
                "card_fill":   {"ok": cf_ok, "warn": cf_warn, "crit": cf_crit},
            },
        },
    }

    if age_warn >= age_crit:
        st.warning("※ age_sec: WARN は CRIT より小さくしてください。", icon="⚠️")

    # pending を上書きせず追記マージ（保存直前の再実行でも失われない）
    _old = st.session_state.get("set.health.pending", {})

    st.session_state["set.health.pending"] = _deep_merge(_old or {}, pending)

    # === セクション専用ボタン（閉じる／デフォルト／保存） ===
    UI.render_section_controls(
        prefix="set.health",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base="set.health.btn",
        labels=("閉じる","デフォルト","保存"),
        confirm_message="健全性設定を更新します。よろしいですか？"
    )

def _deep_merge(dst: dict, src: dict) -> dict:
    """dict を再帰マージ（src優先）。"""
    from collections.abc import Mapping
    for k, v in (src or {}).items():
        if isinstance(v, Mapping) and isinstance(dst.get(k), Mapping):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def apply_pending() -> int:

    """
    上部「保存」で呼ばれる想定。セッションに保管した pending を health.yaml / monitoring.yaml へ一括保存。
    戻り値: 書き込んだファイル数（0/1/2）
    """
    p = st.session_state.get("set.health.pending")
    if not p:
        return 0

    # 1) health.yaml（order のみ）
    try:
        _write_yaml("health", p["health"])
        wrote_health = True
    except Exception:
        wrote_health = False

    # 2) monitoring.yaml（既存を残しつつマージ保存）
    try:
        current = _read_yaml("monitoring")
        merged  = _deep_merge(current or {}, p["monitoring"])
        _write_yaml("monitoring", merged)
        wrote_mon = True
    except Exception:
        wrote_mon = False

    # 保存に成功したら pending をクリア（次保存に持ち越さない）
    try:
        if (wrote_health or wrote_mon) and "set.health.pending" in st.session_state:
            del st.session_state["set.health.pending"]
    except Exception:
        pass

    return int(wrote_health) + int(wrote_mon)
