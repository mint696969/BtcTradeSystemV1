# path: ./btcts_next/src/btcts/replay/experiment_export.py
# desc: Export replay strategy experiment artifacts for later research and comparison.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .replay_io import ensure_dir, write_json, write_jsonl


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_strategy_experiment(
    *,
    experiment: Dict,
    out_root: Path,
) -> Dict[str, str]:
    name = str(experiment.get("name") or "strategy_experiment")
    stamp = _utc_stamp()

    session_dir = ensure_dir(out_root / f"{name}_{stamp}")

    regime_report = experiment.get("regime_report") or {}
    strategy_reports = experiment.get("strategy_reports") or []
    best_strategy = experiment.get("best_strategy") or {}

    regime_path = write_json(session_dir / "regime_report.json", regime_report)
    strategy_reports_path = write_jsonl(session_dir / "strategy_reports.jsonl", strategy_reports)
    best_strategy_path = write_json(session_dir / "best_strategy.json", best_strategy)

    summary = {
        "name": name,
        "created_at_utc": stamp,
        "result_count": int(experiment.get("result_count") or 0),
        "regime": regime_report.get("regime"),
        "best_strategy": best_strategy.get("strategy") if isinstance(best_strategy, dict) else None,
        "strategy_count": len(strategy_reports),
    }
    summary_path = write_json(session_dir / "experiment_summary.json", summary)

    manifest = {
        "name": name,
        "created_at_utc": stamp,
        "session_dir": str(session_dir),
        "regime_report_path": str(regime_path),
        "strategy_reports_path": str(strategy_reports_path),
        "best_strategy_path": str(best_strategy_path),
        "summary_path": str(summary_path),
    }
    manifest_path = write_json(session_dir / "manifest.json", manifest)

    return {
        "session_dir": str(session_dir),
        "regime_report_path": str(regime_path),
        "strategy_reports_path": str(strategy_reports_path),
        "best_strategy_path": str(best_strategy_path),
        "summary_path": str(summary_path),
        "manifest_path": str(manifest_path),
    }