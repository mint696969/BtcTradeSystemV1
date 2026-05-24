# path: ./tools/probe_phase4a_broader_real_data_validation_review.py
# desc: Manual bounded broader real-data validation review probe for existing BTC / bitFlyer diagnostic outputs.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_real_data_validation_probe"
DEFAULT_INVENTORY = OUT_DIR / "probe_phase4a_read_only_real_data_validation_inventory.out.json"
DEFAULT_REPLAY_REPORT = OUT_DIR / "probe_phase4a_read_only_real_data_replay_report_validation.out.json"
DEFAULT_OUT = OUT_DIR / "probe_phase4a_broader_real_data_validation_review.out.json"

EXPECTED_CHANNELS = ("board_snapshot", "board_ws", "executions", "executions_ws")
BOARD_CHANNELS = {"board_snapshot", "board_ws"}
TRADE_CHANNELS = {"executions", "executions_ws"}


def _load_json(path: Path, failures: List[str], label: str) -> Dict[str, Any]:
    if not path.exists():
        failures.append(f"{label} missing: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"{label} invalid JSON: {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        failures.append(f"{label} must be JSON object: {path}")
        return {}
    return value


def _source_path_channel_date(path_text: str) -> Dict[str, Any]:
    channel = None
    date = None
    for part in Path(path_text).parts:
        if part.startswith("channel="):
            channel = part.removeprefix("channel=")
        if part.startswith("date="):
            date = part.removeprefix("date=")
    return {"path": path_text, "channel": channel, "date": date}


def _replay_source_coverage(replay: Dict[str, Any]) -> Dict[str, Any]:
    paths: List[str] = []
    for channel_summary in replay.get("channel_summaries", {}).values():
        # Replay/report probe stores per-channel counts but not full paths there.
        # Full source path count is still validated from totals; date coverage is inferred from inventory output.
        _ = channel_summary
    source_count = int(replay.get("totals", {}).get("source_path_count", 0) or 0)
    return {"source_path_count": source_count, "source_paths": paths}


def _channel_review(inventory: Dict[str, Any], replay: Dict[str, Any], failures: List[str]) -> Dict[str, Any]:
    inventory_channels = inventory.get("channels", {}) if isinstance(inventory.get("channels"), dict) else {}
    replay_channels = replay.get("channel_summaries", {}) if isinstance(replay.get("channel_summaries"), dict) else {}
    rows: Dict[str, Any] = {}

    for channel in EXPECTED_CHANNELS:
        inv = inventory_channels.get(channel, {}) if isinstance(inventory_channels.get(channel), dict) else {}
        rep = replay_channels.get(channel, {}) if isinstance(replay_channels.get(channel), dict) else {}
        missing: List[str] = []
        if not inv:
            missing.append("inventory_channel_missing")
        if not rep:
            missing.append("replay_channel_missing")
        if inv and inv.get("exists") is not True:
            missing.append("inventory_channel_not_existing")
        if rep and int(rep.get("json_error_count", 0) or 0) != 0:
            missing.append("replay_channel_json_errors")
        if inv and int(inv.get("json_error_count", 0) or 0) != 0:
            missing.append("inventory_channel_json_errors")
        if missing:
            failures.append(f"channel diagnostic issue: {channel}: {','.join(missing)}")

        rows[channel] = {
            "inventory_exists": inv.get("exists"),
            "date_partition_count": inv.get("date_partition_count"),
            "earliest_date": inv.get("earliest_date"),
            "latest_date": inv.get("latest_date"),
            "selected_dates": inv.get("selected_dates", []),
            "inventory_file_count_sampled": inv.get("file_count_sampled", 0),
            "inventory_json_ok_count": inv.get("json_ok_count", 0),
            "inventory_json_error_count": inv.get("json_error_count", 0),
            "replay_file_count_sampled": rep.get("file_count_sampled", 0),
            "replay_row_count": rep.get("replay_row_count", 0),
            "replay_json_ok_count": rep.get("json_ok_count", 0),
            "replay_json_error_count": rep.get("json_error_count", 0),
            "sample_payload_keys": rep.get("sample_payload_keys", []),
            "diagnostic_notes": missing,
        }

    extra_inventory = sorted(set(inventory_channels) - set(EXPECTED_CHANNELS))
    extra_replay = sorted(set(replay_channels) - set(EXPECTED_CHANNELS))
    if extra_inventory:
        failures.append(f"unexpected inventory channels: {extra_inventory}")
    if extra_replay:
        failures.append(f"unexpected replay channels: {extra_replay}")

    return {
        "expected_channels": list(EXPECTED_CHANNELS),
        "channel_count": len(rows),
        "rows": rows,
        "extra_inventory_channels": extra_inventory,
        "extra_replay_channels": extra_replay,
    }


def build_review(*, inventory_path: Path, replay_report_path: Path) -> Dict[str, Any]:
    failures: List[str] = []
    inventory = _load_json(inventory_path, failures, "inventory_output")
    replay = _load_json(replay_report_path, failures, "replay_report_validation_output")

    if inventory and inventory.get("ok") is not True:
        failures.append("inventory output ok must be true")
    if replay and replay.get("ok") is not True:
        failures.append("replay/report validation output ok must be true")

    inventory_totals = inventory.get("totals", {}) if isinstance(inventory.get("totals"), dict) else {}
    replay_totals = replay.get("totals", {}) if isinstance(replay.get("totals"), dict) else {}
    report_shape = replay.get("report_shape", {}) if isinstance(replay.get("report_shape"), dict) else {}
    session_summary = replay.get("session_summary", {}) if isinstance(replay.get("session_summary"), dict) else {}

    channel_review = _channel_review(inventory, replay, failures) if inventory and replay else {}

    inventory_json_ok = int(inventory_totals.get("json_ok_count", 0) or 0)
    inventory_json_error = int(inventory_totals.get("json_error_count", 0) or 0)
    replay_json_ok = int(replay_totals.get("json_ok_count", 0) or 0)
    replay_json_error = int(replay_totals.get("json_error_count", 0) or 0)
    replay_row_count = int(replay_totals.get("replay_row_count", 0) or 0)
    source_path_count = int(replay_totals.get("source_path_count", 0) or 0)

    if inventory_json_ok <= 0:
        failures.append("inventory json_ok_count must be positive")
    if replay_json_ok <= 0:
        failures.append("replay json_ok_count must be positive")
    if inventory_json_error != 0:
        failures.append(f"inventory json_error_count must be 0: {inventory_json_error}")
    if replay_json_error != 0:
        failures.append(f"replay json_error_count must be 0: {replay_json_error}")
    if replay_row_count != replay_json_ok:
        failures.append("replay_row_count must match replay json_ok_count")
    if source_path_count <= 0:
        failures.append("source_path_count must be positive")
    if report_shape.get("result_count") != replay_row_count:
        failures.append("report result_count must match replay_row_count")
    if session_summary.get("processed_count") != replay_row_count:
        failures.append("session processed_count must match replay_row_count")
    if report_shape.get("signal_count") != 0:
        failures.append("broader review input must remain signal-free diagnostic output")
    if report_shape.get("microstructure_event_count") != 0:
        failures.append("broader review input must remain microstructure-event-free diagnostic output")
    if report_shape.get("prediction_direction_summary") is not None:
        failures.append("broader review must not consume synthesized Direction summary")
    if report_shape.get("direction_replay_calibration_review_material") is not None:
        failures.append("broader review must not consume synthesized Direction review material")

    board_count = int(report_shape.get("board_count", 0) or 0)
    trade_count = int(report_shape.get("trade_count", 0) or 0)
    board_rows = 0
    trade_rows = 0
    for channel, row in (channel_review.get("rows", {}) if isinstance(channel_review, dict) else {}).items():
        if channel in BOARD_CHANNELS:
            board_rows += int(row.get("replay_row_count", 0) or 0)
        if channel in TRADE_CHANNELS:
            trade_rows += int(row.get("replay_row_count", 0) or 0)
    if board_count != board_rows:
        failures.append("report board_count must match board channel replay rows")
    if trade_count != trade_rows:
        failures.append("report trade_count must match trade channel replay rows")

    diagnostic_notes = []
    for channel, row in (channel_review.get("rows", {}) if isinstance(channel_review, dict) else {}).items():
        notes = row.get("diagnostic_notes", [])
        if notes:
            diagnostic_notes.append({"channel": channel, "notes": notes})

    return {
        "phase": "phase4a_broader_real_data_validation_review_probe",
        "scope": {
            "exchange": "bitflyer",
            "symbol": "BTC_JPY",
            "manual": True,
            "bounded": True,
            "diagnostic_only": True,
            "read_only_existing_outputs": True,
            "writes_only_to_tmp_work": True,
            "does_not_write_to_data_root": True,
            "does_not_write_to_d_drive_hot_runtime": True,
            "does_not_mutate_collector_state": True,
            "does_not_open_runtime_ui_market_engine_or_broker_order": True,
            "does_not_open_inference_or_training": True,
        },
        "inputs": {
            "inventory_output_path": str(inventory_path),
            "replay_report_validation_output_path": str(replay_report_path),
        },
        "totals": {
            "inventory_json_ok_count": inventory_json_ok,
            "inventory_json_error_count": inventory_json_error,
            "replay_json_ok_count": replay_json_ok,
            "replay_json_error_count": replay_json_error,
            "source_path_count": source_path_count,
            "replay_row_count": replay_row_count,
            "report_result_count": report_shape.get("result_count"),
            "report_board_count": board_count,
            "report_trade_count": trade_count,
            "session_processed_count": session_summary.get("processed_count"),
        },
        "channel_review": channel_review,
        "replay_report_diagnostic_only": {
            "signal_count": report_shape.get("signal_count"),
            "microstructure_event_count": report_shape.get("microstructure_event_count"),
            "prediction_direction_summary_is_none": report_shape.get("prediction_direction_summary") is None,
            "direction_replay_calibration_review_material_is_none": report_shape.get("direction_replay_calibration_review_material") is None,
        },
        "diagnostic_notes": diagnostic_notes,
        "failures": failures,
        "ok": len(failures) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual bounded broader real-data validation review probe")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--replay-report", type=Path, default=DEFAULT_REPLAY_REPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    out_path = args.out.resolve()
    allowed_root = OUT_DIR.resolve()
    if allowed_root not in [out_path, *out_path.parents]:
        print(json.dumps({
            "phase": "phase4a_broader_real_data_validation_review_probe",
            "failures": [f"output path must be under {allowed_root}: {out_path}"],
            "ok": False,
        }, ensure_ascii=False, indent=2))
        return 1

    summary = build_review(
        inventory_path=args.inventory.resolve(),
        replay_report_path=args.replay_report.resolve(),
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "phase": summary["phase"],
        "output_path": str(out_path),
        "channel_count": summary.get("channel_review", {}).get("channel_count"),
        "inventory_json_ok_count": summary["totals"]["inventory_json_ok_count"],
        "inventory_json_error_count": summary["totals"]["inventory_json_error_count"],
        "replay_json_ok_count": summary["totals"]["replay_json_ok_count"],
        "replay_json_error_count": summary["totals"]["replay_json_error_count"],
        "source_path_count": summary["totals"]["source_path_count"],
        "replay_row_count": summary["totals"]["replay_row_count"],
        "report_result_count": summary["totals"]["report_result_count"],
        "report_board_count": summary["totals"]["report_board_count"],
        "report_trade_count": summary["totals"]["report_trade_count"],
        "diagnostic_note_count": len(summary.get("diagnostic_notes", [])),
        "failures": summary["failures"],
        "ok": summary["ok"],
    }, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
