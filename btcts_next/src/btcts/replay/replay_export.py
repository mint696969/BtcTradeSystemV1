# path: ./btcts_next/src/btcts/replay/replay_export.py
# desc: Export replay fusion results and reports to JSON/JSONL artifacts.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

from .prediction_evaluation_report import build_prediction_evaluation_report
from .replay_io import ensure_dir, write_json, write_jsonl
from .replay_report import build_replay_report
from .replay_session import ReplaySession


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_replay_results(
    *,
    name: str,
    source_paths: Iterable[Path],
    results: List[Dict],
    out_root: Path,
    prediction_evaluation_entries: List[Dict] | None = None,
) -> Dict[str, str]:
    source_paths_str = [str(Path(p)) for p in source_paths]
    stamp = _utc_stamp()

    session_dir = ensure_dir(out_root / f"{name}_{stamp}")

    results_path = write_jsonl(session_dir / "replay_results.jsonl", results)

    report = build_replay_report(
        name=name,
        source_paths=source_paths_str,
        results=results,
        prediction_evaluation_entries=prediction_evaluation_entries,
    )
    report_path = write_json(session_dir / "replay_report.json", report)

    prediction_evaluation_report_path = None
    prediction_evaluation_entry_count = 0
    if prediction_evaluation_entries:
        prediction_evaluation_entry_count = len(prediction_evaluation_entries)
        prediction_evaluation_report = build_prediction_evaluation_report(
            name=f"{name}_prediction_evaluation",
            entries=prediction_evaluation_entries,
        )
        prediction_evaluation_report_path = str(
            write_json(
                session_dir / "prediction_evaluation_report.json",
                prediction_evaluation_report,
            )
        )

    manifest = {
        "name": name,
        "created_at_utc": stamp,
        "source_paths": source_paths_str,
        "results_path": str(results_path),
        "report_path": str(report_path),
        "prediction_evaluation_report_path": prediction_evaluation_report_path,
        "prediction_evaluation_entry_count": prediction_evaluation_entry_count,
        "result_count": len(results),
    }
    manifest_path = write_json(session_dir / "manifest.json", manifest)

    return {
        "session_dir": str(session_dir),
        "results_path": str(results_path),
        "report_path": str(report_path),
        "prediction_evaluation_report_path": prediction_evaluation_report_path,
        "manifest_path": str(manifest_path),
    }


def export_replay_session(
    *,
    session: ReplaySession,
    out_root: Path,
) -> Dict[str, str]:
    return export_replay_results(
        name=session.name,
        source_paths=[Path(p) for p in session.source_paths],
        results=session.output,
        out_root=out_root,
        prediction_evaluation_entries=session.prediction_evaluation_entries,
    )