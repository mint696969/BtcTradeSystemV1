# path: btc_trade_system/common/io_safe.py
# desc: 安全書き込み（tmp→置換 / JSONL append+fsync）と小さなユーティリティ

from __future__ import annotations
import os, io, json, tempfile, pathlib

_JSON_SEP = (",", ":")

def _fsync(fh) -> None:
    fh.flush()
    os.fsync(fh.fileno())

def write_atomic(path: str | os.PathLike, data: bytes) -> None:
    """
    バイナリ（bytes）を一時ファイルに書いてから原子的に置換。
    boost_svc.export_snapshot / export_handover_text が呼ぶ想定の互換I/F。
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # バイナリモードで安全に書き出し → fsync → 原子的置換
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent) as tf:
        tf.write(data)
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
