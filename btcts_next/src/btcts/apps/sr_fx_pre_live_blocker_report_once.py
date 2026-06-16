# path: ./btcts_next/src/btcts/apps/sr_fx_pre_live_blocker_report_once.py
# desc: One-shot SR-FX pre-live blocker report writer. Read-only; no mode changes and no broker calls.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from btcts.autotrade.execution.pre_live_blocker_report import build_sr_fx_pre_live_blocker_report
from btcts.autotrade.readiness import evaluate_autotrade_live_readiness
from btcts.collector_vnext.config import ConfigValidationError, load_config
from btcts.collector_vnext.paths import ensure_dir


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def _read_json(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise RuntimeError(f"could not read JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON root must be object: {path}")
    return data


def _write_json(path: Path, data: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    roots = cfg.roots()
    public_path = roots["state"] / "public" / "bitflyer_fx_public_market_readiness.json"
    private_path = roots["state"] / "private" / "bitflyer_fx_readiness.json"
    live_contract_path = roots["state"] / "private" / "bitflyer_fx_live_readiness_contract.json"
    report_path = roots["state"] / "autotrade" / "sr_fx_pre_live_blocker_report.json"
    safety_harness_path = roots["state"] / "autotrade" / "sr_fx_execution_safety_harness.json"

    public_market = _read_json(public_path)
    private_readiness = _read_json(private_path)
    live_contract = _read_json(live_contract_path)
    safety_harness = _read_json(safety_harness_path) if safety_harness_path.exists() else None

    autotrade = evaluate_autotrade_live_readiness(
        current_mode=os.getenv("BTCTS_AUTOTRADE_CURRENT_MODE", "ARMED_DRY_RUN"),
        target_mode=os.getenv("BTCTS_LIVE_READINESS_TARGET_MODE", "LIVE_MIN_SIZE"),
        human_confirmed=_env_bool("BTCTS_AUTOTRADE_HUMAN_CONFIRMED", True),
        allow_warnings=_env_bool("BTCTS_AUTOTRADE_ALLOW_WARNINGS", True),
        enforce_sr_fx_live_contract=True,
        sr_fx_live_contract_path=live_contract_path,
    )

    report = build_sr_fx_pre_live_blocker_report(
        public_market_readiness=public_market,
        private_readiness=private_readiness,
        live_readiness_contract=live_contract,
        autotrade_readiness={"readiness": autotrade.to_dict()},
        execution_safety_harness=safety_harness,
    )

    out: Dict[str, object] = {
        "ok": report.ok,
        "stage": "sr_fx_pre_live_blocker_report_once",
        "paths": {
            "public_market_readiness_path": str(public_path),
            "private_readiness_path": str(private_path),
            "live_readiness_contract_path": str(live_contract_path),
            "report_path": str(report_path),
            "execution_safety_harness_path": str(safety_harness_path),
        },
        "report": report.to_dict(),
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    }
    _write_json(report_path, out)
    _print_json(out)
    # Blocked is expected before live. This diagnostic should not fail the shell pipeline.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
