# path: ./tools/make_repo_map_extract.py
# desc: リポジトリ構造の要約/抽出（handoff 用 repo map 生成支援）

"""
Usage (PowerShell):
  # python は PATH でもOK。venv を使う場合は各自の運用に合わせること。
  $py = "python"
  $out = ".\\tmp\\handoff"
  & $py tools\\make_repo_map_extract.py --root . --out-md "$out\\REPO_MAP.extract.md" --out-yaml "$out\\repo_structure.yaml"

外部ルート（ランタイム領域）も同時にマップ化する場合（例: E:\\btc_ts）:
  & $py tools\\make_repo_map_extract.py --root . --out-yaml "$out\\repo_structure.yaml" --extra-root E:\\btc_ts

Notes:
- 2行ヘッダ (# path / # desc) が無い場合は、実際の相対パスのみを出力
- 既定で重い/不要ディレクトリは除外（.git, .venv, data, logs, artifacts, backup, cache, tmp, node_modules）
- 対象拡張子はテキスト中心（.py, .ps1, .psm1, .psd1, .bat, .cmd, .sh, .yaml, .yml, .json, .md, .toml, .ini）
- UTF-8 前提、読込時 errors="ignore" でサマリ取得の安全性を優先

--extra-root について（NEXT運用の迷子防止）
- 例: E:\\btc_ts
- 目的: 設定/出力/secrets の「場所」を GPT が理解できるようにする
- secrets は中身を列挙しない（ファイル名をマスクして存在だけを出す）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Dict, Any


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

# リポ外（例: E:\btc_ts）に対して「出してよい／出す価値が高い」ものだけを拾う既定。
# - config/ui: 運用差分（current override）
# - config/schema: schema（配布物）
# - data/logs: 代表（README など）
# - secrets: 位置のみ（ファイル名はマスク）
DEFAULT_EXTRA_GLOBS = [
    "config/ui/*.yaml",
    "config/ui/*.yml",
    "config/schema/*.yaml",
    "config/schema/*.yml",
    "data/README*",
    "logs/README*",
    "secrets/*",
]


def read_header2(path: Path, max_bytes: int = 4096) -> Tuple[str, str]:
    """ファイル先頭から # path / # desc を抽出して返す。見つからなければ空文字。"""
    try:
        head = path.read_bytes()[:max_bytes]
        text = head.decode("utf-8", errors="ignore")
    except Exception:
        return "", ""

    lines = text.splitlines()[:6]
    p = ""
    d = ""
    for ln in lines:
        m = HEADER_PATH_RE.match(ln)
        if m:
            p = m.group(1).strip()
        m2 = HEADER_DESC_RE.match(ln)
        if m2:
            d = m2.group(1).strip()
    return p, d


def should_skip(root: Path, p: Path, exclude: List[str]) -> bool:
    """
    除外ディレクトリ判定（階層非依存）。
    例: root/btcts_next/data/... のように 2階層目以降に data/logs/tmp が出ても除外できるようにする。
    """
    try:
        rel_parts = p.relative_to(root).parts
    except Exception:
        return False
    if not rel_parts:
        return False

    excl = {e.lower() for e in exclude if e}
    # どの階層でも exclude 名が現れたら除外
    for part in rel_parts:
        if part.lower() in excl:
            return True
    return False


def iter_files(root: Path, exts: List[str], exclude: List[str]) -> Iterable[Path]:
    exts_l = {e.lower() for e in exts}
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if should_skip(root, p, exclude):
            continue
        if p.suffix.lower() not in exts_l:
            continue
        yield p


def build_index(root: Path, exts: List[str], exclude: List[str], max_bytes: int) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for f in iter_files(root, exts, exclude):
        try:
            stat = f.stat()
        except OSError:
            continue
        hp, hd = read_header2(f, max_bytes=max_bytes)
        items.append(
            {
                "path": str(f.relative_to(root)).replace("\\", "/"),
                "head1": hp,
                "head2": hd,
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
            }
        )
    items.sort(key=lambda x: x["path"].lower())
    return items


def _safe_rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def _infer_name_from_root(extra_root: Path) -> str:
    name = (extra_root.name or "extra").strip()
    return name if name else "extra"


