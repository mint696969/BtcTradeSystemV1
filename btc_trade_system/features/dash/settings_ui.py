# path: btc_trade_system/features/dash/settings_ui.py
# path: ./btc_trade_system/features/dash/settings_ui.py
# desc: 設定タブのUI（monitoring.yaml の閲覧/保存を svc_settings 経由で行う）

from __future__ import annotations
import json
from typing import Any, Callable, Tuple

# --- streamlit（無ければダミーで崩れないように） ---
try:
    import streamlit as st
except Exception:  # pragma: no cover
    import types as _t
    st = _t.SimpleNamespace(
        subheader=print, text_area=lambda *a, **k: "", button=lambda *a, **k: False,
        success=print, warning=print, error=print, info=print, caption=print, columns=lambda *a, **k: [None, None],
        write=print
    )

# --- yaml は任意（無ければ JSON で代替） ---
try:
    import yaml  # type: ignore
    def _to_text(obj: Any) -> str:
        return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)
    def _from_text(text: str) -> Any:
        return yaml.safe_load(text) if text.strip() else {}
except Exception:  # pragma: no cover
    def _to_text(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    def _from_text(text: str) -> Any:
        return json.loads(text) if text.strip() else {}

# --- svc_settings の API を多段で解決（名前差異に強く） ---
def _resolve_api() -> Tuple[Callable[[], Any], Callable[[Any], None]]:
    from importlib import import_module
    svc = import_module("btc_trade_system.features.dash.settings_svc")

    # 候補（load系 / save系）
    load_candidates = [
        "load_for_ui", "load", "load_monitoring", "read", "read_monitoring", "get_monitoring",
    ]
    save_candidates = [
        "save_from_ui", "save", "save_monitoring", "write", "write_monitoring", "put_monitoring",
    ]

    load_fn = None
    for name in load_candidates:
        fn = getattr(svc, name, None)
        if callable(fn):
            load_fn = fn
            break
    if load_fn is None:
        # 最低限のダミー
        def _load_stub():
            return {}
        load_fn = _load_stub

    save_fn = None
    for name in save_candidates:
        fn = getattr(svc, name, None)
        if callable(fn):
            save_fn = fn
            break
    if save_fn is None:
        def _save_stub(_obj: Any) -> None:
            raise RuntimeError("svc_settings に保存用APIが見つかりません")
        save_fn = _save_stub

    return load_fn, save_fn

def render():
    st.subheader("設定（monitoring.yaml）")
    load_fn, save_fn = _resolve_api()

    # 読み込み（dict/obj/None どれでもテキスト化）
    try:
        cfg = load_fn()
    except Exception as e:
        st.warning(f"設定の読み込みに失敗しました: {e}")
        cfg = {}

    text = _to_text(cfg if isinstance(cfg, (dict, list)) else (cfg or {}))
    text = st.text_area("設定（YAML / JSON）", text, height=360)

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("保存", use_container_width=True):
            try:
                obj = _from_text(text)
                save_fn(obj)
                st.success("保存しました。")
            except Exception as e:
                st.error(f"保存に失敗しました: {e}")

    with c2:
        if st.button("再読込", use_container_width=True):
            try:
                cfg2 = load_fn()
                st.info("読み込み完了。下のプレビューに反映しています。")
                st.write(cfg2)
            except Exception as e:
                st.error(f"再読込に失敗しました: {e}")


