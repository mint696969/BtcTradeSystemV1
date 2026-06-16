# path: ./tools/run_archive_copy_job.py
# desc: Safe copy-only archive job from hot(D) to cold(E).

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HOT_ROOT_DEFAULT = Path(r"D:\btc_ts_hot")
COLD_ROOT_DEFAULT = Path(r"E:\btc_ts")

DEFAULT_RELATIVE_PREFIXES = [
    "data/market_data",
    "data/collector_raw",
    "state/collector_vnext",
    "logs/collector_vnext",
]


@dataclass(frozen=True)
class CopyItem:
    src: Path
    dst: Path
    kind: str  # file | dir


def _iter_date_dirs(base: Path) -> Iterable[Path]:
    if not base.exists():
        return
    for p in base.rglob("*"):
        if p.is_dir() and p.name.startswith("date="):
            yield p


def _has_date_dirs(base: Path) -> bool:
    if not base.exists():
        return False
    for p in base.rglob("*"):
        if p.is_dir() and p.name.startswith("date="):
            return True
    return False


def _iter_target_roots(hot_root: Path, relative_prefixes: list[str]) -> Iterable[tuple[str, Path]]:
    for rel in relative_prefixes:
        p = hot_root / rel
        if p.exists():
            yield rel, p


def _match_date_dir(path: Path, target_date: str | None) -> bool:
    if target_date is None:
        return True
    return path.name == f"date={target_date}"


def _build_copy_plan(
    *,
    hot_root: Path,
    cold_root: Path,
    relative_prefixes: list[str],
    target_date: str | None,
) -> list[CopyItem]:
    items: list[CopyItem] = []

    for rel_prefix, root in _iter_target_roots(hot_root, relative_prefixes):
        # data 系は date=YYYY-MM-DD ディレクトリ単位で扱う
        if rel_prefix.startswith("data/"):
            for date_dir in _iter_date_dirs(root):
                if not _match_date_dir(date_dir, target_date):
                    continue

                rel = date_dir.relative_to(hot_root)
                dst_dir = cold_root / rel

                if not dst_dir.exists():
                    items.append(CopyItem(src=date_dir, dst=dst_dir, kind="dir"))
                    continue

                for src_file in date_dir.rglob("*"):
                    if not src_file.is_file():
                        continue

                    rel_file = src_file.relative_to(hot_root)
                    dst_file = cold_root / rel_file

                    if not dst_file.exists():
                        items.append(CopyItem(src=src_file, dst=dst_file, kind="file"))
                        continue

                    src_size = src_file.stat().st_size
                    dst_size = dst_file.stat().st_size

                    if dst_size < src_size:
                        items.append(CopyItem(src=src_file, dst=dst_file, kind="file"))

            continue

        # state / logs 系は prefix 配下の file を直接見る
        for src_file in root.rglob("*"):
            if not src_file.is_file():
                continue

            rel_file = src_file.relative_to(hot_root)
            dst_file = cold_root / rel_file

            if not dst_file.exists():
                items.append(CopyItem(src=src_file, dst=dst_file, kind="file"))
                continue

            src_size = src_file.stat().st_size
            dst_size = dst_file.stat().st_size

            if dst_size < src_size:
                items.append(CopyItem(src=src_file, dst=dst_file, kind="file"))

    return items


def _copy_dir(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _execute_copy_plan(items: list[CopyItem], *, dry_run: bool) -> dict:
    copied_dirs = 0
    copied_files = 0
    skipped = 0
    errors: list[dict] = []

    for item in items:
        try:
            if dry_run:
                skipped += 1
                continue

            if item.kind == "dir":
                _copy_dir(item.src, item.dst)
                copied_dirs += 1
            else:
                _copy_file(item.src, item.dst)
                copied_files += 1

        except Exception as e:
            errors.append(
                {
                    "src": str(item.src),
                    "dst": str(item.dst),
                    "kind": item.kind,
                    "error": f"{type(e).__name__}: {e}",
                }
            )

    return {
        "copied_dirs": copied_dirs,
        "copied_files": copied_files,
        "dry_run_skipped": skipped,
        "error_count": len(errors),
        "errors_sample": errors[:20],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy hot data to cold storage safely (copy-only).")
    parser.add_argument("--hot-root", default=str(HOT_ROOT_DEFAULT))
    parser.add_argument("--cold-root", default=str(COLD_ROOT_DEFAULT))
    parser.add_argument("--date", default=None, help="Target date like 2026-03-19")
    parser.add_argument(
        "--prefix",
        action="append",
        default=[],
        help="Relative prefix under hot root. Can be repeated. Default includes market_data/raw/state/logs.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    hot_root = Path(args.hot_root)
    cold_root = Path(args.cold_root)
    relative_prefixes = args.prefix or list(DEFAULT_RELATIVE_PREFIXES)

    plan = _build_copy_plan(
        hot_root=hot_root,
        cold_root=cold_root,
        relative_prefixes=relative_prefixes,
        target_date=args.date,
    )

    result = _execute_copy_plan(plan, dry_run=args.dry_run)

    print(
        json.dumps(
            {
                "ok": result["error_count"] == 0,
                "mode": "dry_run" if args.dry_run else "copy",
                "hot_root": str(hot_root),
                "cold_root": str(cold_root),
                "target_date": args.date,
                "relative_prefixes": relative_prefixes,
                "plan_count": len(plan),
                **result,
                "plan_sample": [
                    {
                        "kind": x.kind,
                        "src": str(x.src),
                        "dst": str(x.dst),
                    }
                    for x in plan[:20]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()