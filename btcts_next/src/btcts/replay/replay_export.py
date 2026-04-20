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
    prediction_calibration_reviews: List[Dict] | None = None,
    tactic_proposal_outputs: List[Dict] | None = None,
    tactic_review_records: List[Dict] | None = None,
    tactic_operation_records: List[Dict] | None = None,
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
        prediction_calibration_reviews=prediction_calibration_reviews,
        tactic_proposal_outputs=tactic_proposal_outputs,
        tactic_review_records=tactic_review_records,
        tactic_operation_records=tactic_operation_records,
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

    prediction_calibration_review_path = None
    prediction_calibration_review_count = 0
    if prediction_calibration_reviews:
        prediction_calibration_review_count = len(prediction_calibration_reviews)
        prediction_calibration_review_path = str(
            write_json(
                session_dir / "prediction_calibration_review.json",
                prediction_calibration_reviews[-1],
            )
        )

    tactic_proposal_output_path = None
    tactic_proposal_output_count = 0
    if tactic_proposal_outputs:
        tactic_proposal_output_count = len(tactic_proposal_outputs)
        tactic_proposal_output_path = str(
            write_json(
                session_dir / "tactic_proposal_output.json",
                tactic_proposal_outputs[-1],
            )
        )

    tactic_review_record_path = None
    tactic_review_record_count = 0
    if tactic_review_records:
        tactic_review_record_count = len(tactic_review_records)
        tactic_review_record_path = str(
            write_json(
                session_dir / "tactic_review_record.json",
                tactic_review_records[-1],
            )
        )

    tactic_operation_record_path = None
    tactic_operation_record_count = 0
    if tactic_operation_records:
        tactic_operation_record_count = len(tactic_operation_records)
        tactic_operation_record_path = str(
            write_json(
                session_dir / "tactic_operation_record.json",
                tactic_operation_records[-1],
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
        "prediction_calibration_review_path": prediction_calibration_review_path,
        "prediction_calibration_review_count": prediction_calibration_review_count,
        "tactic_proposal_output_path": tactic_proposal_output_path,
        "tactic_proposal_output_count": tactic_proposal_output_count,
        "tactic_review_record_path": tactic_review_record_path,
        "tactic_review_record_count": tactic_review_record_count,
        "tactic_operation_record_path": tactic_operation_record_path,
        "tactic_operation_record_count": tactic_operation_record_count,
        "result_count": len(results),
    }
    manifest_path = write_json(session_dir / "manifest.json", manifest)

    return {
        "session_dir": str(session_dir),
        "results_path": str(results_path),
        "report_path": str(report_path),
        "prediction_evaluation_report_path": prediction_evaluation_report_path,
        "prediction_calibration_review_path": prediction_calibration_review_path,
        "tactic_proposal_output_path": tactic_proposal_output_path,
        "tactic_review_record_path": tactic_review_record_path,
        "tactic_operation_record_path": tactic_operation_record_path,
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
        prediction_calibration_reviews=session.prediction_calibration_reviews,
        tactic_proposal_outputs=session.tactic_proposal_outputs,
        tactic_review_records=session.tactic_review_records,
        tactic_operation_records=session.tactic_operation_records,
    )