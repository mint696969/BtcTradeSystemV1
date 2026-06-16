# path: ./btcts_next/src/btcts/apps/sr_fx_execution_safety_harness_once.py
# desc: One-shot SR-FX execution safety harness writer. Read-only; no mode changes and no broker calls.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from btcts.autotrade.execution.safety_harness import evaluate_sr_fx_execution_safety_harness
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


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return float(raw)


def _env_int_or_none(name: str, default: int | None) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    if raw.lower() in {"none", "null", "-1"}:
        return None
    return int(raw)


def _target_mode() -> str:
    return os.getenv("BTCTS_LIVE_READINESS_TARGET_MODE", "LIVE_MIN_SIZE").strip().upper()


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
    safety_path = Path(
        os.getenv(
            "BTCTS_SR_FX_EXECUTION_SAFETY_HARNESS_PATH",
            str(roots["state"] / "autotrade" / "sr_fx_execution_safety_harness.json"),
        )
    )

    try:
        public_market = _read_json(public_path)
        private_readiness = _read_json(private_path)
        live_contract = _read_json(live_contract_path)
    except Exception as exc:
        out: Dict[str, object] = {
            "ok": False,
            "stage": "sr_fx_execution_safety_harness_once",
            "error": str(exc),
            "paths": {
                "public_market_readiness_path": str(public_path),
                "private_readiness_path": str(private_path),
                "live_readiness_contract_path": str(live_contract_path),
                "safety_harness_path": str(safety_path),
            },
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
        _write_json(safety_path, out)
        _print_json(out)
        return 0

    autotrade = evaluate_autotrade_live_readiness(
        current_mode=os.getenv("BTCTS_AUTOTRADE_CURRENT_MODE", "ARMED_DRY_RUN"),
        target_mode=_target_mode(),
        human_confirmed=_env_bool("BTCTS_AUTOTRADE_HUMAN_CONFIRMED", True),
        allow_warnings=_env_bool("BTCTS_AUTOTRADE_ALLOW_WARNINGS", True),
        max_observer_run_age_sec=_env_float("BTCTS_AUTOTRADE_MAX_OBSERVER_RUN_AGE_SEC", 120.0),
        max_lines=_env_int_or_none("BTCTS_AUTOTRADE_MAX_LINES", 1000),
        enforce_sr_fx_live_contract=True,
        sr_fx_live_contract_path=live_contract_path,
    )

    safety = evaluate_sr_fx_execution_safety_harness(
        public_market_readiness=public_market,
        private_readiness=private_readiness,
        live_readiness_contract=live_contract,
        autotrade_readiness={"readiness": autotrade.to_dict()},
        target_mode=_target_mode(),
        kill_switch_active=_env_bool("BTCTS_AUTOTRADE_KILL_SWITCH_ACTIVE", False),
        kill_switch_reason=os.getenv("BTCTS_AUTOTRADE_KILL_SWITCH_REASON") or None,
    )

    out = {
        "ok": safety.ok,
        "stage": "sr_fx_execution_safety_harness_once",
        "paths": {
            "public_market_readiness_path": str(public_path),
            "private_readiness_path": str(private_path),
            "live_readiness_contract_path": str(live_contract_path),
            "safety_harness_path": str(safety_path),
        },
        "autotrade_readiness": autotrade.to_dict(),
        "execution_safety_harness": safety.to_dict(),
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    }
    _write_json(safety_path, out)
    _print_json(out)
    # Blocked is expected before live. This diagnostic should not fail the shell pipeline.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
