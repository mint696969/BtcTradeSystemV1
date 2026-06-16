# path: ./btcts_next/src/btcts/autotrade/config/defaults.py
# desc: Initial AutoTrade FX parameter set defaults.

from __future__ import annotations

from .models import (
    AggressivenessProfile,
    ParameterSet,
    ParameterSetBundle,
    ParameterSetBundleRegistry,
    ParameterSetBundleStatus,
    ParameterSetRegistry,
    ParameterSetStatus,
    ProductType,
    RegimeParameterSet,
    RegimeParameterSetStatus,
)

INITIAL_PARAMETER_SET_ID = "params_fx_balanced_v0_1"
INITIAL_REGIME_PARAMETER_SET_ID = "regime_fx_balanced_v0_1"
INITIAL_PARAMETER_BUNDLE_ID = "pb_fx_balanced_v0_1"
INITIAL_LOGIC_VERSION = "autotrade_logic_v0_1"


def initial_regime_parameter_set_v0_1() -> RegimeParameterSet:
    return RegimeParameterSet(
        regime_parameter_set_id=INITIAL_REGIME_PARAMETER_SET_ID,
        parent_regime_parameter_set_id=None,
        status=RegimeParameterSetStatus.SHADOW,
        product_type=ProductType.FX,
        exchange="bitFlyer",
        symbol="FX_BTC_JPY",
        created_at="2026-06-16 JST",
        created_by="human_gpt_design_session",
        change_reason="Initial FX balanced regime parameter set for market-condition judgment.",
        logic_version=INITIAL_LOGIC_VERSION,
        notes=(
            "Regime parameters are separated from trade parameters so market-condition "
            "classification can be reviewed, replayed, and tuned independently."
        ),
    )


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


def initial_parameter_bundle_v0_1() -> ParameterSetBundle:
    return ParameterSetBundle(
        parameter_bundle_id=INITIAL_PARAMETER_BUNDLE_ID,
        parent_parameter_bundle_id=None,
        status=ParameterSetBundleStatus.SHADOW,
        regime_parameter_set=initial_regime_parameter_set_v0_1(),
        trade_parameter_set=initial_parameter_set_v0_1(),
        created_at="2026-06-16 JST",
        created_by="human_gpt_design_session",
        change_reason="Initial bundle pairing separated regime and trade parameter sets.",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        product_code="FX_BTC_JPY",
        logic_version=INITIAL_LOGIC_VERSION,
        notes="Bundle is the replay/reproduction unit; regime and trade responsibilities remain separate.",
    )


def initial_bundle_registry() -> ParameterSetBundleRegistry:
    return ParameterSetBundleRegistry(
        active_shadow_bundle_id=INITIAL_PARAMETER_BUNDLE_ID,
        active_paper_bundle_id=None,
        active_live_bundle_id=None,
        last_known_good_bundle_id=None,
        rollback_bundle_id=None,
        pending_draft_bundle_id=None,
        retired_bundle_ids=(),
    )

