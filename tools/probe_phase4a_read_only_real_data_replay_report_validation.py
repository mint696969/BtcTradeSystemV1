# path: ./tools/probe_phase4a_read_only_real_data_replay_report_validation.py
# desc: Read-only bounded real-data replay/report validation probe for BTC / bitFlyer archive samples.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from btcts.replay.replay_report import build_replay_report
from btcts.replay.replay_session import ReplaySession


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("BTC_TS_ROOT") or os.environ.get("BTC_TS_DATA_ROOT") or r"E:\btc_ts")
DATA_DIR = Path(os.environ.get("BTC_TS_DATA_DIR") or (DATA_ROOT / "data"))
OUT_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_real_data_validation_probe"
DEFAULT_OUT = OUT_DIR / "probe_phase4a_read_only_real_data_replay_report_validation.out.json"

EXCHANGE = "bitflyer"
SYMBOL = "BTC_JPY"
CHANNELS = ("board_snapshot", "board_ws", "executions", "executions_ws")
BOARD_CHANNELS = {"board_snapshot", "board_ws"}
TRADE_CHANNELS = {"executions", "executions_ws"}


def _iter_jsonl_files(date_dir: Path, *, max_files: int) -> Iterable[Path]:
    yielded = 0
    for pattern in ("*.jsonl", "*.jsonl.gz"):
        for path in sorted(date_dir.glob(pattern)):
            if yielded >= max_files:
                return
            yielded += 1
            yield path


def _read_jsonl_records(path: Path, *, max_lines: int) -> Dict[str, Any]:
    if path.suffix == ".gz":
        return {
            "path": str(path),
            "records": [],
            "json_ok_count": 0,
            "json_error_count": 0,
            "skipped_reason": "gzip_sample_not_opened_in_first_probe",
        }

    records: List[Dict[str, Any]] = []
    json_error_count = 0
    with path.open("r", encoding="utf-8") as fh:
        for index, raw in enumerate(fh):
            if index >= max_lines:
                break
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except Exception:
                json_error_count += 1
                continue
            if isinstance(value, dict):
                records.append(value)
    return {
        "path": str(path),
        "records": records,
        "json_ok_count": len(records),
        "json_error_count": json_error_count,
    }


def _selected_channel_files(channel: str, *, max_dates: int, max_files_per_date: int) -> List[Path]:
    channel_dir = DATA_DIR / "collector_raw" / "exchange=bitflyer" / "symbol=BTC_JPY" / f"channel={channel}"
    date_dirs = sorted(path for path in channel_dir.glob("date=*") if path.is_dir()) if channel_dir.exists() else []
    selected_dates = date_dirs[-max_dates:] if max_dates > 0 else []
    files: List[Path] = []
    for date_dir in selected_dates:
        files.extend(list(_iter_jsonl_files(date_dir, max_files=max_files_per_date)))
    return files


def _record_to_replay_row(channel: str, record: Dict[str, Any]) -> Dict[str, Any]:
    envelope = {
        "channel": record.get("channel"),
        "record_type": record.get("record_type"),
        "exchange": record.get("exchange"),
        "symbol": record.get("symbol"),
        "market": record.get("market"),
        "instrument_id": record.get("instrument_id"),
        "event_ts": record.get("event_ts"),
        "ingest_ts": record.get("ingest_ts"),
        "record_id": record.get("record_id"),
        "schema_contract": record.get("schema_contract"),
        "schema_version": record.get("schema_version"),
        "payload_contract_version": record.get("payload_contract_version"),
    }
    payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}

    if channel in BOARD_CHANNELS:
        return {
            "kind": "board",
            "source_channel": channel,
            "source_envelope": envelope,
            "result": {
                "signal": None,
                "events": [],
                "payload_keys": sorted(str(key) for key in payload.keys())[:40],
                "read_only_real_data_validation": True,
            },
        }

    return {
        "kind": "trade",
        "source_channel": channel,
        "source_envelope": envelope,
        "microstructure": [],
        "payload_keys": sorted(str(key) for key in payload.keys())[:40],
        "read_only_real_data_validation": True,
    }


