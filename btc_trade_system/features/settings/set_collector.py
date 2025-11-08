# path: btc_trade_system/features/settings/set_collector.py
# desc: Collector 登録の設定UI。唯一の正＝features/collector/config/endpoints_def.yaml を直接編集（atomic+fsync）

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Any, cast
import streamlit as st
from btc_trade_system.features.settings import ui_common as UI

# 監査（開発監査）
from btc_trade_system.features.audit_dev import writer as W  # dev_audit: logs/dev_audit.jsonl

# ---- 監査（標準ラッパ） --------------------------------------------------------
import time
from datetime import datetime

# セッション跨ぎでも安全に使える軽量メモ（Streamlit再実行に耐える）
_emit_state_key = "__settings_collector_emit_last"
_emit_last: Dict[str, float] = cast(Dict[str, float], st.session_state.setdefault(_emit_state_key, {}))

def _k(s: str) -> str:
    """設定タブ切替時に一括破棄できるよう set.collector.* に統一"""
    return f"set.collector.{s}"

def _emit(event: str, level: str = "INFO", feature: str = "settings", payload: Dict[str, Any] | None = None) -> None:
    """全監査イベントの共通フォーマット（ts/actor を必ず付与）"""
    try:
        base = {
            "ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "actor": "ui.settings.collector",   # どこ発かを固定で明示
        }
        if payload:
            base.update(payload)
        W.emit(event, level=level, feature=feature, payload=base)
    except Exception:
        pass

def _emit_throttled(key: str, event: str, level: str = "INFO", feature: str = "settings",
                    payload: Dict[str, Any] | None = None, min_interval_sec: float = 2.0) -> None:
    """多発しやすいイベントの間引き（UIの再実行で連打されないようガード）"""
    now = time.time()
    last = _emit_last.get(key, 0.0)
    if (now - last) >= min_interval_sec:
        _emit_last[key] = now
        _emit(event, level=level, feature=feature, payload=payload)

# 追加候補を保持（Streamlit 再実行に耐える簡易キュー）
_add_key = "set.collector.add_names"
if _add_key not in st.session_state:
    st.session_state[_add_key] = []  # List[str]

# YAML（PyYAML）
try:
    import yaml  # type: ignore
except Exception as e:
    raise RuntimeError("PyYAML is required. pip install pyyaml") from e

# ---- 定義ファイルの場所（唯一の正） ----
def _endpoints_yaml() -> Path:
    here = Path(__file__).resolve()
    return here.parents[2] / "features" / "collector" / "config" / "endpoints_def.yaml"

# ---- 安全書き込み（atomic + fsync） ----
def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

# ---- I/O ----
def _load_yaml() -> Dict[str, Any]:
    p = _endpoints_yaml()
    if not p.exists():
        return {"exchanges": []}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {"exchanges": []}

def _dump_yaml(obj: Dict[str, Any]) -> str:
    # 読みやすい順序で
    return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)

def _validate(values: Dict[str, Any]) -> List[str]:
    """保存直前に行う軽い検証（UIの入力ミスを弾く）。致命的でなければ保存は続行し、監査に載せる。"""
    errs: List[str] = []
    exs = values.get("exchanges", [])
    seen = set()
    for i, e in enumerate(exs):
        name = (e.get("name") or "").strip()
        if not name:
            errs.append(f"exchange[{i}]: name is empty")
            continue
        if name in seen:
            errs.append(f"exchange[{i}] '{name}': duplicated name")
        seen.add(name)

        rate = e.get("rate", {}) or {}
        max_rps = float(rate.get("max_rps", 0.0))
        burst = int(rate.get("burst", 1))
        if max_rps < 0:
            errs.append(f"{name}: max_rps negative -> {max_rps}")
        if burst < 1:
            errs.append(f"{name}: burst < 1 -> {burst}")

        eps = e.get("endpoints", []) or []
        ep_keys = [str(x.get("key", "")).strip() for x in eps]
        if any(not k for k in ep_keys):
            errs.append(f"{name}: endpoint key empty")
        if len(set(ep_keys)) != len(ep_keys):
            errs.append(f"{name}: endpoint keys duplicated -> {ep_keys}")
        for ep in eps:
            try:
                ti = float(ep.get("target_interval", 0.0))
                if ti and ti < 0.05:
                    errs.append(f"{name}:{ep.get('key')}: target_interval < 0.05s -> {ti}")
            except Exception:
                errs.append(f"{name}:{ep.get('key')}: target_interval invalid -> {ep.get('target_interval')}")
    return errs

