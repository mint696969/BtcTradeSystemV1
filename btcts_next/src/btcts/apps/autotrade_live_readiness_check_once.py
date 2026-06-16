# path: ./btcts_next/src/btcts/apps/autotrade_live_readiness_check_once.py
# desc: One-shot AutoTrade live readiness check. Read-only; no mode changes and no broker calls.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from btcts.autotrade.readiness import evaluate_autotrade_live_readiness
from btcts.collector_vnext.config import ConfigValidationError, load_config


def _print_json(data: Dict[str, object]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


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


def main() -> int:
    try:
        cfg = load_config()
    except ConfigValidationError as exc:
        _print_json({"ok": False, "stage": "load_config", "error": str(exc)})
        return 2

    current_mode = os.getenv("BTCTS_AUTOTRADE_CURRENT_MODE", "ARMED_DRY_RUN")
    target_mode = os.getenv("BTCTS_LIVE_READINESS_TARGET_MODE", "LIVE_MIN_SIZE")
    contract_path = Path(
        os.getenv(
            "BTCTS_SR_FX_LIVE_CONTRACT_PATH",
            str(cfg.roots()["state"] / "private" / "bitflyer_fx_live_readiness_contract.json"),
        )
    )

    readiness = evaluate_autotrade_live_readiness(
        current_mode=current_mode,
        target_mode=target_mode,
        human_confirmed=_env_bool("BTCTS_AUTOTRADE_HUMAN_CONFIRMED", True),
        allow_warnings=_env_bool("BTCTS_AUTOTRADE_ALLOW_WARNINGS", True),
        max_observer_run_age_sec=_env_float("BTCTS_AUTOTRADE_MAX_OBSERVER_RUN_AGE_SEC", 120.0),
        max_lines=_env_int_or_none("BTCTS_AUTOTRADE_MAX_LINES", 1000),
        enforce_sr_fx_live_contract=True,
        sr_fx_live_contract_path=contract_path,
    )

    out: Dict[str, object] = {
        "ok": readiness.ready,
        "stage": "autotrade_live_readiness_check_once",
        "current_mode": readiness.current_mode.value,
        "target_mode": readiness.target_mode.value,
        "sr_fx_live_contract_path": str(contract_path),
        "readiness": readiness.to_dict(),
        "would_send_to_broker": False,
        "read_only": True,
        "mode_changed": False,
    }
    _print_json(out)
    # Not-ready is expected until public/private/account/risk/flags/sender/runtime are all ready.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
