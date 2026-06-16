# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_models.py
# desc: Guards split regime/trade parameter sets and bundle-level replay identity.

from __future__ import annotations

import json

from btcts.autotrade.config import (
    INITIAL_PARAMETER_BUNDLE_ID,
    INITIAL_PARAMETER_SET_ID,
    INITIAL_REGIME_PARAMETER_SET_ID,
    initial_bundle_registry,
    initial_parameter_bundle_v0_1,
)
from btcts.autotrade.config.registry import write_bundle_registry, write_parameter_bundle


def test_initial_parameter_bundle_separates_regime_and_trade_sets() -> None:
    bundle = initial_parameter_bundle_v0_1()

    assert bundle.parameter_bundle_id == INITIAL_PARAMETER_BUNDLE_ID
    assert bundle.regime_parameter_set_id == INITIAL_REGIME_PARAMETER_SET_ID
    assert bundle.trade_parameter_set_id == INITIAL_PARAMETER_SET_ID
    assert bundle.regime_parameter_set_id != bundle.trade_parameter_set_id

    data = bundle.to_dict()
    assert data["schema_version"] == "autotrade_parameter_bundle.v1"
    assert data["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert data["product_code"] == "FX_BTC_JPY"
    assert data["regime_parameter_set"]["kind"] == "regime"
    assert data["trade_parameter_set"]["kind"] == "trade"
    assert data["trade_parameter_set"]["parameter_set_id"] == INITIAL_PARAMETER_SET_ID
    assert "entry_quality" in data["trade_parameter_set"]
    assert "thresholds" in data["regime_parameter_set"]


def test_initial_bundle_registry_tracks_bundle_not_single_threshold_set() -> None:
    registry = initial_bundle_registry()
    data = registry.to_dict()

    assert data["schema_version"] == "autotrade_parameter_bundle_registry.v1"
    assert data["active_shadow_bundle_id"] == INITIAL_PARAMETER_BUNDLE_ID
    assert data["active_live_bundle_id"] is None
    assert data["rollback_bundle_id"] is None


def test_parameter_bundle_serialization_roundtrip(tmp_path) -> None:
    bundle_path = tmp_path / "parameter_bundle.json"
    registry_path = tmp_path / "parameter_bundle_registry.json"

    bundle = initial_parameter_bundle_v0_1()
    registry = initial_bundle_registry()

    write_parameter_bundle(bundle_path, bundle)
    write_bundle_registry(registry_path, registry)

    bundle_data = json.loads(bundle_path.read_text(encoding="utf-8"))
    registry_data = json.loads(registry_path.read_text(encoding="utf-8"))

    assert bundle_data["parameter_bundle_id"] == INITIAL_PARAMETER_BUNDLE_ID
    assert bundle_data["regime_parameter_set"]["regime_parameter_set_id"] == INITIAL_REGIME_PARAMETER_SET_ID
    assert bundle_data["trade_parameter_set"]["parameter_set_id"] == INITIAL_PARAMETER_SET_ID
    assert registry_data["active_shadow_bundle_id"] == INITIAL_PARAMETER_BUNDLE_ID
