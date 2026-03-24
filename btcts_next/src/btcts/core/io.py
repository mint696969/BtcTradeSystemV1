# path: ./btcts_next/src/btcts/core/io.py
# desc: 原子的I/O（atomic write/replace）とJSON/YAML/JSONLの読み書き、および簡易ファイルロックを提供する。

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional


try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


# ---- locking -----------------------------------------------------------------


@contextmanager
def file_lock(target_path: Path, *, timeout_sec: float = 10.0, stale_sec: float = 60.0) -> Iterator[None]:
    """
    排他用のロックファイルを作ってロックする。

    - target_path が ".../x.json" なら lock は ".../x.json.lock"
    - 既存 lock が stale_sec より古ければ回収（削除）して取り直す
    """
    lock_path = Path(str(target_path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + float(timeout_sec)

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                msg = f"pid={os.getpid()} ts={time.time()}\n"
                os.write(fd, msg.encode("utf-8", errors="replace"))
                os.fsync(fd)
            finally:
                os.close(fd)
            break

        except FileExistsError:
            # stale 判定：mtime が古い lock は回収する
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age >= float(stale_sec):
                    lock_path.unlink(missing_ok=True)
                    continue
            except Exception:
                pass

            if time.time() >= deadline:
                raise TimeoutError(f"lock timeout: {lock_path}")

            time.sleep(0.05)

    try:
        yield
    finally:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass


# ---- atomic write -------------------------------------------------------------


def _atomic_replace(tmp_path: Path, final_path: Path) -> None:
    """同一ファイルシステム内で原子的に置換する。"""
    tmp_path.replace(final_path)


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8", newline: str = "\n") -> None:
    """テキストを原子的に書き込む。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with open(tmp, "w", encoding=encoding, newline=newline) as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    _atomic_replace(tmp, path)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """バイナリを原子的に書き込む。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    _atomic_replace(tmp, path)


# ---- json --------------------------------------------------------------------


def read_json(path: Path, *, default: Optional[Any] = None) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, obj: Any, *, indent: int = 2, sort_keys: bool = True) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=indent, sort_keys=sort_keys) + "\n"
    atomic_write_text(path, text)


# ---- yaml --------------------------------------------------------------------


def _require_yaml() -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is required for YAML operations")


def read_yaml(path: Path, *, default: Optional[Any] = None) -> Any:
    if not path.exists():
        return default
    _require_yaml()
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)  # type: ignore


def write_yaml(path: Path, obj: Any) -> None:
    _require_yaml()
    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)  # type: ignore
    if not text.endswith("\n"):
        text += "\n"
    atomic_write_text(path, text)


# ---- jsonl -------------------------------------------------------------------


def append_jsonl(path: Path, row: Dict[str, Any], *, fsync_each: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)
        f.flush()
        if fsync_each:
            os.fsync(f.fileno())


def read_jsonl_tail(path: Path, *, max_lines: int = 200) -> list[Dict[str, Any]]:
    """簡易 tail（大きすぎるファイル向けの最適化は別途）。"""
    if not path.exists():
        return []
    out: list[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f.readlines()[-max_lines:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out
