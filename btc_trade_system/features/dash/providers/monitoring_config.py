# path: ./btc_trade_system/features/dash/providers/monitoring_config.py
# desc: monitoring.yaml（閾値/色/プリセット）を最小YAMLで保存/読込。UIからの保存/復元の入口。

from __future__ import annotations
import os, tempfile
from pathlib import Path
from typing import Dict, Any, Tuple

from btc_trade_system.common import paths

# 保存先: config/ui/monitoring.yaml
def _ui_dir() -> Path:
    try:
        base = paths.config_dir()  # type: ignore[attr-defined]
    except Exception:
        base = Path("config")
    p = Path(base) / "ui"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _yaml_path() -> Path:
    return _ui_dir() / "monitoring.yaml"

# ---- 既定値（不足分はこれで補完） ------------------------------------------
DEFAULTS: Dict[str, Any] = {
    "levels": {"OK": 0, "WARN": 1, "CRIT": 2},
    "thresholds": {
        # 代表例（UIから項目が増減しても map としてそのまま保存される）
        "latency_ms": {"warn": 500, "crit": 1500},
        "error_rate": {"warn": 0.01, "crit": 0.05},
    },
    "colors": {"OK": "#00B050", "WARN": "#FFC000", "CRIT": "#C00000"},
    "presets": {
        # UIの期間プリセット等（必要に応じ拡張）
        "lookbacks": ["15m", "1h", "6h", "24h", "7d"]
    },
}

# ---- 超軽量 YAML ダンプ（2段の mapping 想定） -------------------------------
def _dump_yaml(cfg: Dict[str, Any]) -> str:
    lines: list[str] = []
    def emit_map(prefix: str, m: Dict[str, Any]) -> None:
        lines.append(f"{prefix}:")
        for k, v in m.items():
            if isinstance(v, dict):
                lines.append(f"  {k}:")
                for k2, v2 in v.items():
                    lines.append(f"    {k2}: {v2}")
            elif isinstance(v, (list, tuple)):
                lines.append(f"  {k}:")
                for it in v:
                    lines.append(f"    - {it}")
            else:
                lines.append(f"  {k}: {v}")
    for top_key in ("levels", "thresholds", "colors", "presets"):
        if top_key in cfg and isinstance(cfg[top_key], dict):
            emit_map(top_key, cfg[top_key])
    return "\n".join(lines) + "\n"

# ---- 超軽量 YAML ロード（2段の mapping/配列のみを想定） --------------------
def _load_yaml(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    cur1: Tuple[str, Dict[str, Any]] | None = None
    cur2_key: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if not raw.startswith(" "):  # top level
            if ":" in raw:
                k = raw.split(":", 1)[0].strip()
                out.setdefault(k, {})
                cur1 = (k, out[k])  # type: ignore[index]
                cur2_key = None
            continue
        if raw.startswith("  - "):  # top-level list（今回は使わない想定）
            continue
        if raw.startswith("    "):
            # 第2階層（4スペース）
            if ":" in raw.strip():
                k2, v2 = [x.strip() for x in raw.strip().split(":", 1)]
                if cur1 and cur2_key:
                    cur1[1][cur2_key] = cur1[1].get(cur2_key, {})
                    if isinstance(cur1[1][cur2_key], dict):
                        cur1[1][cur2_key][k2] = _coerce(v2)
            elif raw.strip().startswith("- "):
                val = raw.strip()[2:].strip()
                if cur1 and cur2_key:
                    cur1[1][cur2_key] = cur1[1].get(cur2_key, [])
                    if isinstance(cur1[1][cur2_key], list):
                        cur1[1][cur2_key].append(_coerce(val))
            continue
        elif raw.startswith("  "):
            # 第1階層（2スペース）
            s = raw.strip()
            if ":" in s:
                k, v = [x.strip() for x in s.split(":", 1)]
                if v == "":  # section start (second level map or list)
                    if cur1:
                        cur1[1].setdefault(k, {})
                        cur2_key = k
                elif v.startswith("- "):  # list inline（簡易）
                    arr = [x.strip() for x in v.split("-")[1:] if x.strip()]
                    if cur1:
                        cur1[1][k] = arr
                        cur2_key = None
                else:
                    if cur1:
                        cur1[1][k] = _coerce(v)
                        cur2_key = None
            continue
    return out

def _coerce(s: str) -> Any:
    # 数値/小数/真偽をざっくり変換
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s

# ---- Public API ---------------------------------------------------------------
def load_config() -> Dict[str, Any]:
    """monitoring.yaml を読み込み、欠損は DEFAULTS で補完して返す。"""
    p = _yaml_path()
    if not p.exists():
        return DEFAULTS.copy()
    try:
        text = p.read_text(encoding="utf-8")
        cfg = _load_yaml(text)
        # 欠損補完（2階層まで）
        out = DEFAULTS.copy()
        for k, v in cfg.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                merged = out[k].copy()
                merged.update(v)
                out[k] = merged
            else:
                out[k] = v
        return out
    except Exception:
        return DEFAULTS.copy()

def save_config(cfg: Dict[str, Any]) -> Path:
    """
    cfg を monitoring.yaml に原子的保存。
    - 未指定キーは DEFAULTS で補完
    - 2階層までの dict/list/プリミティブをサポート
    """
    # DEFAULTS で補完
    merged = load_config()
    for k, v in cfg.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            m = merged[k].copy()
            m.update(v)
            merged[k] = m
        else:
            merged[k] = v

    text = _dump_yaml(merged)
    path = _yaml_path()
    fd, tmp = tempfile.mkstemp(prefix="monitoring_", suffix=".tmp", dir=str(path.parent))
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
