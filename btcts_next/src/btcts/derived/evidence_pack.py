# path: ./btcts_next/src/btcts/derived/evidence_pack.py
# desc: Phase2：監査（audit）＋派生サマリ（derived）＋主要設定/状態の「証拠パック(zip)」を生成する。

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from btcts.core import env, io, paths


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_stamp() -> str:
    return _utc_now().strftime("%Y%m%d_%H%M%SZ")


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest().upper()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _try_git_head(repo_root: Path) -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root))
        return out.decode("utf-8", errors="replace").strip()
    except Exception:
        return None


def _tail_text_lines(src: Path, *, max_lines: int) -> str:
    # 大きいファイルでも破綻しにくい tail（deque）
    dq: deque[str] = deque(maxlen=int(max_lines))
    with open(src, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            dq.append(line)
    return "".join(dq)


@dataclass
class Item:
    kind: str                 # "copy" | "tail"
    src: str                  # absolute or logical
    dst: str                  # zip internal path (posix)
    exists: bool
    bytes: int
    sha256: Optional[str]
    note: str = ""


def _posix(p: str) -> str:
    return p.replace("\\", "/")


def build_evidence_pack(
    *,
    tail_audit_lines: int = 2000,
    tail_super_lines: int = 2000,
    tail_superlog_lines: int = 800,
    keep_dir: bool = True,
) -> Tuple[Path, Path]:
    repo_root = paths.repo_root()
    logs_dir = paths.logs_dir()
    data_dir = paths.data_dir()
    cfg_dir = paths.config_dir()
    derived_dir = logs_dir / "derived"
    derived_dir.mkdir(parents=True, exist_ok=True)

    stamp = _utc_stamp()
    pack_dir = derived_dir / "evidence_packs" / stamp
    pack_dir.mkdir(parents=True, exist_ok=True)

    items: List[Item] = []

    def add_copy(src: Path, dst_rel: str, *, note: str = "") -> None:
        dst_rel2 = _posix(dst_rel)
        if src.exists():
            dst_path = pack_dir / dst_rel2
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_path)
            b = dst_path.stat().st_size
            items.append(Item("copy", str(src), dst_rel2, True, int(b), _sha256_file(dst_path), note))
        else:
            items.append(Item("copy", str(src), dst_rel2, False, 0, None, note))

    def add_tail(src: Path, dst_rel: str, *, max_lines: int, note: str = "") -> None:
        dst_rel2 = _posix(dst_rel)
        if src.exists():
            dst_path = pack_dir / dst_rel2
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            text = _tail_text_lines(src, max_lines=max_lines)
            io.atomic_write_text(dst_path, text)
            b = dst_path.stat().st_size
            items.append(Item("tail", str(src), dst_rel2, True, int(b), _sha256_file(dst_path), note))
        else:
            items.append(Item("tail", str(src), dst_rel2, False, 0, None, note))

    # ---- derived（判断の主役）----
    add_copy(derived_dir / "latest_hourly.json", "derived/latest_hourly.json", note="derived summary (latest hour)")
    add_copy(derived_dir / "latest_daily.json", "derived/latest_daily.json", note="derived summary (latest day)")
    add_copy(derived_dir / "state.json", "derived/state.json", note="derived cursor/state (internal)")

    # ---- settings / status（判断の土台）----
    add_copy(cfg_dir / "collector.yaml", "config/ui/collector.yaml", note="collector runtime config")
    add_copy(cfg_dir / "watchdog.yaml", "config/ui/watchdog.yaml", note="watchdog config (if exists)")
    add_copy(data_dir / "collector" / "status.json", "data/collector/status.json", note="collector status snapshot")
    add_copy(data_dir / "collector" / "rate_state.json", "data/collector/rate_state.json", note="rate control state")

    # ---- logs（巨大なので tail のみ）----
    add_tail(logs_dir / "audit.jsonl", "logs_tail/audit_tail.jsonl", max_lines=tail_audit_lines, note=f"tail {tail_audit_lines} lines")
    add_tail(logs_dir / "supervisor_collector.jsonl", "logs_tail/supervisor_collector_tail.jsonl", max_lines=tail_super_lines, note=f"tail {tail_super_lines} lines")
    add_tail(logs_dir / "supervisor_collector.log", "logs_tail/supervisor_collector_tail.log", max_lines=tail_superlog_lines, note=f"tail {tail_superlog_lines} lines")

    # ---- manifest（台帳）----
    manifest: Dict[str, Any] = {
        "generated_utc": _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "paths": {
            "config_dir": str(cfg_dir),
            "data_dir": str(data_dir),
            "logs_dir": str(logs_dir),
            "derived_dir": str(derived_dir),
        },
        "mode": env.mode(),
        "git_head": _try_git_head(repo_root),
        "items": [item.__dict__ for item in items],
    }
    io.write_json(pack_dir / "manifest.json", manifest, indent=2, sort_keys=True)

    # ---- zip ----
    zip_path = derived_dir / f"evidence_pack_{stamp}.zip"
    if zip_path.exists():
        zip_path.unlink(missing_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in pack_dir.rglob("*"):
            if p.is_file():
                arc = _posix(str(p.relative_to(pack_dir)))
                z.write(p, arcname=arc)

    if not keep_dir:
        shutil.rmtree(pack_dir, ignore_errors=True)

    return zip_path, pack_dir


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail-audit", type=int, default=2000)
    ap.add_argument("--tail-super", type=int, default=2000)
    ap.add_argument("--tail-superlog", type=int, default=800)
    ap.add_argument("--no-keep-dir", action="store_true")
    args = ap.parse_args()

    zip_path, pack_dir = build_evidence_pack(
        tail_audit_lines=args.tail_audit,
        tail_super_lines=args.tail_super,
        tail_superlog_lines=args.tail_superlog,
        keep_dir=(not args.no_keep_dir),
    )
    print(f"OK evidence_pack: {zip_path}")
    print(f"pack_dir: {pack_dir}")


if __name__ == "__main__":
    main()
