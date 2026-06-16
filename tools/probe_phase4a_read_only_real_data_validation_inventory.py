# path: ./tools/probe_phase4a_read_only_real_data_validation_inventory.py
# desc: Read-only bounded inventory probe for collected BTC / bitFlyer archive data.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.environ.get("BTC_TS_ROOT") or os.environ.get("BTC_TS_DATA_ROOT") or r"E:\btc_ts")
DATA_DIR = Path(os.environ.get("BTC_TS_DATA_DIR") or (DATA_ROOT / "data"))
OUT_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_real_data_validation_probe"
DEFAULT_OUT = OUT_DIR / "probe_phase4a_read_only_real_data_validation_inventory.out.json"

EXCHANGE = "bitflyer"
SYMBOL = "BTC_JPY"
CHANNELS = ("board_snapshot", "board_ws", "executions", "executions_ws")


def _iter_jsonl_files(date_dir: Path, *, max_files: int) -> Iterable[Path]:
    yielded = 0
    for pattern in ("*.jsonl", "*.jsonl.gz"):
        for path in sorted(date_dir.glob(pattern)):
            if yielded >= max_files:
                return
            yielded += 1
            yield path


def _read_jsonl_sample(path: Path, *, max_lines: int) -> Dict[str, Any]:
    # Plain jsonl only for first implementation. gz files are inventoried but not decompressed.
    if path.suffix == ".gz":
        return {
            "path": str(path),
            "readable": False,
            "skipped_reason": "gzip_sample_not_opened_in_first_probe",
            "line_count_read": 0,
            "json_ok_count": 0,
            "json_error_count": 0,
            "sample_keys": [],
        }

    line_count = 0
    json_ok_count = 0
    json_error_count = 0
    sample_keys: List[str] = []

    try:
        with path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                if line_count >= max_lines:
                    break
                line_count += 1
                stripped = raw.strip()
                if not stripped:
                    continue
                try:
                    value = json.loads(stripped)
                except Exception:
                    json_error_count += 1
                    continue
                json_ok_count += 1
                if isinstance(value, dict) and not sample_keys:
                    sample_keys = sorted(str(key) for key in value.keys())[:40]
    except Exception as exc:
        return {
            "path": str(path),
            "readable": False,
            "error": str(exc),
            "line_count_read": line_count,
            "json_ok_count": json_ok_count,
            "json_error_count": json_error_count,
            "sample_keys": sample_keys,
        }

    return {
        "path": str(path),
        "readable": True,
        "line_count_read": line_count,
        "json_ok_count": json_ok_count,
        "json_error_count": json_error_count,
        "sample_keys": sample_keys,
    }


def _channel_inventory(channel_dir: Path, *, max_dates: int, max_files_per_date: int, max_lines_per_file: int) -> Dict[str, Any]:
    date_dirs = sorted(path for path in channel_dir.glob("date=*") if path.is_dir())
    selected_dates = date_dirs[-max_dates:] if max_dates > 0 else []
    date_summaries: List[Dict[str, Any]] = []
    total_files_sampled = 0
    total_json_ok = 0
    total_json_error = 0

    for date_dir in selected_dates:
        files = list(_iter_jsonl_files(date_dir, max_files=max_files_per_date))
        samples = [_read_jsonl_sample(path, max_lines=max_lines_per_file) for path in files]
        total_files_sampled += len(samples)
        total_json_ok += sum(int(sample.get("json_ok_count", 0)) for sample in samples)
        total_json_error += sum(int(sample.get("json_error_count", 0)) for sample in samples)
        date_summaries.append(
            {
                "date": date_dir.name.removeprefix("date="),
                "file_count_sampled": len(samples),
                "samples": samples,
            }
        )

    return {
        "channel": channel_dir.name.removeprefix("channel="),
        "date_partition_count": len(date_dirs),
        "earliest_date": date_dirs[0].name.removeprefix("date=") if date_dirs else None,
        "latest_date": date_dirs[-1].name.removeprefix("date=") if date_dirs else None,
        "selected_date_count": len(selected_dates),
        "selected_dates": [path.name.removeprefix("date=") for path in selected_dates],
        "file_count_sampled": total_files_sampled,
        "json_ok_count": total_json_ok,
        "json_error_count": total_json_error,
        "date_summaries": date_summaries,
    }


def build_inventory(*, max_dates: int, max_files_per_date: int, max_lines_per_file: int) -> Dict[str, Any]:
    collector_raw = DATA_DIR / "collector_raw"
    target = collector_raw / "exchange=bitflyer" / "symbol=BTC_JPY"
    channels: Dict[str, Any] = {}
    failures: List[str] = []

    if not DATA_ROOT.exists():
        failures.append(f"DATA_ROOT missing: {DATA_ROOT}")
    if not DATA_DIR.exists():
        failures.append(f"DATA_DIR missing: {DATA_DIR}")
    if not collector_raw.exists():
        failures.append(f"collector_raw missing: {collector_raw}")
    if not target.exists():
        failures.append(f"BTC/bitFlyer target partition missing: {target}")

    for channel in CHANNELS:
        channel_dir = target / f"channel={channel}"
        if not channel_dir.exists():
            failures.append(f"channel partition missing: {channel}")
            channels[channel] = {"channel": channel, "exists": False}
            continue
        inventory = _channel_inventory(
            channel_dir,
            max_dates=max_dates,
            max_files_per_date=max_files_per_date,
            max_lines_per_file=max_lines_per_file,
        )
        inventory["exists"] = True
        channels[channel] = inventory

    total_json_ok = sum(int(item.get("json_ok_count", 0)) for item in channels.values() if isinstance(item, dict))
    total_json_error = sum(int(item.get("json_error_count", 0)) for item in channels.values() if isinstance(item, dict))

    return {
        "phase": "phase4a_read_only_real_data_validation_inventory_probe",
        "scope": {
            "exchange": EXCHANGE,
            "symbol": SYMBOL,
            "read_only": True,
            "bounded": True,
            "writes_only_to_tmp_work": True,
            "does_not_write_to_data_root": True,
            "does_not_write_to_d_drive_hot_runtime": True,
            "does_not_mutate_collector_state": True,
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
        "channels": channels,
        "totals": {
            "json_ok_count": total_json_ok,
            "json_error_count": total_json_error,
        },
        "failures": failures,
        "ok": len(failures) == 0 and total_json_ok > 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only bounded BTC/bitFlyer archive inventory probe")
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
            "phase": "phase4a_read_only_real_data_validation_inventory_probe",
            "failures": [f"output path must be under {allowed_root}: {out_path}"],
            "ok": False,
        }, ensure_ascii=False, indent=2))
        return 1

    summary = build_inventory(
        max_dates=max(1, args.max_dates),
        max_files_per_date=max(1, args.max_files_per_date),
        max_lines_per_file=max(1, args.max_lines_per_file),
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "phase": summary["phase"],
        "output_path": str(out_path),
        "channel_count": len(summary["channels"]),
        "total_json_ok_count": summary["totals"]["json_ok_count"],
        "total_json_error_count": summary["totals"]["json_error_count"],
        "failures": summary["failures"],
        "ok": summary["ok"],
    }, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
