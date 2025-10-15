# path: ./btc_trade_system/features/dash/providers/health_order.py
# desc: Health の並び順を config/ui/health.yaml に保存・復元する最小I/F（YAMLは自前の超軽量実装）。

from __future__ import annotations
import os, tempfile, json
from pathlib import Path
from typing import List

from btc_trade_system.common import paths

HEALTH_YAML_REL = Path("ui") / "health.yaml"

def _ui_dir() -> Path:
    """
    config/ui へのルートを返す。
    - paths.config_dir() があればそれを使用
    - 無ければリポ直下の ./config を使う
    """
    try:
        base = paths.config_dir()  # type: ignore[attr-defined]
    except Exception:
        # フォールバック: カレント→./config
        base = Path("config")
    p = Path(base)
    (p / "ui").mkdir(parents=True, exist_ok=True)
    return p / "ui"

def _yaml_path() -> Path:
    return _ui_dir() / "health.yaml"

# ---- 超軽量 YAML 読み/書き（order: [a, b, c] だけ想定） ----------------------
def _dump_yaml_order(order: List[str]) -> str:
    # シンプル：order: の配下に - item の配列を書く
    lines = ["order:"]
    for it in order:
        lines.append(f"  - {it}")
    return "\n".join(lines) + "\n"

def _load_yaml_order(text: str) -> List[str]:
    # 「order:」セクションの - 行のみを抽出する超簡易パーサ
    order: List[str] = []
    in_order = False
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("order:"):
            in_order = True
            continue
        if in_order:
            if s.startswith("- "):
                order.append(s[2:].strip())
            elif s.startswith("#"):
                continue
            else:
                # order セクションを抜けた
                break
    # 重複除去（先勝ち）
    seen = set()
    uniq: List[str] = []
    for x in order:
        if x not in seen:
            uniq.append(x); seen.add(x)
    return uniq

# ---- Public API ---------------------------------------------------------------
def load_order() -> List[str]:
    """config/ui/health.yaml の order を読み込んで返す。無ければ空。"""
    p = _yaml_path()
    if not p.exists():
        return []
    try:
        txt = p.read_text(encoding="utf-8")
        return _load_yaml_order(txt)
    except Exception:
        return []

def save_order(order: List[str]) -> Path:
    """
    order を health.yaml に原子的に保存する。
    - 空要素/重複を除去して保存
    """
    cleaned = [x for x in order if isinstance(x, str) and x.strip()]
    # 先勝ちで重複除去
    seen = set()
    uniq: List[str] = []
    for x in cleaned:
        if x not in seen:
            uniq.append(x); seen.add(x)

    text = _dump_yaml_order(uniq)
    path = _yaml_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp = tempfile.mkstemp(prefix="health_", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
    return path
