# path: ./btcts_next/src/btcts/prediction/market_regime/tools/calibration_evidence_once.py
# desc: Read-only MR-F7 once tool that audits D-hot outcome/trace calibration evidence without fitting, writing artifacts, or changing runtime confidence.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from btcts.prediction.market_regime.calibration_evidence_readiness import (
    build_market_regime_calibration_evidence_readiness,
)

MARKET_REGIME_CALIBRATION_EVIDENCE_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.calibration_evidence_once.mr_f7.v1"
)
DEFAULT_MAX_OUTCOME_ROWS = 100_000
DEFAULT_MAX_TRACE_ROWS = 100_000
DEFAULT_MAX_TOTAL_BYTES = 512 * 1024 * 1024


def _candidate_paths(root: Path, relative_glob: str) -> list[Path]:
    return sorted(path for path in root.glob(relative_glob) if path.is_file())


def _read_jsonl_rows(
    paths: Iterable[Path],
    *,
    root: Path,
    max_rows: int,
    max_total_bytes: int,
    required_artifact_kind: str | None = None,
    selected_run_ids: set[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    file_count = 0
    scanned_line_count = 0
    parsed_object_count = 0
    filtered_artifact_count = 0
    filtered_selection_count = 0
    total_bytes = 0
    truncated = False
    row_limit = max(1, int(max_rows))
    byte_limit = max(1, int(max_total_bytes))

    for path in paths:
        if len(rows) >= row_limit or total_bytes >= byte_limit:
            truncated = True
            break
        file_count += 1
        try:
            handle = path.open("rb")
        except OSError as exc:
            failures.append(f"open_failed:{path.relative_to(root).as_posix()}:{exc.__class__.__name__}")
            continue
        with handle:
            for line_number, raw in enumerate(handle, start=1):
                if len(rows) >= row_limit or total_bytes + len(raw) > byte_limit:
                    truncated = True
                    break
                scanned_line_count += 1
                total_bytes += len(raw)
                if not raw.strip():
                    continue
                try:
                    payload = json.loads(raw.decode("utf-8-sig"))
                except Exception:
                    failures.append(
                        f"invalid_json:{path.relative_to(root).as_posix()}:{line_number}"
                    )
                    continue
                if not isinstance(payload, Mapping):
                    failures.append(
                        f"json_not_object:{path.relative_to(root).as_posix()}:{line_number}"
                    )
                    continue
                parsed_object_count += 1
                if required_artifact_kind is not None and payload.get("artifact_kind") != required_artifact_kind:
                    filtered_artifact_count += 1
                    continue
                if selected_run_ids is not None:
                    run_id = str(payload.get("run_id") or "").strip()
                    if not run_id:
                        failures.append(
                            f"selected_row_run_id_missing:{path.relative_to(root).as_posix()}:{line_number}"
                        )
                        continue
                    if run_id not in selected_run_ids:
                        filtered_selection_count += 1
                        continue
                rows.append(dict(payload))
            if truncated:
                break

    return rows, {
        "file_count": file_count,
        "scanned_line_count": scanned_line_count,
        "parsed_object_count": parsed_object_count,
        "selected_row_count": len(rows),
        "filtered_artifact_count": filtered_artifact_count,
        "filtered_selection_count": filtered_selection_count,
        "selected_run_id_count": len(selected_run_ids) if selected_run_ids is not None else None,
        "total_bytes": total_bytes,
        "max_rows": row_limit,
        "max_total_bytes": byte_limit,
        "truncated": truncated,
        "failure_count": len(failures),
        "failures": failures[:100],
        "failures_truncated": len(failures) > 100,
    }


def build_market_regime_calibration_evidence_once_report(
    *,
    hot_root: str | Path,
    max_outcome_rows: int = DEFAULT_MAX_OUTCOME_ROWS,
    max_trace_rows: int = DEFAULT_MAX_TRACE_ROWS,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, Any]:
    root = Path(hot_root).resolve()
    outcome_paths = _candidate_paths(
        root,
        "prediction/market_regime/outcomes/date=*/part-*.jsonl",
    )
    trace_paths = _candidate_paths(
        root,
        "prediction/market_regime/ledgers/date=*/hour=*/part-*.jsonl",
    )
    outcome_rows, outcome_scan = _read_jsonl_rows(
        outcome_paths,
        root=root,
        max_rows=max_outcome_rows,
        max_total_bytes=max_total_bytes,
    )
    outcome_run_ids = {
        str(row.get("run_id") or "").strip()
        for row in outcome_rows
        if str(row.get("run_id") or "").strip()
    }
    remaining_bytes = max(1, int(max_total_bytes) - int(outcome_scan["total_bytes"]))
    trace_rows, trace_scan = _read_jsonl_rows(
        trace_paths,
        root=root,
        max_rows=max_trace_rows,
        max_total_bytes=remaining_bytes,
        required_artifact_kind="trace_row",
        selected_run_ids=outcome_run_ids,
    )
    readiness = build_market_regime_calibration_evidence_readiness(
        outcome_rows=outcome_rows,
        trace_rows=trace_rows,
    )
    input_complete = not outcome_scan["truncated"] and not trace_scan["truncated"]
    reader_ok = outcome_scan["failure_count"] == 0 and trace_scan["failure_count"] == 0
    return {
        "schema_version": "market_regime_calibration_evidence_once_report.mr_f7.v1",
        "tool_version": MARKET_REGIME_CALIBRATION_EVIDENCE_ONCE_TOOL_VERSION,
        "hot_root": str(root),
        "ok": bool(readiness["ok"] and reader_ok and input_complete),
        "input_complete": input_complete,
        "reader_ok": reader_ok,
        "outcome_scan": outcome_scan,
        "trace_scan": trace_scan,
        "readiness": readiness,
        "closeout_interpretation": {
            "coarse_calibration_evidence_available": bool(
                input_complete and readiness["coarse_calibration_ready"]
            ),
            "detailed_source_flag_evidence_available": bool(
                input_complete and readiness["detailed_source_flag_calibration_ready"]
            ),
            "legacy_history_may_be_used_for_detailed_source_flag_fit": False,
            "report_is_complete_only_when_not_truncated": True,
        },
        "safety": {
            "read_only": True,
            "writes_hot_data": False,
            "writes_repository": False,
            "fits_calibration_model": False,
            "changes_runtime_confidence": False,
            "scheduler_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "would_send_to_broker": False,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit MR-F7 calibration evidence from outcome and trace JSONL without writes."
    )
    parser.add_argument("--hot-root", required=True)
    parser.add_argument("--max-outcome-rows", type=int, default=DEFAULT_MAX_OUTCOME_ROWS)
    parser.add_argument("--max-trace-rows", type=int, default=DEFAULT_MAX_TRACE_ROWS)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Required acknowledgement that this command is a read-only analysis.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.preflight:
        parser.error("--preflight is required; this tool never writes or fits calibration")
    result = build_market_regime_calibration_evidence_once_report(
        hot_root=args.hot_root,
        max_outcome_rows=args.max_outcome_rows,
        max_trace_rows=args.max_trace_rows,
        max_total_bytes=args.max_total_bytes,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
