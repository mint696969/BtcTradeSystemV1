# path: tools/handoff/gen_summary.py
# desc: NEXT 環境の「引き継ぎ用サマリー」を最小構成で生成する（場所・状態・量だけを出す）

"""
Usage:
  python gen_summary.py --repo <repo_root> --data <data_dir> --logs <logs_dir> --out <SUMMARY.md>

Design goals (NEXT 正準):
- 次チャットで迷わないことを最優先
- 実装参照は禁止（import はしない）
- 情報は「場所・状態・量」に限定し、詳細ログや巨大データは含めない
- 旧系の名称やパスが成果物に混入しないようにする（混入は回帰）
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
from typing import List


def p(pth: Path) -> str:
    return str(pth).replace("\\", "/")


def list_files(base: Path, limit: int = 10) -> List[str]:
    if not base.exists():
        return ["(missing)"]
    out: List[str] = []
    try:
        for f in sorted(base.rglob("*")):
            if f.is_file():
                out.append(p(f.relative_to(base)))
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out or ["(empty)"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="repo root (NEXT main repo)")
    # 互換のため残す（旧引数名が使われていた場合の救済）
    ap.add_argument("--v1", required=False, help="(deprecated) same as --repo")
    ap.add_argument("--data", required=True, help="BTC_TS_DATA_DIR")
    ap.add_argument("--logs", required=True, help="BTC_TS_LOGS_DIR")
    ap.add_argument("--out", required=True, help="output SUMMARY.md")
    args = ap.parse_args()

    repo_arg = args.repo or args.v1
    repo = Path(repo_arg).resolve()
    data = Path(args.data).resolve()
    logs = Path(args.logs).resolve()
    out = Path(args.out).resolve()

    lines: List[str] = []

    lines.append("# BTCTS Context SUMMARY (NEXT 正準)")
    lines.append("")
    lines.append(f"- generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")

    lines.append("## Repo")
    lines.append(f"- root: {p(repo)}")
    lines.append(f"- exists: {repo.exists()}")
    lines.append("")

    lines.append("## Runtime roots")
    lines.append(f"- data: {p(data)}")
    lines.append(f"- logs: {p(logs)}")
    lines.append("")

    lines.append("## Data snapshot (representative)")
    for s in list_files(data, limit=10):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Logs snapshot (representative)")
    for s in list_files(logs, limit=10):
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Current Focus")
    lines.append("- Topic: repo map / handoff tooling stabilization")
    lines.append("- Area: tools/make_repo_map_extract.py, tools/handoff/gen_summary.py")
    lines.append("- Goal: next chat can resume work without reconstructing context")
    lines.append("")

    lines.append("## Known Blocking / Unfinished")
    lines.append("- This summary is intentionally minimal; handover.md is authoritative.")
    lines.append("- Any legacy naming/path leakage inside repo outputs is considered a regression.")
    lines.append("- Scheduler / collector deeper inspection is pending (see handover.md).")
    lines.append("")

    lines.append("## Next First Action")
    lines.append("- Read handover.md (latest daily report).")
    lines.append("- Inspect the file mentioned at the top of handover.md and continue from there.")
    lines.append("")

    lines.append("## Notes")
    lines.append("- This summary is intentionally thin.")
    lines.append("- Detailed structure is provided by repo_structure.yaml and REPO_MAP.extract.md.")
    lines.append("- The project assumes only NEXT code is present in this repo.")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