def build_extra_map(
    extra_root: Path,
    globs: List[str],
    max_bytes: int,
    extra_exclude_re: Optional[re.Pattern] = None,
) -> Dict[str, Any]:
    """リポ外ルートを「必要最小限かつ十分」にマップ化する（allowlist方式）。"""
    root = extra_root.resolve()

    out: Dict[str, Any] = {
        "name": _infer_name_from_root(root),
        "root": str(root).replace("\\", "/"),
        "policy": {
            "purpose": "runtime external root for BTCTS (paths/configs/outputs)",
            "secrets": "masked (names hidden)",
            "data_logs": "representative only (README etc.)",
        },
        "dirs": [
            {"path": "config/ui", "desc": "current override (diff-only) YAMLs"},
            {"path": "config/schema", "desc": "schema/default YAMLs"},
            {"path": "data", "desc": "runtime data root (representative only)"},
            {"path": "logs", "desc": "runtime logs root (representative only)"},
            {"path": "secrets", "desc": "API keys/tokens (masked; do not include files)"},
        ],
        "files": [],
    }

    files: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for g in globs:
        try:
            for p in root.glob(g):
                if not p.exists() or not p.is_file():
                    continue
                rel = _safe_rel(root, p)

                # extra exclude: 外部ルートで「迷子要因」になる領域を根本から除外する。
                # ただし secrets は列挙せず「存在だけ」を残す（masked）。
                if extra_exclude_re and extra_exclude_re.search(rel):
                    if rel.lower().startswith("secrets/"):
                        masked = "secrets/***"
                        if masked not in seen:
                            files.append({"path": masked, "masked": True})
                            seen.add(masked)
                    continue

                # secrets はファイル名を出さない（存在だけ）
                if rel.lower().startswith("secrets/"):
                    masked = "secrets/***"
                    if masked not in seen:
                        files.append({"path": masked, "masked": True})
                        seen.add(masked)
                    continue

                if rel in seen:
                    continue

                try:
                    st = p.stat()
                except OSError:
                    continue

                hp, hd = read_header2(p, max_bytes=max_bytes)
                files.append(
                    {
                        "path": rel,
                        "head1": hp,
                        "head2": hd,
                        "size": st.st_size,
                        "mtime": int(st.st_mtime),
                    }
                )
                seen.add(rel)
        except Exception:
            continue

    files.sort(key=lambda x: (x.get("path", "").lower()))
    out["files"] = files
    return out


def _yaml_quote(s: str) -> str:
    # YAML のダブルクォート文字列として安全に出す（最小限）
    return "\"%s\"" % (s or "").replace("\\", "\\\\").replace("\"", "\\\"")


