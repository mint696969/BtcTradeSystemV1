# path: ./tools/report_market_engine_short_soak.py
# desc: Render a compact human-readable summary from market_engine short-soak observer JSON output.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import sys
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    obj = json.loads(text)
    return obj if isinstance(obj, dict) else {}


def _fmt_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def _fmt_map(title: str, data: dict[str, Any]) -> list[str]:
    lines = [title]
    if not data:
        lines.append("  - (empty)")
        return lines
    for key, value in data.items():
        lines.append(f"  - {key}: {value}")
    return lines


def build_report(summary: dict[str, Any]) -> str:
    gate_checks = summary.get("gate_checks") or {}
    trust_counts = summary.get("trust_counts") or {}
    boundary_counts = summary.get("boundary_counts") or {}
    continuity_counts = summary.get("continuity_counts") or {}

    latest_best_bid = summary.get("latest_best_bid")
    latest_best_ask = summary.get("latest_best_ask")
    latest_spread = summary.get("latest_spread")

    crossed_detected = False
    if latest_best_bid is not None and latest_best_ask is not None:
        try:
            crossed_detected = float(latest_best_bid) > float(latest_best_ask)
        except Exception:
            crossed_detected = False

    lines: list[str] = []
    lines.append("=== MARKET ENGINE SHORT SOAK REPORT ===")
    lines.append(f"overall_ok: {_fmt_bool(bool(summary.get('ok')))}")
    lines.append(f"started_at: {summary.get('started_at')}")
    lines.append(f"finished_at: {summary.get('finished_at')}")
    lines.append(f"observed_seconds: {summary.get('observed_seconds')}")
    lines.append(f"output_path: {summary.get('output_path')}")
    lines.append(f"record_count: {summary.get('record_count')}")
    lines.append("")

    lines.append("[Latest State]")
    lines.append(f"  - trust_state: {summary.get('latest_trust_state')}")
    lines.append(f"  - boundary_reason: {summary.get('latest_boundary_reason')}")
    lines.append(f"  - continuity_state: {summary.get('latest_continuity_state')}")
    lines.append(f"  - best_bid: {latest_best_bid}")
    lines.append(f"  - best_ask: {latest_best_ask}")
    lines.append(f"  - spread: {latest_spread}")
    lines.append(f"  - mid_price: {summary.get('latest_mid_price')}")
    lines.append(f"  - ui_caption: {summary.get('ui_caption')}")
    lines.append(f"  - crossed_book_detected: {crossed_detected}")
    lines.append("")

    lines.extend(_fmt_map("[Trust Counts]", trust_counts))
    lines.append("")
    lines.extend(_fmt_map("[Boundary Counts]", boundary_counts))
    lines.append("")
    lines.extend(_fmt_map("[Continuity Counts]", continuity_counts))
    lines.append("")

    lines.append("[Gate Checks]")
    if not gate_checks:
        lines.append("  - (empty)")
    else:
        for key, value in gate_checks.items():
            lines.append(f"  - {key}: {_fmt_bool(bool(value))}")
    lines.append("")

    lines.append("[Operator Interpretation]")
    if not summary.get("ok"):
        lines.append("  - short soak gate is NOT satisfied.")
    else:
        lines.append("  - short soak gate minimum checks are satisfied.")

    if crossed_detected:
        lines.append("  - crossed book detected in latest state. investigate before longer soak.")
    else:
        lines.append("  - latest top-of-book is not crossed.")

    latest_trust = str(summary.get("latest_trust_state") or "")
    latest_boundary = str(summary.get("latest_boundary_reason") or "")
    if latest_trust in {"broken", "quarantined"}:
        lines.append("  - latest trust state is degraded. do not advance to weekly soak.")
    elif latest_boundary not in {"", "none"}:
        lines.append("  - boundary condition is currently visible. verify recovery behavior.")
    else:
        lines.append("  - latest state looks operationally usable for continued observation.")

    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python .\\tools\\report_market_engine_short_soak.py <observer_json_file>")
        return 2

    src = Path(sys.argv[1]).resolve()
    if not src.exists():
        print(f"file not found: {src}")
        return 2

    summary = _load_json(src)
    print(build_report(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())