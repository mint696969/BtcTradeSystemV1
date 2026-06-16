# path: ./tools/test_phase4a_autotrade_milestone_dn_pre_live_operational_decision_lock_guard.py
# desc: Guard pre-live operational decisions after Phase 3 closure: spot-as-signal / FX-as-execution and configurable safety policies.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_DOC = REPO_ROOT / "tmp/gpt_room/memory/decisions/2026-06-13_autotrade_pre_live_operational_decision_lock.md"
BOUNDARY_DOC = REPO_ROOT / "tmp/docs/architecture/AUTOTRADE_PRE_LIVE_OPERATIONAL_BOUNDARY_2026-06-13.md"
DM_GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_dm_phase3_shadow_mode_closure_guard.py"
COLLECTOR_CONFIG = REPO_ROOT / "btcts_next/src/btcts/collector_vnext/config.py"
MARKET_ENGINE_CONFIG = REPO_ROOT / "btcts_next/src/btcts/market_engine/config.py"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)

REQUIRED_DECISION_TOKENS = (
    "Real trading is bitFlyer FX only",
    "Spot real trading is not considered",
    "spot-as-signal / FX-as-execution",
    "AutoTrade may not treat existing spot defaults as live execution identity",
    "Spot data is allowed as signal, never as execution target",
    "FX market data acquisition is required early",
    "live readiness blocks if FX data/product identity is missing",
    "emergency_market_order_enabled = false",
    "market_order_entry_enabled = false",
    "Long and short are both first-class strategy sides",
    "HALT_NEW",
    "HALT_AND_CANCEL",
    "EMERGENCY_FLATTEN",
    "leverage_cap = 2.0",
    "max_loss_per_trade_pct_of_margin = 0.25",
    "minimum_required_edge = spread_cost + fee_estimate + slippage_buffer + profile_min_edge",
    "Live parameters are not edited in place",
    "No FX product/account confirmation, no live mode",
)

REQUIRED_BOUNDARY_TOKENS = (
    "spot-as-signal / FX-as-execution",
    "execution_market_type = FX",
    "execution_product_code = unconfirmed_in_repo",
    "spot_execution_allowed = false",
    "spot_reference_input",
    "fx_execution_market_input",
    "FX product code missing",
    "execution market identity equals spot market identity",
    "emergency_market_order_enabled = false",
    "kill_switch_default = HALT_NEW",
    "long_short_strategy_sides = both_first_class",
    "fx_market_data_required_early = true",
)


def main() -> int:
    failures: list[str] = []
    decision_text = DECISION_DOC.read_text(encoding="utf-8") if DECISION_DOC.exists() else ""
    boundary_text = BOUNDARY_DOC.read_text(encoding="utf-8") if BOUNDARY_DOC.exists() else ""
    collector_text = COLLECTOR_CONFIG.read_text(encoding="utf-8")
    market_engine_text = MARKET_ENGINE_CONFIG.read_text(encoding="utf-8")

    checks = {
        "phase3_closure_guard_exists": DM_GUARD.exists(),
        "decision_doc_exists": DECISION_DOC.exists(),
        "boundary_doc_exists": BOUNDARY_DOC.exists(),
        "decision_doc_locks_fx_only_execution_and_spot_signal_policy": all(token in decision_text for token in REQUIRED_DECISION_TOKENS),
        "boundary_doc_declares_unconfirmed_fx_identity_blocks_live": all(token in boundary_text for token in REQUIRED_BOUNDARY_TOKENS),
        "repo_current_defaults_are_explicitly_spot_and_not_mistaken_for_fx": all(token in collector_text for token in ('market: str = "spot"', 'symbol: str = "BTC_JPY"', 'instrument_id: str = "bitflyer.spot.BTC_JPY"')) and all(token in market_engine_text for token in ('symbol_raw = _env_str("BTCTS_MARKET_ENGINE_SYMBOL", "BTC_JPY")', 'instrument_id = _env_str("BTCTS_MARKET_ENGINE_INSTRUMENT_ID", "bitflyer.spot.BTC_JPY")')),
        "decision_requires_configurable_not_silent_policy_changes": all(token in decision_text for token in ("Future adjustment is allowed only by versioned policy/config change", "Future adjustment is allowed only through versioned parameter/policy changes", "staged parameters", "immutable parameter_set_id")),
        "decision_keeps_long_and_short_in_scope": all(token in decision_text for token in ("Long and short are both first-class strategy sides", "Shadow and Paper should evaluate both long and short candidates", "Live Minimum Size may support both sides")),
        "decision_preserves_conservative_initial_emergency_and_kill_defaults": all(token in decision_text for token in ("emergency_market_order_enabled = false", "market_order_entry_enabled = false", "HALT_NEW", "HALT_AND_CANCEL", "EMERGENCY_FLATTEN")),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DN: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dn_pre_live_operational_decision_lock_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "phase3_closure_guard_exists": checks["phase3_closure_guard_exists"],
            "decision_doc_exists": checks["decision_doc_exists"],
            "boundary_doc_exists": checks["boundary_doc_exists"],
            "decision_doc_locks_fx_only_execution_and_spot_signal_policy": checks["decision_doc_locks_fx_only_execution_and_spot_signal_policy"],
            "boundary_doc_declares_unconfirmed_fx_identity_blocks_live": checks["boundary_doc_declares_unconfirmed_fx_identity_blocks_live"],
            "repo_current_defaults_are_explicitly_spot_and_not_mistaken_for_fx": checks["repo_current_defaults_are_explicitly_spot_and_not_mistaken_for_fx"],
            "decision_requires_configurable_not_silent_policy_changes": checks["decision_requires_configurable_not_silent_policy_changes"],
            "decision_keeps_long_and_short_in_scope": checks["decision_keeps_long_and_short_in_scope"],
            "decision_preserves_conservative_initial_emergency_and_kill_defaults": checks["decision_preserves_conservative_initial_emergency_and_kill_defaults"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "decision_doc": str(DECISION_DOC.relative_to(REPO_ROOT)),
        "boundary_doc": str(BOUNDARY_DOC.relative_to(REPO_ROOT)),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
