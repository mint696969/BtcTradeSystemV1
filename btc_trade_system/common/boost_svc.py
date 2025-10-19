# path: btc_trade_system/common/boost_svc.py
# desc: BOOSTモード用スナップショット（構造/環境/直近監査）を logs/boost_snapshot.json に上書き出力（10秒レート制御）

from __future__ import annotations
import os
import json
import importlib
import pkgutil
import time
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Tuple

from btc_trade_system.common import paths, io_safe

# --- レート制御（プロセス内） ---
_LAST_WRITE_MS: float | None = None
_RATE_MS = 10_000  # 10 秒


def _utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _list_modules(root_pkg: str) -> List[str]:
    """主要層までのモジュール名だけ列挙して重さを避ける"""
    mods: List[str] = []
    try:
        pkg = importlib.import_module(root_pkg)
        for m in pkgutil.walk_packages(pkg.__path__, prefix=root_pkg + "."):
            if m.name.count(".") <= 4:
                mods.append(m.name)
    except Exception:
        pass
    return mods


def _tail_jsonl(path: Path, n: int) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:]
    except Exception:
        return []
    out: List[Dict[str, Any]] = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out


def _list_tree(base: Path, *, max_depth: int = 2, max_entries: int = 200) -> Dict[str, Any]:
    """
    data/ と logs/ の“薄い”ツリー。深さ/件数を厳しめに打ち切る。
    返り値は {root: str, entries: [(relpath, 'd'|'f', size_or_0)]}
    """
    entries: List[Tuple[str, str, int]] = []
    base = Path(base)
    try:
        for root, dirs, files in os.walk(base):
            rel_root = str(Path(root).relative_to(base))
            depth = 0 if rel_root == "." else rel_root.count(os.sep) + 1
            if depth > max_depth:
                # 深すぎる階層は切る
                dirs[:] = []
                continue
            # ディレクトリ
            for d in list(dirs):
                rel = str(Path(rel_root) / d) if rel_root != "." else d
                entries.append((rel.replace("\\", "/"), "d", 0))
                if len(entries) >= max_entries:
                    raise StopIteration
            # ファイル（サイズは最小限）
            for f in files:
                rel = str(Path(rel_root) / f) if rel_root != "." else f
                try:
                    sz = (Path(root) / f).stat().st_size
                except Exception:
                    sz = 0
                entries.append((rel.replace("\\", "/"), "f", int(sz)))
                if len(entries) >= max_entries:
                    raise StopIteration
    except StopIteration:
        pass
    except Exception:
        pass
    return {"root": str(base), "entries": entries}


def make_snapshot() -> Dict[str, Any]:
    data_root = paths.data_dir()
    logs_root = paths.logs_dir()
    snapshot: Dict[str, Any] = {
        "ts": _utc_iso(),
        "env": {
            "BTC_TS_MODE": os.getenv("BTC_TS_MODE"),
            "PYTHON": os.getenv("PYTHON") or os.getenv("VIRTUAL_ENV"),
            "PYTHONPATH_contains_repo": any(
                str(p).endswith("BtcTradeSystemV1")
                for p in filter(None, os.getenv("PYTHONPATH", "").split(os.pathsep))
            ),
        },
        "roots": {"data_root": str(data_root), "logs_root": str(logs_root)},
        "tree": {
            "data": _list_tree(Path(data_root)),
            "logs": _list_tree(Path(logs_root)),
        },
        "modules": _list_modules("btc_trade_system"),
        "recent": {
            "audit_tail": _tail_jsonl(Path(logs_root) / "audit.jsonl", 50),
            "dev_audit_tail": _tail_jsonl(Path(logs_root) / "dev_audit.jsonl", 50),
        },
    }
    return snapshot


def export_snapshot(out_path: Path | None = None, *, force: bool = False) -> str:
    """
    logs/boost_snapshot.json を生成（原子的上書き）。
    - BOOST切替直後は force=True で即出力
    - 以降は 10 秒以内の連続生成をスキップ
    戻り値: 生成（または既存）ファイルのフルパス（str）
    例外: I/O 系は OSError に統一して送出（UI側でトレース可能にする）
    """
    global _LAST_WRITE_MS
    now_ms = time.time() * 1000
    out = out_path or (Path(paths.logs_dir()) / "boost_snapshot.json")

    if not force and _LAST_WRITE_MS is not None and (now_ms - _LAST_WRITE_MS) < _RATE_MS:
        return str(out)

    snap = make_snapshot()
    data = json.dumps(snap, ensure_ascii=False).encode("utf-8")

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        io_safe.write_atomic(out, data)
        _LAST_WRITE_MS = now_ms
    except Exception as e:
        # 最低限のフォールバックを試すが、失敗したら OSError で明示的に投げる
        try:
            tmp = out.with_suffix(out.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(out)
            _LAST_WRITE_MS = now_ms
        except Exception as e2:
            raise OSError(f"export_snapshot failed: {out}") from e2

    return str(out)

# desc: スナップショットJSONから、GPT引き継ぎ向けのテキストを生成する
def build_handover_text(snapshot: dict | None = None) -> str:
    try:
        snap = snapshot or make_snapshot()
    except Exception:
        snap = {}
    roots = snap.get("roots", {})
    recent = snap.get("recent", {})
    modules = snap.get("modules", [])
    env = snap.get("env", {})

    lines = []
    p = lines.append
    p("# BtcTradeSystemV1 Handover (BOOST)")
    p(f"- ts: {snap.get('ts','')}")
    p("## Roots")
    p(f"- data_root: {roots.get('data_root','')}")
    p(f"- logs_root: {roots.get('logs_root','')}")
    p("## Env")
    p(f"- BTC_TS_MODE: {env.get('BTC_TS_MODE')}")
    p(f"- PYTHONPATH_contains_repo: {env.get('PYTHONPATH_contains_repo')}")
    p("## Loaded modules (top 50)")
    for m in modules[:50]:
        p(f"- {m}")
    p("## Recent dev_audit tail (last 20)")
    for r in (recent.get("dev_audit_tail") or [])[-20:]:
        ev = r.get("event","")
        lvl = r.get("level","")
        ts  = r.get("ts","")
        feat= r.get("feature","")
        p(f"- [{ts}] {lvl} {ev} ({feat})")
    p("## How to reproduce (PowerShell)")
    p("```powershell")
    p("Set-Location $env:USERPROFILE\\BtcTradeSystemV1")
    p("$env:PYTHONPATH = (Get-Location).Path")
    p("$env:BTC_TS_LOGS_DIR = \"D:\\BtcTS_V1\\logs\"")
    p("python -m streamlit run .\\btc_trade_system\\features\\dash\\dashboard.py --server.port 8501")
    p("```")
    return "\n".join(lines) + "\n"

# desc: BOOST時に handover テキストも同時出力（logs/handover_gpt.txt）
def export_handover_text(force: bool = False) -> str:
    """
    handover_gpt.txt を logs に出力してフルパス（str）を返す。
    例外: 失敗時は OSError を送出（UI 側でトレース可能）
    """
    out = Path(paths.logs_dir()) / "handover_gpt.txt"
    snap = make_snapshot()  # ここでの失敗はそのまま外へ（原因特定が容易）
    text = build_handover_text(snap)

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        io_safe.write_atomic(out, text.encode("utf-8"))
    except Exception:
        try:
            tmp = out.with_suffix(out.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(out)
        except Exception as e2:
            raise OSError(f"export_handover_text failed: {out}") from e2

    return str(out)
