# path: ./btc_trade_system/features/audit_dev/search.py
# desc: dev_audit.jsonl / audit.jsonl のテール抽出（Errors only など）をUIから呼べる非UIロジックに集約

from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import io, os, json

__all__ = [
    "tail_lines",
    "errors_only_tail",
]

# ---- 基本ユーティリティ：末尾から最大N行を文字列のまま取得 ----

def tail_lines(path: Path, limit: int = 200, encoding: str = "utf-8") -> List[str]:
    """ファイル末尾から最大 limit 行のテキストを返す（改行を除去）。
    - ファイルが無い/読めない場合は空配列。
    - JSONであるかどうかは気にしない（上位関数が解釈する）。
    """
    try:
        if not path.exists() or limit <= 0:
            return []
        # ざっくり・安全に：小さなチャンクで逆走
        # dev_audit は行単位JSONLなので 256KB で十分
        chunk = 256 * 1024
        size = path.stat().st_size
        buf = b""
        with open(path, "rb") as f:
            pos = size
            while pos > 0 and len(buf.splitlines()) <= limit * 1.2:
                read = min(chunk, pos)
                pos -= read
                f.seek(pos)
                buf = f.read(read) + buf
        text = buf.decode(encoding, errors="ignore")
        lines = text.splitlines()
        return lines[-limit:]
    except Exception:
        return []

# ---- Errors only tail ------------------------------------------------------

def _is_error_level(level: str | None) -> bool:
    if not level:
        return False
    lv = level.upper()
    return lv in {"ERR", "ERROR", "CRIT", "CRITICAL"}


def errors_only_tail(path: Path, limit: int = 200) -> List[str]:
    """dev_audit.jsonl の末尾から Errors/Critical のみを抽出して返す。
    - 行が JSON なら level フィールドで判定、非JSONの場合は文字列に 'ERROR'/'CRIT' を含むかで判定。
    - 返却は "そのまま画面に st.code('\n'.join(...)) できる文字列の配列"。
    """
    out: List[str] = []
    try:
        for s in tail_lines(path, limit=limit * 4):  # 余裕目に読んでから間引き
            s2 = s.strip()
            if not s2:
                continue
            keep = False
            try:
                obj = json.loads(s2)
                keep = _is_error_level(obj.get("level"))
            except Exception:
                # 非JSON行へのフォールバック
                us = s2.upper()
                keep = ("ERROR" in us) or ("CRIT" in us)
            if keep:
                out.append(s2)
            if len(out) >= limit:
                break
    except Exception:
        return []
    return out
