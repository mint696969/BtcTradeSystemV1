# path: btc_trade_system/features/settings/set_health.py
# desc: 「健全性」タブのUI（説明・SLOしきい値編集）。I/Oは settings_svc に委譲

from __future__ import annotations
import os
from pathlib import Path
import streamlit as st
import json  # ← PyYAMLが無いときのフォールバックで使用
from btc_trade_system.features.settings import settings_svc
# 既存プロバイダを利用して現在値を読む
from ..dash.providers import get_health_summary, _cfg_root

# YAML I/O（PyYAML）
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

def _ui_dir() -> Path:
    return _cfg_root() / "config" / "ui"

def _ensure_ui_dir() -> None:
    d = _ui_dir()
    d.mkdir(parents=True, exist_ok=True)

def _read_yaml(path: Path) -> dict:
    try:
        # settings_svc 側が相対/絶対どちらでも解決できる実装に委譲
        return settings_svc.load_yaml(str(path)) or {}
    except Exception:
        return {}


def _write_yaml(path: Path, data: dict) -> None:
    try:
        text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False) if yaml else json.dumps(data, ensure_ascii=False)
        settings_svc.write_atomic(str(path), text)
    except Exception as e:
        st.error(f"write failed: {e}")

def render():
    st.subheader("設定（健全性ビュー）")
    if yaml is None:
        st.error("PyYAML が見つかりません。 `pip install pyyaml` を実行してください。")
        return

    _ensure_ui_dir()
    ui_dir = _ui_dir()
    health_path = ui_dir / "health.yaml"
    mon_path    = ui_dir / "monitoring.yaml"

    # 現在の状況を取得（順序候補の源）
    s = get_health_summary()
    current_order = s.get("order", [])
    current_cards = [c["exchange"] for c in s.get("cards", [])]
    # health.yaml 既存内容
    y_health = _read_yaml(health_path)
    y_mon    = _read_yaml(mon_path)

    st.caption(f"設定ファイル: {health_path.name}, {mon_path.name}")

    # --- カード順の編集 ---
    st.markdown("### カード順（左→右）")
    default_order = y_health.get("order", current_order or current_cards)
    # 簡易UI：テキストで順序編集（カンマ区切り）
    order_text = st.text_input(
        "順序（カンマ区切り・例: binance,bybit,okx）",
        value=",".join(default_order),
        placeholder="binance,bybit,okx,bitflyer など"
    )
    new_order = [x.strip() for x in order_text.split(",") if x.strip()]

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
        age_warn = st.number_input("WARN（秒）", min_value=1, max_value=600, value=int(age.get("warn", 20)))
        age_crit = st.number_input("CRIT（秒）", min_value=1, max_value=600, value=int(age.get("crit", 30)))
    with colB:
        st.markdown("**レイテンシ（latency_ms）**")
        lat_warn = st.number_input("WARN（ms）", min_value=10, max_value=10000, value=int(lat.get("warn", 400)))
        lat_crit = st.number_input("CRIT（ms）", min_value=10, max_value=10000, value=int(lat.get("crit", 1200)))

    st.markdown("**SLO（最大許容スタレ）**")
    col1, col2, col3 = st.columns(3)
    with col1:
        slo_ticker_max = st.number_input("ticker.max_stale_s", min_value=1, max_value=3600, value=int(slo_ticker.get("max_stale_s", 5)))
    with col2:
        slo_ob_max = st.number_input("orderbook.max_stale_s", min_value=1, max_value=3600, value=int(slo_orderbook.get("max_stale_s", 6)))
    with col3:
        slo_trades_max = st.number_input("trades.max_stale_s", min_value=1, max_value=3600, value=int(slo_trades.get("max_stale_s", 5)))

    st.divider()

    # --- 保存 ---
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("順序を保存（health.yaml）", use_container_width=True):
            try:
                _write_yaml(health_path, {"order": new_order})
                st.success("カード順を保存しました。")
            except Exception as e:
                st.error(f"保存に失敗: {e}")
    with c2:
        if st.button("しきい値を保存（monitoring.yaml）", use_container_width=True):
            try:
                data = {
                    "health": {
                        "age_sec": {"ok": min(age_warn, age_crit), "warn": age_warn, "crit": age_crit},
                        "latency_ms": {"warn": lat_warn, "crit": lat_crit},
                        "require_all_ok": True,
                    },
                    "slo": {
                        "ticker": {"max_stale_s": slo_ticker_max},
                        "orderbook": {"max_stale_s": slo_ob_max},
                        "trades": {"max_stale_s": slo_trades_max},
                    },
                }
                _write_yaml(mon_path, data)
                st.success("しきい値を保存しました。")
            except Exception as e:
                st.error(f"保存に失敗: {e}")

    st.caption("※ 保存先はいずれも `config/ui/` 配下です。保存後、健全性タブに反映されます。")
