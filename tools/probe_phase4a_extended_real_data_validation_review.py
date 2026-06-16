# path: ./tools/probe_phase4a_extended_real_data_validation_review.py
# desc: Manual bounded extended real-data validation review probe for BTC / bitFlyer archive diagnostics.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_real_data_validation_probe"
OUT_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_extended_real_data_validation_review"
DEFAULT_OUT = OUT_DIR / "probe_phase4a_extended_real_data_validation_review.out.json"
BASELINE_BROADER = BASELINE_DIR / "probe_phase4a_broader_real_data_validation_review.out.json"

EXPECTED_CHANNELS = ("board_snapshot", "board_ws", "executions", "executions_ws")


def _run_json(args: List[str], failures: List[str], label: str) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=1800,
    )
    parsed: Any = None
    parse_ok = False
    try:
        parsed = json.loads(proc.stdout)
        parse_ok = isinstance(parsed, dict)
    except Exception as exc:
        failures.append(f"{label} did not emit valid JSON: {exc}")
    ok = proc.returncode == 0 and parse_ok and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{label} must return ok true and failures []")
    return {
        "returncode": proc.returncode,
        "ok": ok,
        "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "failure_count": len(parsed.get("failures", [])) if isinstance(parsed, dict) else None,
        "stdout_tail": proc.stdout[-2200:],
        "stderr_tail": proc.stderr[-1200:],
        "parsed": parsed if isinstance(parsed, dict) else None,
    }


