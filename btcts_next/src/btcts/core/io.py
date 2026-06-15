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


def read_jsonl_tail(
    path: Path,
    *,
    max_lines: int = 200,
    max_bytes: int = 8 * 1024 * 1024,
) -> list[Dict[str, Any]]:
    """Read recent JSONL rows without loading the full append-only file.

    The previous implementation used ``readlines()[-max_lines:]``, which still
    read the whole file before slicing.  Health UI reads large audit logs on the
    render path, so this function must tail from the end with bounded bytes.

    If the file tail is unusually sparse or a line is extremely large, the
    returned row count may be smaller than ``max_lines``.  That is preferable to
    blocking UI render on a full-file scan.
    """
    if not path.exists():
        return []

    try:
        size = path.stat().st_size
    except Exception:
        return []

    if size <= 0:
        return []

    read_size = min(int(size), max(1024, int(max_bytes)))
    try:
        with open(path, "rb") as f:
            f.seek(max(0, int(size) - read_size))
            data = f.read(read_size)
    except Exception:
        return []

    if not data:
        return []

    if read_size < size:
        first_newline = data.find(bytes((10,)))
        if first_newline >= 0:
            data = data[first_newline + 1 :]

    try:
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []

    out: list[Dict[str, Any]] = []
    for line in lines[-max(1, int(max_lines)) :]:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out
