# path: ./tools/run_l3_official_artifacts.py
# desc: Build official L3 replay/audit artifacts by orchestrating existing L3 audit tools.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.core import io
from btcts.core import paths as core_paths


REPO_ROOT = Path(__file__).resolve().parents[1]


_ARTIFACT_SCRIPTS: list[tuple[str, str]] = [
    ("threshold_grid_replay_audit", "test_l3_threshold_grid_replay_audit.py"),
    ("near_wall_rank_grid_audit", "test_l3_near_wall_rank_grid_audit.py"),
    ("near_wall_alignment_audit", "test_l3_near_wall_alignment_audit.py"),
    ("wall_rank_distribution_audit", "test_l3_wall_rank_distribution_audit.py"),
    ("wall_created_transition_audit", "test_l3_wall_created_transition_audit.py"),
    ("event_usage_audit", "test_l3_event_usage_audit.py"),
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_stamp() -> str:
    return _utc_now().strftime("%Y%m%d_%H%M%SZ")


def _artifact_root() -> Path:
    root = core_paths.logs_dir() / "derived" / "l3_official_artifacts"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _try_git_head() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
        )
        return out.decode("utf-8", errors="replace").strip()
    except Exception:
        return None


def _extract_json_block(text: str) -> dict[str, Any]:
    starts = [idx for idx, ch in enumerate(text) if ch == "{"]

    for start in starts:
        candidate = text[start:].strip()
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise RuntimeError("json report block not found in tool stdout")


def _run_tool(
    *,
    script_name: str,
    report_name: str,
    output_dir: Path,
    max_records: int | None,
) -> dict[str, Any]:
    script_path = REPO_ROOT / "tools" / script_name
    if not script_path.exists():
        raise RuntimeError(f"tool script not found: {script_path}")

    env = os.environ.copy()
    if max_records is not None:
        env["BTCTS_L3_AUDIT_MAX_RECORDS"] = str(int(max_records))

    proc = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    stdout_text = proc.stdout or ""
    stderr_text = proc.stderr or ""

    raw_stdout_path = output_dir / f"{report_name}.stdout.txt"
    raw_stderr_path = output_dir / f"{report_name}.stderr.txt"
    io.atomic_write_text(raw_stdout_path, stdout_text)
    io.atomic_write_text(raw_stderr_path, stderr_text)

    if proc.returncode != 0:
        raise RuntimeError(
            f"{script_name} failed with exit code {proc.returncode}. "
            f"See {raw_stdout_path.name} / {raw_stderr_path.name}"
        )

    report = _extract_json_block(stdout_text)
    report_path = output_dir / f"{report_name}.json"
    io.write_json(report_path, report, indent=2, sort_keys=True)

    return {
        "report_name": report_name,
        "script_name": script_name,
        "report_path": str(report_path),
        "stdout_path": str(raw_stdout_path),
        "stderr_path": str(raw_stderr_path),
        "returncode": proc.returncode,
    }


def build_l3_official_artifacts(
    *,
    output_dir: Path | None = None,
    max_records: int | None = None,
) -> Path:
    root = _artifact_root()
    out_dir = output_dir or (root / _utc_stamp())
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, Any]] = []

    for report_name, script_name in _ARTIFACT_SCRIPTS:
        print(f"[L3 official artifact] running: {script_name}", flush=True)
        result = _run_tool(
            script_name=script_name,
            report_name=report_name,
            output_dir=out_dir,
            max_records=max_records,
        )
        manifest_rows.append(result)

    manifest = {
        "generated_utc": _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(REPO_ROOT),
        "git_head": _try_git_head(),
        "artifact_policy_note": "gpt_room/memory/notes/L3_OFFICIAL_ARTIFACT_POLICY_2026-04-06.md",
        "closeout_gate_draft": "tmp/L3_CLOSEOUT_AND_L4_GATE_DRAFT_2026-04-06.md",
        "baseline_profile": {
            "wall_near_rank_threshold": 5,
            "wall_ratio_threshold": 0.30,
        },
        "max_records_override": max_records,
        "reports": manifest_rows,
    }

    io.write_json(out_dir / "manifest.json", manifest, indent=2, sort_keys=True)
    return out_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Optional explicit output directory. Default: logs/derived/l3_official_artifacts/<utc_stamp>",
    )
    ap.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Optional BTCTS_L3_AUDIT_MAX_RECORDS override forwarded to audit tools.",
    )
    args = ap.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else None
    out_dir = build_l3_official_artifacts(
        output_dir=output_dir,
        max_records=args.max_records,
    )

    print(f"OK l3_official_artifacts: {out_dir}")
    print(f"manifest: {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())