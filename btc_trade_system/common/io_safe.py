# path: btc_trade_system/common/io_safe.py
# desc: 安全書き込み（tmp→置換 / JSONL append+fsync）と小さなユーティリティ
from __future__ import annotations
import os, io, json, tempfile, pathlib

_JSON_SEP = (",", ":")

def _fsync(fh) -> None:
    fh.flush()
    os.fsync(fh.fileno())

def write_atomic_text(path: str | os.PathLike, text: str, encoding="utf-8") -> None:
    """テキストを一時ファイルに書いてから原子的に置換。"""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding=encoding, newline="") as tf:
        tf.write(text)
        _fsync(tf)
        tmpname = tf.name
    os.replace(tmpname, path)

def append_jsonl(path: str | os.PathLike, obj: dict) -> None:
    """JSON Lines へ1行追記（ensure_ascii=False, separators=(',', ':'), fsync）。"""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    s = json.dumps(obj, ensure_ascii=False, separators=_JSON_SEP)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(s + "\n")
        _fsync(fh)
