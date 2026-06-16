# path: ./tools/test_phase4a_autotrade_milestone_b_parameter_sets_guard.py
# desc: Guard AutoTrade milestone B parameter-set schema, FX defaults, and temporal flow policy.

from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import (  # noqa: E402
    INITIAL_LOGIC_VERSION,
    INITIAL_PARAMETER_SET_ID,
    ParameterSetStatus,
    initial_parameter_set_v0_1,
    initial_registry,
)
from btcts.autotrade.config.registry import write_parameter_set, write_registry  # noqa: E402

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    registry = initial_registry()

    checks = {
        "initial_id": ps.parameter_set_id == INITIAL_PARAMETER_SET_ID,
        "logic_version": ps.logic_version == INITIAL_LOGIC_VERSION,
        "status_shadow": ps.status == ParameterSetStatus.SHADOW,
        "fx_product": ps.product_type.value == "FX",
        "exchange_bitflyer": ps.exchange == "bitFlyer",
        "fx_product_confirm_required": "CONFIRM_REQUIRED" in ps.symbol,
        "leverage_cap_2x": ps.margin_policy.leverage_cap == 2.0,
        "normal_margin_200": ps.margin_policy.normal_margin_target_pct == 200.0,
        "attack_floor_150": ps.margin_policy.attack_margin_floor_pct == 150.0,
        "hard_block_150": ps.margin_policy.hard_block_margin_pct == 150.0,
        "live_min_one_order": ps.exposure_policy.max_open_orders_live_min_size == 1,
        "live_min_no_add": ps.exposure_policy.max_add_count_live_min_size == 0,
        "balanced_threshold_not_no_trade_extreme": ps.entry_quality.live_threshold_balanced == 75,
        "watch_threshold_exists": ps.entry_quality.watch_threshold == 55,
        "forecast_5m": ps.forecast.horizon_sec == 300,
        "temporal_windows": ps.temporal_flow.windows_sec == (15, 30, 60, 180, 300),
        "temporal_flow_enabled": ps.temporal_flow.use_temporal_liquidity_flow and ps.temporal_flow.use_temporal_price_flow and ps.temporal_flow.use_temporal_pressure_flow,
        "temporal_pattern_flags_enabled": ps.temporal_flow.use_temporal_pattern_flags,
        "registry_shadow_active": registry.active_shadow_parameter_set_ids == (INITIAL_PARAMETER_SET_ID,),
        "registry_no_live_active_initially": registry.active_live_parameter_set_id is None,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    immutable = False
    try:
        ps.parameter_set_id = "mutated"  # type: ignore[misc]
    except FrozenInstanceError:
        immutable = True
    except Exception as exc:
        failures.append(f"unexpected immutability exception: {type(exc).__name__}: {exc}")
    if not immutable:
        failures.append("parameter set is not immutable")

    as_dict = ps.to_dict()
    dict_checks = {
        "dict_status_string": as_dict.get("status") == "shadow",
        "dict_product_type_string": as_dict.get("product_type") == "FX",
        "dict_temporal_flow_present": "temporal_flow" in as_dict,
        "dict_forecast_present": "forecast" in as_dict,
        "dict_margin_policy_present": "margin_policy" in as_dict,
        "dict_loss_limits_present": "loss_limits" in as_dict,
    }
    failures.extend(f"dict check failed: {name}" for name, ok in dict_checks.items() if not ok)

    tmp_dir = REPO_ROOT / "tmp/_autotrade_guard_milestone_b"
    param_path = tmp_dir / "sets" / f"{ps.parameter_set_id}.json"
    reg_path = tmp_dir / "registry.json"
    write_parameter_set(param_path, ps)
    write_registry(reg_path, registry)
    serialized_checks = {
        "parameter_set_written": param_path.exists(),
        "registry_written": reg_path.exists(),
        "parameter_set_json_valid": json.loads(param_path.read_text(encoding="utf-8"))["parameter_set_id"] == INITIAL_PARAMETER_SET_ID,
        "registry_json_valid": json.loads(reg_path.read_text(encoding="utf-8"))["active_shadow_parameter_set_ids"] == [INITIAL_PARAMETER_SET_ID],
    }
    failures.extend(f"serialization check failed: {name}" for name, ok in serialized_checks.items() if not ok)

    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone B: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_b_parameter_sets_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "fx_initial_parameter_set_present": all(checks.values()),
            "parameter_set_immutable": immutable,
            "parameter_set_serializable": all(dict_checks.values()) and all(serialized_checks.values()),
            "temporal_flow_policy_included": checks["temporal_windows"] and checks["temporal_flow_enabled"] and checks["temporal_pattern_flags_enabled"],
            "no_live_active_initially": checks["registry_no_live_active_initially"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "parameter_set_id": ps.parameter_set_id,
        "logic_version": ps.logic_version,
        "temporal_windows_sec": list(ps.temporal_flow.windows_sec),
        "entry_thresholds": {
            "watch": ps.entry_quality.watch_threshold,
            "paper": ps.entry_quality.paper_threshold,
            "balanced_live": ps.entry_quality.live_threshold_balanced,
            "conservative_live": ps.entry_quality.live_threshold_conservative,
            "opportunistic_live": ps.entry_quality.live_threshold_opportunistic,
        },
        "margin_policy": {
            "leverage_cap": ps.margin_policy.leverage_cap,
            "normal_margin_target_pct": ps.margin_policy.normal_margin_target_pct,
            "attack_margin_floor_pct": ps.margin_policy.attack_margin_floor_pct,
        },
        "checks": checks,
        "dict_checks": dict_checks,
        "serialized_checks": serialized_checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
