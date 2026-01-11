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
def file_lock(path: Path, *, timeout_sec: float = 10.0, poll_sec: float = 0.05) -> Iterator[None]:
    """クロスプロセスで使える簡易ロック。

    - portalocker があればそれを使う（Windows対応）。
    - 無ければ "排他用ファイルの原子的作成"（open('x')）で代替する。

    注意: 代替方式はプロセス異常終了時にロックファイルが残る可能性がある。
    その場合は timeout で諦める。
    """

    lock_path = Path(str(path) + ".lock")

    # portalocker がある場合
    try:
        import portalocker  # type: ignore

        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "a", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            try:
                yield
            finally:
                try:
                    portalocker.unlock(f)
                except Exception:
                    pass
        return
    except Exception:
        pass

    # fallback: lockfile create
    start = time.time()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                os.write(fd, f"pid={os.getpid()} ts={time.time()}\n".encode("utf-8"))
            finally:
                os.close(fd)
            break
        except FileExistsError:
            if (time.time() - start) >= timeout_sec:
                raise TimeoutError(f"lock timeout: {lock_path}")
            time.sleep(poll_sec)

    try:
        yield
    finally:
        try:
            lock_path.unlink(missing_ok=True)  # py3.8+
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
