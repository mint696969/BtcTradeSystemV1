# path: ./tools/_btcts_bootstrap.py
# desc: tests/tools 用の btcts import bootstrap（PYTHONPATH 無しでも btcts_next/src を sys.path に追加）

from __future__ import annotations

import os
import sys
from pathlib import Path


def ensure_btcts_on_syspath() -> Path:
    """
    優先順位:
      1) env:BTCTS_SRC（btcts の src ディレクトリを直指定）
      2) env:BTC_TS_REPO_ROOT（repo root を指定）
      3) このファイル位置から repo root を推定（./tools 直下想定）

    追加対象:
      <repo_root>/btcts_next/src
    """
    env_src = os.environ.get("BTCTS_SRC")
    if env_src:
        p = Path(env_src).expanduser().resolve()
        if p.exists():
            _prepend_sys_path(p)
            return p

    env_repo = os.environ.get("BTC_TS_REPO_ROOT")
    if env_repo:
        repo = Path(env_repo).expanduser().resolve()
    else:
        repo = Path(__file__).resolve().parents[1]

    src = (repo / "btcts_next" / "src").resolve()
    if not src.exists():
        raise RuntimeError(f"btcts_next/src not found: {src}")

    _prepend_sys_path(src)
    return src


def _prepend_sys_path(p: Path) -> None:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