# ---- UI 本体 ----
def render() -> Dict[str, Any]:
    """
    設定モーダルの 1 セクションとして呼ばれる想定。
    - 返り値: ユーザー操作を反映した dict（呼び出し側で保存ボタンを押したら commit() を呼ぶ）
    """
    data = _load_yaml()
    exs: List[Dict[str, Any]] = list(data.get("exchanges", []))

    st.subheader("取引所登録（Collector）")

    # 取引所 追加（テンプレ）
    with st.expander("＋ 取引所を追加（最小テンプレ）", expanded=False):
        c1, c2 = st.columns([3, 1])
        with c1:
            new_name = st.text_input("name（例: binance / bybit / okx など）", value="", key=_k("add_name"))
        with c2:
            if st.button("追加", use_container_width=True, key=_k("add_btn")) and new_name.strip():
                name = new_name.strip()
                known = {e.get("name") for e in exs}
                if name not in known and name not in st.session_state[_add_key]:
                    st.session_state[_add_key].append(name)
                    _emit("settings.collector.add.request", level="INFO",
                        payload={"name": name})

    # 追加要求を exs に反映（既存に無ければテンプレを append）
    for nm in list(st.session_state[_add_key]):
        if not any(e.get("name") == nm for e in exs):
            exs.append({
                "name": nm,
                "label": nm,
                "enabled": True,
                "rate": {"max_rps": 0.0, "burst": 1},
                "endpoints": []
            })
            _emit("settings.collector.add.staged", level="INFO",
                payload={"name": nm})

    if not exs:
        st.info("まだ登録がありません。bitflyer の定義を既定で用意しておくことを推奨します。")

    # 並び順（CSV）
    init_order = ",".join([e.get("name", "") for e in exs if e.get("name")])
    order_csv = st.text_input("並び順（カンマ区切り例: bitflyer,binance,bybit,okx）",
                              value=init_order, key=_k("order_csv"))
    order = [x.strip() for x in order_csv.split(",") if x.strip()]

    # 追加ステージ済みの name が order に無ければ末尾へ
    for nm in st.session_state[_add_key]:
        if nm not in order:
            order.append(nm)

    # 編集結果を収集
    new_list: List[Dict[str, Any]] = []
    to_remove_ex: List[str] = []

    for name in order:
        e = next((x for x in exs if x.get("name") == name), None)
        if not e:
            continue

        with st.container(border=True):
            st.markdown(f"#### {name}")
            top = st.columns([2, 1, 1, 1])
            # 有効/無効（運用スイッチ）
            enabled = top[0].toggle("enabled", value=bool(e.get("enabled", True)), key=_k(f"{name}.enabled"))
            label = top[1].text_input("表示ラベル", value=e.get("label", name), key=_k(f"{name}.label"))

            # レート（exchange レベル）
            max_rps = top[2].number_input("max_rps（0で無効）", min_value=0.0, step=1.0,
                                          value=float(e.get("rate", {}).get("max_rps", 0.0)),
                                          key=_k(f"{name}.rps"))
            burst = top[3].number_input("burst（>=1）", min_value=1, step=1,
                                        value=int(e.get("rate", {}).get("burst", 1)),
                                        key=_k(f"{name}.burst"))

            # エンドポイント一覧
            st.caption("エンドポイント（priority: 小さいほど高 / target_interval: 最小間隔[s]）")

            rm_ep_keys: List[str] = []
            for ep in e.get("endpoints", []):
                k = ep.get("key", "")
                c = st.columns([2, 1, 1, 1])
                c[0].text_input("key", value=k, key=_k(f"{name}.{k}.key"), disabled=True)
                ep["priority"] = c[1].number_input("priority", min_value=0, step=1,
                                                   value=int(ep.get("priority", 0)),
                                                   key=_k(f"{name}.{k}.prio"))
                ep["target_interval"] = c[2].number_input("target_interval", min_value=0.05, step=0.05,
                                                          value=float(ep.get("target_interval", 0.5)),
                                                          key=_k(f"{name}.{k}.intv"))
                # 念のためのクランプ（UIプロテクトに加えてサーバ側でも）
                try:
                    ep["priority"] = max(0, int(ep.get("priority", 0)))
                except Exception:
                    ep["priority"] = 0
                try:
                    ti_val = float(ep.get("target_interval", 0.5))
                    ep["target_interval"] = max(0.05, ti_val)
                except Exception:
                    ep["target_interval"] = 0.5

                if c[3].button("削除", key=_k(f"{name}.{k}.rm"), use_container_width=True):
                    rm_ep_keys.append(k)

            # 削除指示の反映
            if rm_ep_keys:
                e["endpoints"] = [x for x in e.get("endpoints", []) if x.get("key") not in rm_ep_keys]
                if rm_ep_keys:
                    _emit("settings.collector.endpoint.remove", level="INFO",
                        payload={"name": name, "keys": rm_ep_keys})

            # 操作ガイド
            st.caption("※ 削除はカード内のチェック＋削除ボタンで確定。保存後に反映されます。")

            # エンドポイント追加
            with st.popover("＋ エンドポイントを追加", use_container_width=True):
                add_cols = st.columns([2, 1, 1, 1])
                new_ep_key = add_cols[0].text_input("key（例: ticker）", value="", key=_k(f"{name}.new_ep.key"))
                new_ep_pri = add_cols[1].number_input("priority", min_value=0, step=1, value=0,
                                                      key=_k(f"{name}.new_ep.pri"))
                new_ep_intv = add_cols[2].number_input("target_interval", min_value=0.05, step=0.05, value=0.5,
                                                       key=_k(f"{name}.new_ep.intv"))
                if add_cols[3].button("追加", key=_k(f"{name}.new_ep.btn"), use_container_width=True) and new_ep_key.strip():
                    if not any(x.get("key") == new_ep_key for x in e.get("endpoints", [])):
                        e.setdefault("endpoints", []).append({
                            "key": new_ep_key.strip(),
                            "priority": int(new_ep_pri),
                            "target_interval": float(new_ep_intv),
                        })
                        _emit("settings.collector.endpoint.add", level="INFO",
                            payload={"name": name, "key": new_ep_key.strip()})

            # 取引所削除（安全側：チェック→ボタンの2段階）
            del_cols = st.columns([3, 1])
            del_ok = del_cols[0].checkbox("この取引所を削除する（確認）", value=False, key=_k(f"{name}.del.ck"))
            if del_cols[1].button("削除", key=_k(f"{name}.del.btn"), use_container_width=True) and del_ok:
                to_remove_ex.append(name)
                _emit("settings.collector.remove", level="WARN",
                    payload={"name": name})

            # 軽いクランプ（マイナス/不正を防止）
            max_rps = max(0.0, float(max_rps))
            burst = max(1, int(burst))

            # 反映
            e["label"] = label
            e["enabled"] = bool(enabled)
            e.setdefault("rate", {})["max_rps"] = float(max_rps)
            e.setdefault("rate", {})["burst"] = int(burst)

            # まだ削除指定されていないものだけ積む
            if name not in to_remove_ex:
                new_list.append(e)

    # 表に無い name は最後尾へ（削除指定されていない・未知 name は温存）
    tail = [e for e in exs if e.get("name") not in order and e.get("name") not in to_remove_ex]
    out = {"exchanges": new_list + tail}

    # 監査：プレビュー（件数と order の要約）
    try:
        summary = {
            "count": len(out["exchanges"]),
            "order": [e.get("name") for e in out["exchanges"]],
            "enabled": {e.get("name"): bool(e.get("enabled", True)) for e in out["exchanges"]},
            "removed": to_remove_ex,
        }
        _emit_throttled("preview", "settings.collector.preview", level="INFO",
                        payload=summary, min_interval_sec=2.0)
    except Exception:
        pass

    # タブ切替＝未保存破棄に対応：pending を set.collector.* に集約
    st.session_state["set.collector.pending"] = out

    # 実行ハンドラ（共通フッターから呼ばれる）
    def _exec_default() -> None:
        # 注意：collector のデフォルトは“空定義”
        _atomic_write_text(_endpoints_yaml(), _dump_yaml({"exchanges": []}))
        _emit("settings.collector.default.apply", level="WARN",
              payload={"path": str(_endpoints_yaml())})

    def _exec_save() -> None:
        vals = st.session_state.get("set.collector.pending", out)
        commit(vals)

    # === 共通フッター：閉じる／デフォルト／保存（確認ダイアログ＋即時反映つき） ===
    UI.render_section_controls(
        prefix="set.collector",
        on_default=_exec_default,
        on_save=_exec_save,
        key_base=_k("btn"),
        labels=("閉じる", "デフォルト", "保存"),
        confirm_message="Collector 定義を更新します。よろしいですか？"
    )

    # 呼び出し側（settings ハブ）で保存ボタンを押したら commit(out) を呼ぶ想定

    return out