def _load_json(path: Path, failures: List[str], label: str) -> Dict[str, Any]:
    if not path.exists():
        failures.append(f"{label} missing: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"{label} invalid JSON: {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"{label} must be JSON object: {path}")
        return {}
    if data.get("ok") is not True or data.get("failures") != []:
        failures.append(f"{label} must be ok true and failures []")
    return data


def _compare_extended_to_baseline(*, baseline: Dict[str, Any], extended: Dict[str, Any], failures: List[str]) -> Dict[str, Any]:
    baseline_totals = baseline.get("totals", {}) if isinstance(baseline.get("totals"), dict) else {}
    extended_totals = extended.get("totals", {}) if isinstance(extended.get("totals"), dict) else {}
    baseline_channels = (baseline.get("channel_review", {}) or {}).get("rows", {}) if isinstance(baseline.get("channel_review"), dict) else {}
    extended_channels = (extended.get("channel_review", {}) or {}).get("rows", {}) if isinstance(extended.get("channel_review"), dict) else {}

    deltas = {}
    monotonic_checks = []
    for key in (
        "inventory_json_ok_count",
        "replay_json_ok_count",
        "source_path_count",
        "replay_row_count",
        "report_result_count",
        "report_board_count",
        "report_trade_count",
    ):
        baseline_value = int(baseline_totals.get(key, 0) or 0)
        extended_value = int(extended_totals.get(key, 0) or 0)
        delta = extended_value - baseline_value
        deltas[key] = {"baseline": baseline_value, "extended": extended_value, "delta": delta}
        ok = extended_value >= baseline_value
        monotonic_checks.append({"key": key, "ok": ok})
        if not ok:
            failures.append(f"extended total must be >= baseline: {key}: {extended_value} < {baseline_value}")

    channel_rows: Dict[str, Any] = {}
    for channel in EXPECTED_CHANNELS:
        base_row = baseline_channels.get(channel, {}) if isinstance(baseline_channels.get(channel), dict) else {}
        ext_row = extended_channels.get(channel, {}) if isinstance(extended_channels.get(channel), dict) else {}
        if not ext_row:
            failures.append(f"extended channel missing: {channel}")
        base_replay = int(base_row.get("replay_row_count", 0) or 0)
        ext_replay = int(ext_row.get("replay_row_count", 0) or 0)
        base_files = int(base_row.get("replay_file_count_sampled", 0) or 0)
        ext_files = int(ext_row.get("replay_file_count_sampled", 0) or 0)
        if ext_replay < base_replay:
            failures.append(f"extended channel replay rows must be >= baseline: {channel}: {ext_replay} < {base_replay}")
        if ext_files < base_files:
            failures.append(f"extended channel sampled files must be >= baseline: {channel}: {ext_files} < {base_files}")
        channel_rows[channel] = {
            "baseline_replay_row_count": base_replay,
            "extended_replay_row_count": ext_replay,
            "replay_row_delta": ext_replay - base_replay,
            "baseline_replay_file_count_sampled": base_files,
            "extended_replay_file_count_sampled": ext_files,
            "replay_file_delta": ext_files - base_files,
            "extended_selected_dates": ext_row.get("selected_dates", []),
            "extended_latest_date": ext_row.get("latest_date"),
            "extended_sample_payload_key_count": len(ext_row.get("sample_payload_keys", [])),
            "extended_diagnostic_notes": ext_row.get("diagnostic_notes", []),
        }

    return {
        "totals_delta": deltas,
        "monotonic_checks": monotonic_checks,
        "channel_rows": channel_rows,
    }


def build_extended_review(*, max_dates: int, max_files_per_date: int, max_lines_per_file: int, out: Path) -> Dict[str, Any]:
    failures: List[str] = []
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Child probes have their own tmp-output boundary fixed to BASELINE_DIR.
    # Keep these intermediate files there with unique extended names, while this
    # probe's final summary remains under OUT_DIR.
    inventory_out = BASELINE_DIR / "probe_phase4a_extended_inventory.out.json"
    replay_out = BASELINE_DIR / "probe_phase4a_extended_replay_report_validation.out.json"
    broader_out = BASELINE_DIR / "probe_phase4a_extended_broader_review.out.json"

    inventory_run = _run_json([
        "tools/probe_phase4a_read_only_real_data_validation_inventory.py",
        "--max-dates", str(max_dates),
        "--max-files-per-date", str(max_files_per_date),
        "--max-lines-per-file", str(max_lines_per_file),
        "--out", str(inventory_out),
    ], failures, "extended inventory probe")

    replay_run = _run_json([
        "tools/probe_phase4a_read_only_real_data_replay_report_validation.py",
        "--max-dates", str(max_dates),
        "--max-files-per-date", str(max_files_per_date),
        "--max-lines-per-file", str(max_lines_per_file),
        "--out", str(replay_out),
    ], failures, "extended replay/report validation probe")

    broader_run = _run_json([
        "tools/probe_phase4a_broader_real_data_validation_review.py",
        "--inventory", str(inventory_out),
        "--replay-report", str(replay_out),
        "--out", str(broader_out),
    ], failures, "extended broader review probe")

    baseline = _load_json(BASELINE_BROADER, failures, "baseline broader review output")
    extended_broader = _load_json(broader_out, failures, "extended broader review output")
    comparison = _compare_extended_to_baseline(baseline=baseline, extended=extended_broader, failures=failures) if baseline and extended_broader else {}

    totals = extended_broader.get("totals", {}) if isinstance(extended_broader.get("totals"), dict) else {}
    channel_review = extended_broader.get("channel_review", {}) if isinstance(extended_broader.get("channel_review"), dict) else {}
    diagnostic_only = extended_broader.get("replay_report_diagnostic_only", {}) if isinstance(extended_broader.get("replay_report_diagnostic_only"), dict) else {}

    if max_dates <= 2:
        failures.append("extended review max_dates must be greater than baseline default 2")
    if max_files_per_date < 2:
        failures.append("extended review max_files_per_date must be at least baseline default 2")
    if max_lines_per_file < 3:
        failures.append("extended review max_lines_per_file must be at least baseline default 3")
    if channel_review.get("channel_count") != 4:
        failures.append(f"extended broader channel_count must be 4: {channel_review.get('channel_count')}")
    if int(totals.get("inventory_json_error_count", -1)) != 0:
        failures.append("extended inventory_json_error_count must be 0")
    if int(totals.get("replay_json_error_count", -1)) != 0:
        failures.append("extended replay_json_error_count must be 0")
    if diagnostic_only.get("signal_count") != 0:
        failures.append("extended review must remain signal-free diagnostic output")
    if diagnostic_only.get("microstructure_event_count") != 0:
        failures.append("extended review must remain microstructure-event-free diagnostic output")
    if diagnostic_only.get("prediction_direction_summary_is_none") is not True:
        failures.append("extended review must not synthesize Direction summary")
    if diagnostic_only.get("direction_replay_calibration_review_material_is_none") is not True:
        failures.append("extended review must not synthesize Direction review material")

    return {
        "phase": "phase4a_extended_real_data_validation_review_probe",
        "scope": {
            "exchange": "bitflyer",
            "symbol": "BTC_JPY",
            "manual": True,
            "bounded": True,
            "diagnostic_only": True,
            "read_only_e_drive_archive_input": True,
            "writes_only_to_tmp_work": True,
            "does_not_write_to_data_root": True,
            "does_not_write_to_d_drive_hot_runtime": True,
            "does_not_mutate_collector_state": True,
            "does_not_open_runtime_ui_market_engine_or_broker_order": True,
            "does_not_open_inference_or_training": True,
        },
        "limits": {
            "max_dates": max_dates,
            "max_files_per_date": max_files_per_date,
            "max_lines_per_file": max_lines_per_file,
        },
        "inputs": {
            "baseline_broader_review_output": str(BASELINE_BROADER),
        },
        "outputs": {
            "inventory_output": str(inventory_out),
            "replay_report_validation_output": str(replay_out),
            "extended_broader_review_output": str(broader_out),
            "summary_output": str(out),
        },
        "runs": {
            "inventory": {k: v for k, v in inventory_run.items() if k != "parsed"},
            "replay_report_validation": {k: v for k, v in replay_run.items() if k != "parsed"},
            "broader_review": {k: v for k, v in broader_run.items() if k != "parsed"},
        },
        "totals": totals,
        "channel_review": channel_review,
        "replay_report_diagnostic_only": diagnostic_only,
        "baseline_comparison": comparison,
        "diagnostic_notes": extended_broader.get("diagnostic_notes", []) if isinstance(extended_broader, dict) else [],
        "failures": failures,
        "ok": len(failures) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual bounded extended real-data validation review probe")
    parser.add_argument("--max-dates", type=int, default=3)
    parser.add_argument("--max-files-per-date", type=int, default=2)
    parser.add_argument("--max-lines-per-file", type=int, default=3)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    out_path = args.out.resolve()
    allowed_roots = [OUT_DIR.resolve(), BASELINE_DIR.resolve()]
    if not any(root in [out_path, *out_path.parents] for root in allowed_roots):
        print(json.dumps({
            "phase": "phase4a_extended_real_data_validation_review_probe",
            "failures": [f"output path must be under one of {[str(root) for root in allowed_roots]}: {out_path}"],
            "ok": False,
        }, ensure_ascii=False, indent=2))
        return 1

    summary = build_extended_review(
        max_dates=max(1, args.max_dates),
        max_files_per_date=max(1, args.max_files_per_date),
        max_lines_per_file=max(1, args.max_lines_per_file),
        out=out_path,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "phase": summary["phase"],
        "output_path": str(out_path),
        "max_dates": summary["limits"]["max_dates"],
        "max_files_per_date": summary["limits"]["max_files_per_date"],
        "max_lines_per_file": summary["limits"]["max_lines_per_file"],
        "channel_count": summary.get("channel_review", {}).get("channel_count"),
        "inventory_json_ok_count": summary.get("totals", {}).get("inventory_json_ok_count"),
        "inventory_json_error_count": summary.get("totals", {}).get("inventory_json_error_count"),
        "replay_json_ok_count": summary.get("totals", {}).get("replay_json_ok_count"),
        "replay_json_error_count": summary.get("totals", {}).get("replay_json_error_count"),
        "source_path_count": summary.get("totals", {}).get("source_path_count"),
        "replay_row_count": summary.get("totals", {}).get("replay_row_count"),
        "report_board_count": summary.get("totals", {}).get("report_board_count"),
        "report_trade_count": summary.get("totals", {}).get("report_trade_count"),
        "diagnostic_note_count": len(summary.get("diagnostic_notes", [])),
        "failures": summary["failures"],
        "ok": summary["ok"],
    }, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
