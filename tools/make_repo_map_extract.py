# path: tools/make_repo_map_extract.py
# desc: リポジトリを走査し、各ファイル先頭の「# path / # desc」を抽出して REPO_MAP の Markdown / YAML を生成（make_handoff.ps1 からのサブプロセス呼び出し対応）

"""
Usage (PowerShell):
  $py = ".\.venv\Scripts\python.exe"
  & $py tools\make_repo_map_extract.py \
      --root . \
      --out-md artifacts\context_bundle\TMP\REPO_MAP.extract.md \
      --out-yaml artifacts\context_bundle\TMP\repo_structure.yaml

make_handoff.ps1 からの呼び出し例:
  $pyTool = Join-Path $V1 "tools\make_repo_map_extract.py"
  if (Test-Path $pyTool) {
    & "$py" $pyTool --root $V1 `
      --out-md (Join-Path $TMP 'REPO_MAP.extract.md') `
      --out-yaml (Join-Path $TMP 'repo_structure.yaml')
  }

Notes:
- 2行ヘッダ (# path / # desc) が無い場合は、実際の相対パスのみを出力
- 既定で重い/不要ディレクトリは除外（.git, .venv, data, logs, artifacts, backup, cache, tmp, node_modules）
- 対象拡張子はテキスト中心（.py, .ps1, .psm1, .psd1, .bat, .cmd, .sh, .yaml, .yml, .json, .md, .toml, .ini）
- UTF-8 前提、読込時 errors="ignore" でサマリ取得の安全性を優先
"""

from __future__ import annotations
import argparse
import io
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Dict, Any
import time
import json

HEADER_PATH_RE = re.compile(r"^\s*#\s*path:\s*(.+)$", re.IGNORECASE)
HEADER_DESC_RE = re.compile(r"^\s*#\s*desc:\s*(.+)$", re.IGNORECASE)

DEFAULT_EXCLUDE = [
    ".git", ".venv", "venv", "node_modules", "data", "logs",
    "artifacts", "backup", "cache", "tmp"
]

DEFAULT_EXTS = [
    ".py", ".ps1", ".psm1", ".psd1", ".bat", ".cmd", ".sh",
    ".yaml", ".yml", ".json", ".md", ".toml", ".ini"
]


def read_header2(path: Path, max_bytes: int = 4096) -> Tuple[str, str]:
    """ファイル先頭から # path / # desc を抽出して返す。見つからなければ空文字。
    UTF-8 前提、errors='ignore' で安全読み。
    """
    try:
        with path.open("rb") as f:
            head = f.read(max_bytes)
        text = head.decode("utf-8", errors="ignore")
    except Exception:
        return "", ""
    # 先頭数行を対象
    lines = text.splitlines()[:4]
    p = ""; d = ""
    for ln in lines:
        m = HEADER_PATH_RE.match(ln)
        if m:
            p = m.group(1).strip()
        m2 = HEADER_DESC_RE.match(ln)
        if m2:
            d = m2.group(1).strip()
    return p, d


def should_skip(root: Path, p: Path, exclude: List[str]) -> bool:
    rel = p.relative_to(root).parts
    return len(rel) > 0 and rel[0].lower() in {e.lower() for e in exclude}


def iter_files(root: Path, exts: List[str], exclude: List[str]) -> Iterable[Path]:
    exts_l = {e.lower() for e in exts}
    for p in root.rglob("*"):
        if p.is_dir():
            if p.parent == root and p.name.lower() in {e.lower() for e in exclude}:
                for _ in ():
                    yield _
                continue
            continue
        if should_skip(root, p, exclude):
            continue
        if p.suffix.lower() not in exts_l:
            continue
        yield p


def build_index(root: Path, exts: List[str], exclude: List[str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for f in iter_files(root, exts, exclude):
        try:
            stat = f.stat()
        except OSError:
            continue
        hp, hd = read_header2(f)
        items.append({
            "path": str(f.relative_to(root)).replace("\\", "/"),
            "head1": hp,
            "head2": hd,
            "size": stat.st_size,
            "mtime": int(stat.st_mtime),
        })
    items.sort(key=lambda x: x["path"].lower())
    return items


def write_md(md_path: Path, items: List[Dict[str, Any]]) -> None:
    lines: List[str] = ["# REPO_MAP extract (header2 only)", ""]
    for it in items:
        p = it["head1"].strip() or it["path"]
        d = it["head2"].strip()
        lines.append(f"- **{p}** — {d}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_yaml(yaml_path: Path, items: List[Dict[str, Any]]) -> None:
    out_lines: List[str] = ["repo_structure:"]
    for it in items:
        out_lines.append("  - path: \"%s\"" % it["path"].replace("\"", "\\\""))
        if it["head1"]:
            out_lines.append("    head1: \"%s\"" % it["head1"].replace("\"", "\\\""))
        if it["head2"]:
            out_lines.append("    head2: \"%s\"" % it["head2"].replace("\"", "\\\""))
        out_lines.append("    size: %d" % it["size"])
        out_lines.append("    mtime: %d" % it["mtime"])
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Extract repo map from header2 comments")
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--out-md", dest="out_md", default=None, help="output markdown path")
    ap.add_argument("--out-yaml", dest="out_yaml", default=None, help="output yaml path")
    ap.add_argument("--exclude", nargs="*", default=DEFAULT_EXCLUDE, help="exclude top-level dirs")
    ap.add_argument("--exts", nargs="*", default=DEFAULT_EXTS, help="target file extensions")
    ap.add_argument("--max-bytes", type=int, default=4096, help="max header read bytes")
    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    ns = parse_args(argv)
    root = Path(ns.root).resolve()
    items = build_index(root, ns.exts, ns.exclude)

    if ns.out_md:
        write_md(Path(ns.out_md), items)
    else:
        buf_md: List[str] = ["# REPO_MAP extract (header2 only)", ""]
        for it in items:
            p = it["head1"].strip() or it["path"]
            d = it["head2"].strip()
            buf_md.append(f"- **{p}** — {d}")
        sys.stdout.write("\n".join(buf_md) + "\n")

    if ns.out_yaml:
        write_yaml(Path(ns.out_yaml), items)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
