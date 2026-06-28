# path: ./tools/test_phase4a_prediction_system_ps_q23c_distributed_reader_validator_close_guard.py
# desc: Close guard for PS-Q23C distributed reader validator patch.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23C_DISTRIBUTED_READER_VALIDATOR_2026-06-28.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23c_distributed_reader_validator.py",
    "tools/test_phase4a_prediction_system_ps_q23c_distributed_reader_validator.py",
    "tools/test_phase4a_prediction_system_ps_q23c_distributed_reader_validator_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or path.endswith(".pyc") or "/__pycache__/" in path:
            continue
        out.add(path)
    return out


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED,
        "guard": "ps_q23c_distributed_reader_validator_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "read_only_validator": True,
            "prefers_latest_manifest": True,
            "fallback_to_legacy_latest": True,
            "writes_d_hot_runtime_artifacts": False,
            "latest_manifest_written_by_patch": False,
            "run_sidecars_written_by_patch": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
