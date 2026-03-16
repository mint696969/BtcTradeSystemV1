# path: ./btcts_next/src/btcts/replay/replay_export.py
# desc: Export replay fusion results and reports to JSON/JSONL artifacts.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from .replay_io import ensure_dir, write_json, write_jsonl
from .replay_report import build_replay_report


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_replay_results(
    *,
    name: str,
    source_paths: Iterable[Path],
    results: List[Dict],
    out_root: Path,
) -> Dict[str, str]:
    source_paths_str = [str(Path(p)) for p in source_paths]
    stamp = _utc_stamp()

    session_dir = ensure_dir(out_root / f"{name}_{stamp}")

    results_path = write_jsonl(session_dir / "replay_results.jsonl", results)

    report = build_replay_report(
        name=name,
        source_paths=source_paths_str,
        results=results,
    )
    report_path = write_json(session_dir / "replay_report.json", report)

    manifest = {
        "name": name,
        "created_at_utc": stamp,
        "source_paths": source_paths_str,
        "results_path": str(results_path),
        "report_path": str(report_path),
        "result_count": len(results),
    }
    manifest_path = write_json(session_dir / "manifest.json", manifest)

    return {
        "session_dir": str(session_dir),
        "results_path": str(results_path),
        "report_path": str(report_path),
        "manifest_path": str(manifest_path),
    }