def build_validation(*, max_dates: int, max_files_per_date: int, max_lines_per_file: int) -> Dict[str, Any]:
    failures: List[str] = []
    collector_raw = DATA_DIR / "collector_raw"
    target = collector_raw / "exchange=bitflyer" / "symbol=BTC_JPY"

    if not DATA_ROOT.exists():
        failures.append(f"DATA_ROOT missing: {DATA_ROOT}")
    if not DATA_DIR.exists():
        failures.append(f"DATA_DIR missing: {DATA_DIR}")
    if not collector_raw.exists():
        failures.append(f"collector_raw missing: {collector_raw}")
    if not target.exists():
        failures.append(f"BTC/bitFlyer target partition missing: {target}")

    source_paths: List[str] = []
    replay_rows: List[Dict[str, Any]] = []
    channel_summaries: Dict[str, Any] = {}
    total_json_ok = 0
    total_json_error = 0

    for channel in CHANNELS:
        files = _selected_channel_files(channel, max_dates=max_dates, max_files_per_date=max_files_per_date)
        channel_json_ok = 0
        channel_json_error = 0
        channel_rows = 0
        sample_payload_keys: List[str] = []
        for path in files:
            source_paths.append(str(path))
            sample = _read_jsonl_records(path, max_lines=max_lines_per_file)
            channel_json_ok += int(sample.get("json_ok_count", 0))
            channel_json_error += int(sample.get("json_error_count", 0))
            for record in sample.get("records", []):
                row = _record_to_replay_row(channel, record)
                replay_rows.append(row)
                channel_rows += 1
                if not sample_payload_keys:
                    sample_payload_keys = list(row.get("result", {}).get("payload_keys", []) if row.get("kind") == "board" else row.get("payload_keys", []))
        total_json_ok += channel_json_ok
        total_json_error += channel_json_error
        channel_summaries[channel] = {
            "file_count_sampled": len(files),
            "json_ok_count": channel_json_ok,
            "json_error_count": channel_json_error,
            "replay_row_count": channel_rows,
            "sample_payload_keys": sample_payload_keys,
        }

    session = ReplaySession(name="phase4a_read_only_real_data_replay_report_validation", source_paths=source_paths)
    for row in replay_rows:
        session.add(row)

    report = build_replay_report(
        name="phase4a_read_only_real_data_replay_report_validation",
        source_paths=source_paths,
        results=replay_rows,
    )

    report_shape = {
        "name": report.get("name"),
        "result_count": report.get("result_count"),
        "board_count": report.get("board_count"),
        "trade_count": report.get("trade_count"),
        "signal_count": report.get("signal_count"),
        "microstructure_event_count": report.get("microstructure_event_count"),
        "event_name_counts": report.get("event_name_counts"),
        "prediction_direction_summary": report.get("prediction_direction_summary"),
        "direction_replay_calibration_review_material": report.get("direction_replay_calibration_review_material"),
    }
    session_summary = session.summary()

    expected_board_count = sum(channel_summaries[channel]["replay_row_count"] for channel in BOARD_CHANNELS)
    expected_trade_count = sum(channel_summaries[channel]["replay_row_count"] for channel in TRADE_CHANNELS)

    if total_json_ok <= 0:
        failures.append("no real-data JSON records were read")
    if total_json_error != 0:
        failures.append(f"JSON errors found: {total_json_error}")
    if report_shape["result_count"] != len(replay_rows):
        failures.append("report result_count does not match replay rows")
    if report_shape["board_count"] != expected_board_count:
        failures.append("report board_count does not match board channel rows")
    if report_shape["trade_count"] != expected_trade_count:
        failures.append("report trade_count does not match trade channel rows")
    if session_summary.get("processed_count") != len(replay_rows):
        failures.append("session processed_count does not match replay rows")
    if report_shape.get("signal_count") != 0:
        failures.append("read-only validation rows must not produce signals")
    if report_shape.get("microstructure_event_count") != 0:
        failures.append("read-only validation rows must not produce microstructure events")
    if report_shape.get("prediction_direction_summary") is not None:
        failures.append("real-data replay/report validation must not synthesize Direction summary")
    if report_shape.get("direction_replay_calibration_review_material") is not None:
        failures.append("real-data replay/report validation must not synthesize Direction review material")

    return {
        "phase": "phase4a_read_only_real_data_replay_report_validation_probe",
        "scope": {
            "exchange": EXCHANGE,
            "symbol": SYMBOL,
            "read_only": True,
            "manual": True,
            "bounded": True,
            "writes_only_to_tmp_work": True,
            "does_not_write_to_data_root": True,
            "does_not_write_to_d_drive_hot_runtime": True,
            "does_not_mutate_collector_state": True,
            "does_not_open_runtime_ui_market_engine_or_broker_order": True,
        },
        "limits": {
            "max_dates": max_dates,
            "max_files_per_date": max_files_per_date,
            "max_lines_per_file": max_lines_per_file,
        },
        "paths": {
            "data_root": str(DATA_ROOT),
            "data_dir": str(DATA_DIR),
            "collector_raw": str(collector_raw),
            "target_partition": str(target),
            "output_path": str(DEFAULT_OUT),
        },
        "channel_summaries": channel_summaries,
        "totals": {
            "json_ok_count": total_json_ok,
            "json_error_count": total_json_error,
            "replay_row_count": len(replay_rows),
            "source_path_count": len(source_paths),
        },
        "session_summary": session_summary,
        "report_shape": report_shape,
        "failures": failures,
        "ok": len(failures) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only bounded real-data replay/report validation probe")
    parser.add_argument("--max-dates", type=int, default=2)
    parser.add_argument("--max-files-per-date", type=int, default=2)
    parser.add_argument("--max-lines-per-file", type=int, default=3)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    out_path = args.out
    try:
        out_path = out_path.resolve()
    except Exception:
        pass

    allowed_root = OUT_DIR.resolve()
    if allowed_root not in [out_path, *out_path.parents]:
        print(json.dumps({
            "phase": "phase4a_read_only_real_data_replay_report_validation_probe",
            "failures": [f"output path must be under {allowed_root}: {out_path}"],
            "ok": False,
        }, ensure_ascii=False, indent=2))
        return 1

    summary = build_validation(
        max_dates=max(1, args.max_dates),
        max_files_per_date=max(1, args.max_files_per_date),
        max_lines_per_file=max(1, args.max_lines_per_file),
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "phase": summary["phase"],
        "output_path": str(out_path),
        "source_path_count": summary["totals"]["source_path_count"],
        "replay_row_count": summary["totals"]["replay_row_count"],
        "json_ok_count": summary["totals"]["json_ok_count"],
        "json_error_count": summary["totals"]["json_error_count"],
        "report_result_count": summary["report_shape"]["result_count"],
        "report_board_count": summary["report_shape"]["board_count"],
        "report_trade_count": summary["report_shape"]["trade_count"],
        "failures": summary["failures"],
        "ok": summary["ok"],
    }, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
