# path: ./tools/export_market_engine_onboarding_input.py
# desc: Export collector canonical jsonl records into a single onboarding input jsonl.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name, "").strip()
    return raw if raw else default


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception as e:
                raise RuntimeError(f"invalid json at line {line_no}: {path}") from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def _wanted_record(record: dict[str, Any]) -> bool:
    record_type = str(record.get("record_type") or "")
    if record_type in {"market.orderbook.snapshot", "market.orderbook.diff"}:
        return True
    if record_type.startswith("stream."):
        return True
    return False


def _iter_input_files(input_root: Path) -> list[Path]:
    if input_root.is_file():
        return [input_root]
    return sorted(input_root.rglob("*.jsonl"))


def main() -> int:
    input_default = str(REPO_ROOT / "tmp" / "market_engine_onboarding_source")
    output_default = str(REPO_ROOT / "tmp" / "market_engine_onboarding_input.jsonl")

    primary_source = Path(_env_str("BTCTS_ONBOARDING_SOURCE", input_default)).resolve()
    extra_sources_raw = _env_str("BTCTS_ONBOARDING_EXTRA_SOURCES", "")

    source_roots: list[Path] = [primary_source]
    if extra_sources_raw:
        for raw in extra_sources_raw.split(";"):
            text = raw.strip()
            if text:
                source_roots.append(Path(text).resolve())

    output_path = Path(_env_str("BTCTS_ONBOARDING_OUTPUT_JSONL", output_default)).resolve()

    missing_roots = [path for path in source_roots if not path.exists()]
    if missing_roots:
        missing_text = ", ".join(str(path) for path in missing_roots)
        raise RuntimeError(f"source path not found: {missing_text}")

    input_files: list[Path] = []
    for root in source_roots:
        input_files.extend(_iter_input_files(root))

    input_files = sorted(dict.fromkeys(input_files))
    if not input_files:
        joined = ", ".join(str(path) for path in source_roots)
        raise RuntimeError(f"no jsonl files found under: {joined}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    kept = 0
    scanned = 0

    with output_path.open("w", encoding="utf-8", newline="\n") as out:
        for path in input_files:
            for row in _load_jsonl(path):
                scanned += 1
                if not _wanted_record(row):
                    continue
                out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                kept += 1

    print(json.dumps({
        "ok": True,
        "source_roots": [str(path) for path in source_roots],
        "output": str(output_path),
        "input_file_count": len(input_files),
        "scanned_records": scanned,
        "exported_records": kept,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())