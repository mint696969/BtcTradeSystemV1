# path: ./scripts/check_gpt_room_persistence.py
# desc: Validates the selective Git allowlist and canonical gpt_room durability contract.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/gpt_room_tracked_files.json"


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tracked = payload["tracked_files"]
    excluded_prefixes = tuple(payload["excluded_prefixes"])

    if tracked != sorted(set(tracked)):
        raise SystemExit("tracked_files must be unique and sorted")

    missing = [path for path in tracked if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"missing canonical room files: {missing}")

    invalid_json: list[str] = []
    for path in tracked:
        if path.endswith(".json"):
            try:
                json.loads((ROOT / path).read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                invalid_json.append(path)
    if invalid_json:
        raise SystemExit(f"invalid canonical JSON files: {invalid_json}")

    still_ignored: list[str] = []
    for path in tracked:
        result = git("check-ignore", "-q", "--no-index", "--", path)
        if result.returncode == 0:
            still_ignored.append(path)
        elif result.returncode != 1:
            raise SystemExit(result.stderr.strip() or f"git check-ignore failed: {path}")
    if still_ignored:
        raise SystemExit(f"canonical room files are still ignored: {still_ignored}")

    must_remain_ignored = (
        "btcts_next/tmp/.gpt_room_ignore_probe",
        "tmp/work/.gpt_room_ignore_probe",
        "tmp/gpt_room/reference/.gpt_room_ignore_probe",
        "tmp/gpt_room/history/.gpt_room_ignore_probe",
    )
    unexpectedly_visible: list[str] = []
    for path in must_remain_ignored:
        result = git("check-ignore", "-q", "--no-index", "--", path)
        if result.returncode == 1:
            unexpectedly_visible.append(path)
        elif result.returncode != 0:
            raise SystemExit(result.stderr.strip() or f"git check-ignore probe failed: {path}")
    if unexpectedly_visible:
        raise SystemExit(f"non-canonical tmp paths are not ignored: {unexpectedly_visible}")

    tracked_now = git("ls-files", "--", "tmp/gpt_room")
    if tracked_now.returncode != 0:
        raise SystemExit(tracked_now.stderr.strip())
    actual = sorted(line.strip() for line in tracked_now.stdout.splitlines() if line.strip())
    unexpected = [path for path in actual if path not in tracked]
    if unexpected:
        raise SystemExit(f"unexpected tracked gpt_room files: {unexpected}")

    print("[PASS] gpt_room persistence policy validated")
    print(f"canonical_file_count={len(tracked)}")
    print("runtime_path=tmp/gpt_room")
    print("durability_boundary=commit_plus_remote_push")


if __name__ == "__main__":
    main()
