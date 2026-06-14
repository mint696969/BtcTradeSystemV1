# path: ./btcts_next/src/btcts/autotrade/config/defaults.py
# desc: Initial AutoTrade FX parameter set defaults.

from __future__ import annotations

from .models import (
    AggressivenessProfile,
    ParameterSet,
    ParameterSetRegistry,
    ParameterSetStatus,
    ProductType,
)

INITIAL_PARAMETER_SET_ID = "params_fx_balanced_v0_1"
INITIAL_LOGIC_VERSION = "autotrade_logic_v0_1"


def initial_parameter_set_v0_1() -> ParameterSet:
    return ParameterSet(
        parameter_set_id=INITIAL_PARAMETER_SET_ID,
        parent_parameter_set_id=None,
        status=ParameterSetStatus.SHADOW,
        product_type=ProductType.FX,
        exchange="bitFlyer",
        symbol="BTC_JPY_FX_PRODUCT_CONFIRM_REQUIRED",
        created_at="2026-06-12 JST",
        created_by="human_gpt_design_session",
        change_reason="Initial FX balanced parameter set for AutoTrade shadow decision ledger MVP.",
        logic_version=INITIAL_LOGIC_VERSION,
        aggressiveness=AggressivenessProfile.BALANCED,
        notes=(
            "Initial values are designed to avoid permanent no-trade while keeping live execution gated. "
            "Exact FX product id and minimum order size must be confirmed from broker integration before live."
        ),
    )


def initial_registry() -> ParameterSetRegistry:
    return ParameterSetRegistry(
        active_live_parameter_set_id=None,
        active_shadow_parameter_set_ids=(INITIAL_PARAMETER_SET_ID,),
        last_known_good_parameter_set_id=None,
        rollback_parameter_set_id=None,
        retired_parameter_set_ids=(),
        pending_draft_parameter_set_id=None,
    )
