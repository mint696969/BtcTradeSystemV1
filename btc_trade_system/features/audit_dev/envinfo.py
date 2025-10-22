# path: ./btc_trade_system/features/audit_dev/envinfo.py
# desc: 環境・バージョン・ファイル概要のユーティリティ（UIから呼ぶだけにするための非UIロジック）

from __future__ import annotations
from pathlib import Path
import hashlib, platform, sys

def mask_env_items(env: dict) -> list[tuple[str, str]]:
    """環境変数をキー名でマスク。KEY/SECRET/TOKEN/PASS/PWD を含むものは伏字。"""
    def _mask(k: str, v: str) -> str:
        key = k.upper()
        if any(p in key for p in ("KEY", "SECRET", "TOKEN", "PASS", "PWD")):
            return "***"
        return v
    items = [(k, _mask(k, v)) for k, v in env.items()]
    return sorted(items, key=lambda kv: kv[0])

def collect_versions() -> list[str]:
    """Python / Streamlit / 主要ライブラリ / OS の簡易バージョン列挙。"""
    out: list[str] = []
    out.append(f"- python: {sys.version.split()[0]}")
    try:
        import streamlit as _st  # type: ignore
        out.append(f"- streamlit: {getattr(_st, '__version__', 'unknown')}")
    except Exception:
        out.append("- streamlit: unknown")
    for lib in ("pandas", "numpy", "requests"):
        try:
            mod = __import__(lib)
            ver = getattr(mod, "__version__", "unknown")
            out.append(f"- {lib}: {ver}")
        except Exception:
            pass
    out.append(f"- platform: {platform.platform()}")
    out.append(f"- os: {platform.system()} {platform.release()} ({platform.version()})")
    return out

def fmt_bytes(n: int) -> str:
    """人間可読のサイズ表記。"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n //= 1024
    return f"{n:.0f}PB"

def fmt_iso(ts: float) -> str:
    """UNIX秒をUTC ISO8601 Z に整形。"""
    import datetime as _dt
    try:
        return _dt.datetime.utcfromtimestamp(ts).isoformat(timespec="seconds") + "Z"
    except Exception:
        return str(ts)

def list_files_brief(root: Path, limit: int = 100) -> list[str]:
    """直下ファイルのサイズ・mtime を列挙（最大 limit 行）。"""
    rows: list[tuple[str, int, float]] = []
    try:
        for p in list(root.glob("*"))[:limit]:
            try:
                if p.is_file():
                    stt = p.stat()
                    rows.append((str(p), stt.st_size, stt.st_mtime))
            except Exception:
                continue
    except Exception:
        pass
    rows.sort(key=lambda t: t[2], reverse=True)
    return [f"- {Path(path).name} ({fmt_bytes(sz)}, mtime={fmt_iso(mt)})" for path, sz, mt in rows[:limit]]

def sha256_file(p: Path) -> str | None:
    """ファイルのSHA256（失敗時 None）。"""
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None
