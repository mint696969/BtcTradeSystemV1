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

def _mark_changed() -> None:
    # 入力変更時は「閉じるトリガ」を立てない（保存/既定ボタンのみで閉じる）
    st.session_state["__settings_changed"] = True  # 任意のフラグ（今は使わないが将来のUI制御に活用可）

def _exec_default():
    # 1) 既定へ戻す（差分=空）。atomic+fsync/監査は settings_svc 側で実施
    settings_svc.reset_to_default("health")
    settings_svc.reset_to_default("monitoring")

    # 2) このセクションの未保存データだけ破棄（モーダルは閉じない）
    UI.discard_prefix("set.health")
    # ★ pending もクリアして、前回の変更を持ち越さない
    st.session_state.pop("set.health.pending", None)

    # 3) ダッシュ側に「設定適用」を通知（再描画は settings/settings.py 側に任せる）
    st.session_state["_dash_require_rerun"] = True
    st.session_state.pop("__settings_changed", None)
    st.session_state["__settings_apply"] = True

def _exec_save():
    # 0) しきい値ガード（WARN < CRIT）
    try:
        th = (st.session_state.get("set.health.pending", {})
                              .get("monitoring", {})
                              .get("thresholds", {})
                              .get("age_sec", {}))
        w, c = th.get("warn"), th.get("crit")
        if isinstance(w, int) and isinstance(c, int) and w >= c:
            st.error("age_sec: WARN は CRIT より小さくしてください。", icon="⚠️")
            return
    except Exception:
        pass

    # 1) 保存（health.yaml / monitoring.yaml へ一括適用）
    n = apply_pending()

    # 2) このセクションの未保存データだけ破棄（次回オープンをクリーンに）
    UI.discard_prefix("set.health")

    # 3) ダッシュへ“即時反映”を通知（モーダルは閉じない）
    st.session_state.pop("__settings_changed", None)

    if n > 0:
        # 実際に何かしら書き込みがあった場合だけ、再描画＋適用フラグを立てる
        st.session_state["_dash_require_rerun"] = True
        st.session_state["__settings_apply"] = True

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

    # --- セクション切替（常にどれか1つだけ開く） ---
    section_options = ("thresholds", "order", "palette")
    section_labels = {
        "order": "カード順",
        "thresholds": "しきい値",
        "palette": "色パレット",
    }

    # st.radio 自身の state を単一ソースとして利用
    section = st.radio(
        "編集セクション",
        section_options,
        index=section_options.index("thresholds"),  # 初期は「しきい値」
        key="set.health.section",
        format_func=lambda k: section_labels.get(k, k),
        horizontal=True,
    )
    st.divider()

    # --- カード順の編集 ---
    DEFAULT_EXCH_ORDER: list[str] = ["bitflyer", "binance", "bybit", "okx"]
    current_order: list[str] = list(y_health.get("order") or [])
    default_order: list[str] = current_order or DEFAULT_EXCH_ORDER
    new_order = current_order or DEFAULT_EXCH_ORDER

    if section == "order":
        st.markdown("### カード順（左→右）")

        order_text = st.text_input(
            "順序（カンマ区切り・例: binance,bybit,okx）",
            value=",".join(default_order),
            placeholder="binance,bybit,okx,bitflyer など",
            key="set.health.order_text",
            on_change=_mark_changed,
        )

        new_order = [x.strip() for x in order_text.split(",") if x.strip()]
        if not new_order:
            new_order = DEFAULT_EXCH_ORDER

        st.divider()

    # --- しきい値（monitoring.yaml） ---
    if section == "thresholds":
        st.markdown("### しきい値")

        thresholds = (y_mon.get("thresholds") or {})

        # ① monitoring.thresholds.age_sec.* を優先
        age = thresholds.get("age_sec")
        # ② 無ければ health.age_thresholds_sec.* を見る
        if not isinstance(age, dict) or not age:
            age = y_health.get("age_thresholds_sec") or {}

        # レイテンシ：monitoring → health.latency_ms の順で参照
        lat = thresholds.get("latency_ms")
        if not isinstance(lat, dict) or not lat:
            lat = y_health.get("latency_ms") or {}

        # SLO：monitoring.slo → health.slo の順で参照
        slo = (y_mon.get("slo") or {})
        if not isinstance(slo, dict) or not slo:
            slo = (y_health.get("slo") or {})

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
                on_change=_mark_changed,
            )

            age_crit = st.number_input(
                "CRIT（秒）",
                min_value=1, max_value=600,
                value=int(age.get("crit", 30)),
                key="set.health.age_crit_s",
                on_change=_mark_changed,
            )

        with colB:
            st.markdown("**レイテンシ（latency_ms）**")
            lat_warn = st.number_input(
                "WARN（ms）",
                min_value=10, max_value=10000,
                value=int(lat.get("warn", 400)),
                key="set.health.lat_warn_ms",
                on_change=_mark_changed,
            )
            lat_crit = st.number_input(
                "CRIT（ms）",
                min_value=10, max_value=10000,
                value=int(lat.get("crit", 1200)),
                key="set.health.lat_crit_ms",
                on_change=_mark_changed,
            )

        st.markdown("**SLO（最大許容スタレ）**")
        col1, col2, col3 = st.columns(3)
        with col1:
            slo_ticker_max = st.number_input(
                "ticker.max_stale_s", min_value=1, max_value=3600,
                value=int(slo_ticker.get("max_stale_s", 5)),
                key="set.health.slo_ticker_max", on_change=_mark_changed,
            )
        with col2:
            slo_ob_max = st.number_input(
                "orderbook.max_stale_s", min_value=1, max_value=3600,
                value=int(slo_orderbook.get("max_stale_s", 6)),
                key="set.health.slo_ob_max", on_change=_mark_changed,
            )
        with col3:
            slo_trades_max = st.number_input(
                "trades.max_stale_s", min_value=1, max_value=3600,
                value=int(slo_trades.get("max_stale_s", 5)),
                key="set.health.slo_trades_max", on_change=_mark_changed,
            )

        st.divider()
    else:
        # セクション外でも pending を組み立てるための既定値
        thresholds = (y_mon.get("thresholds") or {})

        # age しきい値
        age = thresholds.get("age_sec")
        if not isinstance(age, dict) or not age:
            age = y_health.get("age_thresholds_sec") or {}

        # レイテンシ：monitoring → health.latency_ms の順で参照
        lat = thresholds.get("latency_ms")
        if not isinstance(lat, dict) or not lat:
            lat = y_health.get("latency_ms") or {}

        # SLO：monitoring.slo → health.slo の順で参照
        slo = (y_mon.get("slo") or {})
        if not isinstance(slo, dict) or not slo:
            slo = (y_health.get("slo") or {})

        slo_ticker    = (slo.get("ticker") or {})
        slo_orderbook = (slo.get("orderbook") or {})
        slo_trades    = (slo.get("trades") or {})

        # ここで UI 非表示時用の値をすべて決めておく
        age_warn = int(age.get("warn", 20))
        age_crit = int(age.get("crit", 30))

        lat_warn = int(lat.get("warn", 400))
        lat_crit = int(lat.get("crit", 1200))

        slo_ticker_max = int(slo_ticker.get("max_stale_s", 5))
        slo_ob_max     = int(slo_orderbook.get("max_stale_s", 6))
        slo_trades_max = int(slo_trades.get("max_stale_s", 5))

    # --- 色パレット（OK/WARN/CRIT） ---
    # 既存値（なければ既定）
    pal = (y_mon.get("palette") or {})
    if not isinstance(pal, dict) or not pal:
        pal = (y_health.get("palette") or {})

    card_border = (pal.get("card_border") or {})
    bar_fill    = (pal.get("bar_fill") or {})
    card_fill   = (pal.get("card_fill") or {})

    def _col(d: dict, k: str, default: str) -> str:
        v = d.get(k)
        if isinstance(v, str) and v.startswith("#") and len(v) in (4, 7):
            return v
        return default

    if section == "palette":
        st.markdown("### 色パレット（ヘルス表示用）")

        c1, c2 = st.columns(2)
        with c1:
            st.caption("カード枠（border-color）")
            cb_ok   = st.color_picker(
                "OK（カード枠）",
                _col(card_border, "ok", "#10b981"),
                key="set.health.cb_ok",
                on_change=_mark_changed,
            )
            cb_warn = st.color_picker(
                "WARN（カード枠）",
                _col(card_border, "warn", "#f59e0b"),
                key="set.health.cb_warn",
                on_change=_mark_changed,
            )
            cb_crit = st.color_picker(
                "CRIT（カード枠）",
                _col(card_border, "crit", "#ef4444"),
                key="set.health.cb_crit",
                on_change=_mark_changed,
            )

        with c2:
            st.caption("タイムライン/バー（塗り）")
            bf_ok   = st.color_picker(
                "OK（バー）",
                _col(bar_fill, "ok", "#d1fae5"),
                key="set.health.bf_ok",
                on_change=_mark_changed,
            )
            bf_warn = st.color_picker(
                "WARN（バー）",
                _col(bar_fill, "warn", "#fef3c7"),
                key="set.health.bf_warn",
                on_change=_mark_changed,
            )
            bf_crit = st.color_picker(
                "CRIT（バー）",
                _col(bar_fill, "crit", "#fee2e2"),
                key="set.health.bf_crit",
                on_change=_mark_changed,
            )

            st.caption("カード内側（背景）")
            cf1, cf2, cf3 = st.columns(3)
            cf_ok   = cf1.color_picker(
                "OK（背景）",
                _col(card_fill, "ok", "#ecfdf5"),
                key="set.health.cf_ok",
                on_change=_mark_changed,
            )
            cf_warn = cf2.color_picker(
                "WARN（背景）",
                _col(card_fill, "warn", "#fffbeb"),
                key="set.health.cf_warn",
                on_change=_mark_changed,
            )
            cf_crit = cf3.color_picker(
                "CRIT（背景）",
                _col(card_fill, "crit", "#fef2f2"),
                key="set.health.cf_crit",
                on_change=_mark_changed,
            )
    else:
        # セクションが「色パレット」以外のときは、UIは出さずに値だけ決めておく
        cb_ok   = _col(card_border, "ok",   "#10b981")
        cb_warn = _col(card_border, "warn", "#f59e0b")
        cb_crit = _col(card_border, "crit", "#ef4444")

        bf_ok   = _col(bar_fill, "ok",   "#d1fae5")
        bf_warn = _col(bar_fill, "warn", "#fef3c7")
        bf_crit = _col(bar_fill, "crit", "#fee2e2")

        cf_ok   = _col(card_fill, "ok",   "#ecfdf5")
        cf_warn = _col(card_fill, "warn", "#fffbeb")
        cf_crit = _col(card_fill, "crit", "#fef2f2")

    # --- 保存待ち（上部の「保存」で一括反映） ----------------------------
    # health_svc 側の読み取りに合わせ、monitoring.yaml は thresholds.* 配下へ集約
    pending = {
        "health": {
            "order": new_order,
            # health_svc 互換：既存の age_thresholds_sec.* も更新する
            "age_thresholds_sec": {
                "warn": float(age_warn),
                "crit": float(age_crit),
            },
            # レイテンシもしきい値として health 側に保持
            "latency_ms": {
                "warn": int(lat_warn),
                "crit": int(lat_crit),
            },
            # SLO もしっかり health.yaml 側に持たせる
            "slo": {
                "ticker":    {"max_stale_s": int(slo_ticker_max)},
                "orderbook": {"max_stale_s": int(slo_ob_max)},
                "trades":    {"max_stale_s": int(slo_trades_max)},
            },
            # 色パレットも health 側にミラー（UI 再表示用）
            "palette": {
                "card_border": {"ok": cb_ok, "warn": cb_warn, "crit": cb_crit},
                "bar_fill":    {"ok": bf_ok, "warn": bf_warn, "crit": bf_crit},
                "card_fill":   {"ok": cf_ok, "warn": cf_warn, "crit": cf_crit},
            },
        },
        "monitoring": {
            "thresholds": {
                "age_sec": {
                    # OK値は計算で決まるため書かない／WARN/CRITのみを保存
                    "warn": int(age_warn),
                    "crit": int(age_crit),
                },
                # monitoring 側にも latency_ms を持たせておく（将来の拡張用）
                "latency_ms": {
                    "warn": int(lat_warn),
                    "crit": int(lat_crit),
                },
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
        confirm_message="健全性設定を更新します。よろしいですか？",
        audit_tag=None  # success 監査は settings_svc 側のみ（最小監査）
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
    上部「保存」で呼ばれる想定。
    セッションに保管した pending を
      - health:      health.yaml
      - monitoring:  monitoring.yaml
    へ一括保存する。
    戻り値: 書き込みに成功したファイル数（0 / 1 / 2）
    """
    p = st.session_state.get("set.health.pending") or {}
    if not p:
        return 0

    wrote_health = False
    wrote_mon = False

    # 1) health.yaml（def+current をベースに pending.health をマージして保存）
    try:
        base_h = settings_svc.load_yaml("health") or {}
        merged_h = _deep_merge(base_h, p.get("health", {}) or {})
        # def との差分計算は settings_svc.force_save_yaml 側に任せる
        ok_h = getattr(settings_svc, "force_save_yaml", None)
        if callable(ok_h):
            wrote_health = bool(ok_h("health", merged_h))
        else:
            # フォールバック：旧 save_yaml を直接使う（差分ロジックに委譲）
            _write_yaml("health", merged_h)
            wrote_health = True
    except Exception as e:
        st.error(f"health.yaml の保存に失敗しました: {e}", icon="⚠️")
        wrote_health = False

    # 2) monitoring.yaml（def+current をベースに pending.monitoring をマージして保存）
    try:
        base_m = settings_svc.load_yaml("monitoring") or {}
        merged_m = _deep_merge(base_m, p.get("monitoring", {}) or {})
        ok_f = getattr(settings_svc, "force_save_yaml", None)
        if callable(ok_f):
            wrote_mon = bool(ok_f("monitoring", merged_m))
        else:
            _write_yaml("monitoring", merged_m)
            wrote_mon = True
    except Exception as e:
        st.error(f"monitoring.yaml の保存に失敗しました: {e}", icon="⚠️")
        wrote_mon = False

    # 保存に成功したら pending をクリア（次回オープンに持ち越さない）
    try:
        if (wrote_health or wrote_mon) and "set.health.pending" in st.session_state:
            del st.session_state["set.health.pending"]
    except Exception:
        pass

    return int(wrote_health) + int(wrote_mon)