def commit(values: Dict[str, Any]) -> None:
    """保存ボタンから呼ぶ。endpoints_def.yaml を atomic に更新（UIの並び順・削除を厳密に反映）"""
    cur = _load_yaml()
    before = list(cur.get("exchanges", []))
    after  = list(values.get("exchanges", []))  # ← UIが構築した順序・内容をそのまま採用

    # 監査用の差分要約を作る
    try:
        before_names = [e.get("name") for e in before if e.get("name")]
        after_names  = [e.get("name") for e in after  if e.get("name")]

        before_map = {e.get("name"): e for e in before if e.get("name")}
        after_map  = {e.get("name"): e for e in after  if e.get("name")}

        added   = sorted(list(set(after_names)  - set(before_names)))
        removed = sorted(list(set(before_names) - set(after_names)))

        changed_rates = {}
        changed_eps   = {}
        changed_keys  = []

        # enabled / label / rate / endpoints の代表的な差分を収集
        for name, new_e in after_map.items():
            old_e = before_map.get(name, {})
            diff = {}
            for k in ("enabled", "label", "rate", "endpoints"):
                if (new_e.get(k) or None) != (old_e.get(k) or None):
                    diff[k] = {"before": old_e.get(k), "after": new_e.get(k)}
            if diff:
                changed_keys.append(name)
                if "rate" in diff:
                    changed_rates[name] = {"before": diff["rate"]["before"], "after": diff["rate"]["after"]}
                if "endpoints" in diff:
                    try:
                        blen = len(diff["endpoints"]["before"] or [])
                    except Exception:
                        blen = None
                    try:
                        alen = len(diff["endpoints"]["after"] or [])
                    except Exception:
                        alen = None
                    changed_eps[name] = {"before_len": blen, "after_len": alen}

        # 軽いバリデーション（致命であればここで raise して保存中断しても良い）
        errs = _validate({"exchanges": after})
        if errs:
            _emit("settings.collector.commit.validation", level="WARN",
                  payload={"errors": errs[:20], "errors_total": len(errs)})

        payload = {
            "count_before": len(before_names),
            "count_after": len(after_names),
            "order_after": after_names,
            "added": added,
            "removed": removed,
            "changed_keys": changed_keys,
            "changed_rates": changed_rates,
            "changed_endpoints": changed_eps,
        }
        _emit("settings.collector.commit", level="INFO", payload=payload)
    except Exception:
        pass

    # 書き込みは UI から渡された after をそのまま正とする
    _atomic_write_text(_endpoints_yaml(), _dump_yaml({"exchanges": after}))
