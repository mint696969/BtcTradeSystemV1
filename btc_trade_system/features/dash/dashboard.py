# path: ./btc_trade_system/features/dash/dashboard.py
# desc: ダッシュボード（ヘッダー＋タブのハブ）。tabs.yamlで並び順/有効化/初期タブを制御

from __future__ import annotations
import sys, pathlib, importlib
from typing import Callable, Dict, List
import yaml
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 基本設定
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_UI_DIR = REPO_ROOT / "btc_trade_system" / "config" / "ui"
TABS_CFG_PATH = CONFIG_UI_DIR / "tabs.yaml"  # defaultsはローダ側で結合予定

# V1ルートを sys.path に（保険）
sys.path.insert(0, str(REPO_ROOT))

# 設定モーダルの歯車（ロバスト・インポート）
try:
    _settings_mod = importlib.import_module("btc_trade_system.features.settings.ui_settings")
    settings_gear = getattr(_settings_mod, "settings_gear")
except Exception as e:
    import streamlit as st
    _settings_err_msg = f"設定UIの読み込みに失敗しました: {e}"
    def settings_gear(*_a, **_k):
        st.warning(_settings_err_msg)

# ユーティリティ
def _load_yaml(p: pathlib.Path) -> dict:
    try:
        with p.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.warning(f"設定ファイルの読み込みに失敗: {p.name} ({e})")
        return {}

def _resolve_tabs() -> Dict[str, dict]:
    """tabs.yaml を読み、order/enabled/initial を返す。欠損時は安全既定。"""
    cfg = _load_yaml(TABS_CFG_PATH)
    order: List[str] = cfg.get("order", ["main", "health", "audit"])
    enabled: Dict[str, bool] = cfg.get("enabled", {"main": True, "health": True, "audit": True})
    initial: str = cfg.get("initial", order[0] if order else "main")
    # enabled=False を除外
    active_keys = [k for k in order if enabled.get(k, True)]
    if not active_keys:
        active_keys = ["main"]
    # ラベル（最小辞書。i18nは後段で差し替え）
    labels_map = {
        "main": "メイン",
        "health": "コレクターの健全性",
        "audit": "開発監査",
    }
    labels = [labels_map.get(k, k) for k in active_keys]
    return {"order": active_keys, "labels": labels, "initial": initial}

def _import_renderer(tab_key: str) -> Callable[[], None]:
    """
    ui_<key>.py の render() を動的に取得。なければプレースホルダ。
    例: btc_trade_system.features.dash.ui_health.render
    """
    module_name = f"btc_trade_system.features.dash.ui_{tab_key}"
    try:
        mod = importlib.import_module(module_name)
        render = getattr(mod, "render")
        if callable(render):
            return render  # type: ignore
    except Exception:
        pass

    # フォールバック（main など未実装時）
    def _placeholder():
        st.info(f"「{tab_key}」タブのUIは未実装です。後続フェーズで実装します。")
    return _placeholder

# ─────────────────────────────────────────────────────────────
# ページレイアウト：ヘッダー（左タイトル・右歯車）＋タブ
st.set_page_config(page_title="BtcTS V1", layout="wide")

# ヘッダー：1行でコンパクトに（ヘッダー内限定スコープ #hdr）
st.markdown('<div id="hdr">', unsafe_allow_html=True)
left, right = st.columns([1, 0.08], gap="small")
with left:
    # タイトル上の余白を最小化
    st.markdown('<div style="margin-top:4px;"></div>', unsafe_allow_html=True)
    st.markdown("### BtcTradeSystem V1 ダッシュボード")
with right:
    # 歯車は右カラム内に戻す（スクロールバー有無でもズレない）
    st.markdown('<div id="gear-wrap">', unsafe_allow_html=True)
    settings_gear()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ヘッダー内だけのレイアウト安定化＆歯車ボタンのフラット化
st.markdown("""
<style>
  /* ページ幅のブレ防止（スクロールバー有無で横幅が変わらない） */
  :root { scrollbar-gutter: stable both-edges; }

  /* 右カラムは常に右寄せ・高さ一定で安定 */
  #hdr > div:nth-child(2) {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    min-height: 40px !important;
  }

  /* 歯車ボタンを極力フラットに（右カラム内限定） */
  #gear-wrap .stButton > button,
  #gear-wrap a[role='button'] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 6px 8px !important;
  }
  #gear-wrap .stButton > button:hover,
  #gear-wrap a[role='button']:hover {
    background: rgba(0,0,0,0.06) !important;
  }
</style>
""", unsafe_allow_html=True)

# タブ構築（tabs.yaml）
tabs_cfg = _resolve_tabs()
tab_keys: List[str] = tabs_cfg["order"]
tab_labels: List[str] = tabs_cfg["labels"]

# Streamlit タブの初期選択はAPI未提供のため、initial はロード時の並びに委ねる
# （将来：セッションステートで擬似初期選択を実装可）
tabs = st.tabs(tab_labels)

# レンダラを順番に呼ぶ
for i, key in enumerate(tab_keys):
    render = _import_renderer(key)
    with tabs[i]:
        render()
