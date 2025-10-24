# path: ./btc_trade_system/features/audit_dev/boost.py
# desc: BOOST/LITE スナップショットの“公式生成→handover本文”までを行う薄いラッパ（UIから1行で使う）

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple
import datetime as _dt
# 既存の公式API（ここを唯一の依存にしておく）
from btc_trade_system.common.boost_svc import (
    export_snapshot as _export_snapshot,
    build_handover_text as _build_handover_text,
)

def export_and_build_text(*, mode: str, force: bool = True) -> Tuple[str, str]:
    """
    公式スナップショットを生成して（必要なら上書き）→JSONを読み込み→handover本文を構築。
    UI側は返ってきた text をベースに、必要なら REPO_MAP 抜粋・audit_tail などを追記してください。
    Returns: (snapshot_path_str, handover_text)
    Raises : 既存APIに準じて例外をそのまま送出（UI側で握る方針）
    """
    snap_path = Path(_export_snapshot(mode=mode, force=force))
    snap_json = json.loads(snap_path.read_text(encoding="utf-8", errors="ignore"))
    text = _build_handover_text(snap_json)

    # === DEBUG の場合は 'errors_summary' と 'errors-only tail' を必ず末尾に追記 ===
    from btc_trade_system.features.audit_dev.snapshot_compose import (
        ensure_errors_summary_in_text,
        build_tail_block,
    )
    m = (mode or "OFF").upper()
    if m == "DEBUG":
        text = ensure_errors_summary_in_text(text, limit=150)
        tail_block = build_tail_block(mode="DEBUG", last_n=20)
        text += "\n" + tail_block + "\n"

    # handover_gpt.txt を必ず logs に書き出す（テスト対象を常に最新にする）
    try:
        from btc_trade_system.common import paths as _paths
        (_paths.logs_dir() / "handover_gpt.txt").write_text(text, encoding="utf-8")
    except Exception:
        pass

    return str(snap_path), text

# --- utilities moved from UI (kept UI logic unchanged) ---
from pathlib import Path as _Path
import shutil as _shutil
import subprocess as _subp

def git_status_brief(cwd: _Path | None = None) -> list[str]:
    """Git 簡易情報（root/branch/commit/dirty）。失敗時は ['- (git N/A)']。"""
    try:
        def _run(args):
            return _subp.check_output(args, cwd=cwd, stderr=_subp.DEVNULL, text=True, timeout=2).strip()
        root = _run(["git", "rev-parse", "--show-toplevel"])
        branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        commit = _run(["git", "rev-parse", "--short", "HEAD"])
        dirty = "1" if _run(["git", "status", "--porcelain"]) else "0"
        return [
            f"- root: {root}",
            f"- branch: {branch}",
            f"- commit: {commit}",
            f"- dirty: {dirty}",
        ]
    except Exception:
        return ["- (git N/A)"]

def path_probe(p: _Path) -> list[str]:
    """パス実体の簡易情報（exists/is_dir/is_file/mtime）。"""
    try:
        stt = p.stat()
        return [
            f"- path: {p}",
            f"- exists: True",
            f"- is_dir: {p.is_dir()}",
            f"- is_file: {p.is_file()}",
            f"- mtime: { _dt.datetime.utcfromtimestamp(stt.st_mtime).isoformat(timespec='seconds') + 'Z'}",
        ]
    except Exception:
        return [f"- path: {p}", "- exists: False"]

def disk_free_of(p: _Path) -> list[str]:
    """ディスク使用量（total/used/free）。失敗時はエラー文を返す。"""
    try:
        usage = _shutil.disk_usage(str(p.resolve()))
        def _fmt(n: int) -> str:
            for unit in ("B", "KB", "MB", "GB", "TB"):
                if n < 1024:
                    return f"{n:.0f}{unit}"
                n //= 1024
            return f"{n:.0f}PB"
        return [
            f"- total: {_fmt(usage.total)}",
            f"- used:  {_fmt(usage.used)}",
            f"- free:  {_fmt(usage.free)}",
        ]
    except Exception as e:
        return [f"- (disk_usage error: {e!r})"]