def write_md(md_path: Path, root_items: List[Dict[str, Any]], extra: List[Dict[str, Any]]) -> None:
    lines: List[str] = ["# REPO_MAP extract (header2 only)", ""]

    lines.append("## Repo (tracked sources)")
    for it in root_items:
        p = it["head1"].strip() or it["path"]
        d = it["head2"].strip()
        lines.append(f"- **{p}** — {d}")

    if extra:
        lines.append("")
        lines.append("## External roots (runtime)")
        for ex in extra:
            lines.append(f"- **{ex.get('name','extra')}**: {ex.get('root','')}")
            for d in ex.get("dirs", []) or []:
                lines.append(f"  - {d.get('path','')}: {d.get('desc','')}")
            for f in ex.get("files", []) or []:
                if f.get("masked"):
                    lines.append(f"  - {f.get('path')}: (masked)")
                else:
                    pp = f.get("head1") or f.get("path")
                    dd = f.get("head2") or ""
                    lines.append(f"  - {pp} — {dd}")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_yaml(yaml_path: Path, root: Path, root_items: List[Dict[str, Any]], extra: List[Dict[str, Any]]) -> None:
    # 互換性のため、従来の repo_structure は維持しつつ、external_roots を追加する。
    out_lines: List[str] = []

    out_lines.append("meta:")
    out_lines.append(f"  repo_root: {_yaml_quote(str(root).replace('\\\\', '/'))}")

    out_lines.append("repo_structure:")
    for it in root_items:
        out_lines.append(f"  - path: {_yaml_quote(it['path'])}")
        if it.get("head1"):
            out_lines.append(f"    head1: {_yaml_quote(it['head1'])}")
        if it.get("head2"):
            out_lines.append(f"    head2: {_yaml_quote(it['head2'])}")
        out_lines.append(f"    size: {int(it['size'])}")
        out_lines.append(f"    mtime: {int(it['mtime'])}")

    out_lines.append("external_roots:")
    if not extra:
        out_lines.append("  []")
    else:
        for ex in extra:
            out_lines.append(f"  - name: {_yaml_quote(str(ex.get('name','extra')))}")
            out_lines.append(f"    root: {_yaml_quote(str(ex.get('root','')))}")

            out_lines.append("    policy:")
            pol = ex.get("policy", {}) or {}
            out_lines.append(f"      purpose: {_yaml_quote(str(pol.get('purpose','')))}")
            out_lines.append(f"      secrets: {_yaml_quote(str(pol.get('secrets','')))}")
            out_lines.append(f"      data_logs: {_yaml_quote(str(pol.get('data_logs','')))}")

            out_lines.append("    dirs:")
            for d in ex.get("dirs", []) or []:
                out_lines.append(f"      - path: {_yaml_quote(str(d.get('path','')))}")
                out_lines.append(f"        desc: {_yaml_quote(str(d.get('desc','')))}")

            out_lines.append("    files:")
            for f in ex.get("files", []) or []:
                out_lines.append(f"      - path: {_yaml_quote(str(f.get('path','')))}")
                if f.get("masked"):
                    out_lines.append("        masked: true")
                else:
                    if f.get("head1"):
                        out_lines.append(f"        head1: {_yaml_quote(str(f.get('head1','')))}")
                    if f.get("head2"):
                        out_lines.append(f"        head2: {_yaml_quote(str(f.get('head2','')))}")
                    if "size" in f:
                        out_lines.append(f"        size: {int(f.get('size', 0))}")
                    if "mtime" in f:
                        out_lines.append(f"        mtime: {int(f.get('mtime', 0))}")

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

    ap.add_argument(
        "--extra-root",
        action="append",
        default=[],
        help="extra external root to include (e.g. E:\\btc_ts). repeatable.",
    )
    ap.add_argument(
        "--extra-glob",
        action="append",
        default=[],
        help="glob patterns relative to each extra-root. if omitted, defaults are used.",
    )

    ap.add_argument(
        "--extra-exclude-regex",
        default=r"(_stash|secrets|logs|data|backup|tmp|\.git|\.venv|__pycache__)(/|\\)",
        help=(
            "regex to exclude paths inside extra-root(s). "
            "default excludes runtime/noise dirs (incl. _stash old V1). "
            "Note: secrets are still represented as 'secrets/***' (masked)."
        ),
    )

    return ap.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    ns = parse_args(argv)
    root = Path(ns.root).resolve()

    root_items = build_index(root, ns.exts, ns.exclude, max_bytes=ns.max_bytes)

    extra_globs = ns.extra_glob or DEFAULT_EXTRA_GLOBS

    # 外部ルートの除外は「根本対策」。_stash(旧V1退避) 等をここで潰す。
    try:
        extra_exclude_re = re.compile(str(ns.extra_exclude_regex), re.IGNORECASE)
    except Exception:
        extra_exclude_re = None

    extra_maps: List[Dict[str, Any]] = []
    for r in ns.extra_root or []:
        try:
            p = Path(r)
            if p.exists() and p.is_dir():
                extra_maps.append(
                    build_extra_map(
                        p,
                        extra_globs,
                        max_bytes=ns.max_bytes,
                        extra_exclude_re=extra_exclude_re,
                    )
                )
        except Exception:
            continue

    if ns.out_md:
        write_md(Path(ns.out_md), root_items, extra_maps)
    else:
        buf_md: List[str] = ["# REPO_MAP extract (header2 only)", ""]
        buf_md.append("## Repo (tracked sources)")
        for it in root_items:
            p = it["head1"].strip() or it["path"]
            d = it["head2"].strip()
            buf_md.append(f"- **{p}** — {d}")
        if extra_maps:
            buf_md.append("")
            buf_md.append("## External roots (runtime)")
            for ex in extra_maps:
                buf_md.append(f"- **{ex.get('name','extra')}**: {ex.get('root','')}")
        sys.stdout.write("\n".join(buf_md) + "\n")

    if ns.out_yaml:
        write_yaml(Path(ns.out_yaml), root=root, root_items=root_items, extra=extra_maps)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
