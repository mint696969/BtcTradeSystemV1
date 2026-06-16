# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_runtime_loader.py
# desc: Guards loading active parameter bundle JSON from runtime registry.

from __future__ import annotations

import json

from btcts.autotrade.config import initial_parameter_bundle_v0_1
from btcts.autotrade.config.bundle_lifecycle import parameter_bundle_json_path
from btcts.autotrade.config.bundle_runtime_loader import (
    load_parameter_bundle_runtime,
    parameter_set_bundle_from_dict,
    read_parameter_set_bundle,
)
from btcts.autotrade.config.models import ParameterSetBundleRegistry
from btcts.autotrade.config.registry import write_bundle_registry, write_parameter_bundle


def test_parameter_set_bundle_from_dict_roundtrips_split_bundle() -> None:
    bundle = initial_parameter_bundle_v0_1()

    loaded = parameter_set_bundle_from_dict(bundle.to_dict())

    assert loaded.parameter_bundle_id == bundle.parameter_bundle_id
    assert loaded.regime_parameter_set_id == bundle.regime_parameter_set_id
    assert loaded.trade_parameter_set_id == bundle.trade_parameter_set_id
    assert loaded.status == bundle.status
    assert loaded.regime_parameter_set.thresholds.trend_strength_min == bundle.regime_parameter_set.thresholds.trend_strength_min
    assert loaded.trade_parameter_set.entry_quality.paper_threshold == bundle.trade_parameter_set.entry_quality.paper_threshold


def test_read_parameter_set_bundle_reads_stored_json(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    path = tmp_path / "bundle.json"
    write_parameter_bundle(path, bundle)

    loaded = read_parameter_set_bundle(path)

    assert loaded.parameter_bundle_id == bundle.parameter_bundle_id
    assert loaded.regime_parameter_set_id == bundle.regime_parameter_set_id
    assert loaded.trade_parameter_set_id == bundle.trade_parameter_set_id


def test_load_parameter_bundle_runtime_uses_active_shadow_registry(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    bundle_path = parameter_bundle_json_path(registry_path.parent, bundle.parameter_bundle_id)

    write_bundle_registry(
        registry_path,
        ParameterSetBundleRegistry(active_shadow_bundle_id=bundle.parameter_bundle_id),
    )
    write_parameter_bundle(bundle_path, bundle)

    result = load_parameter_bundle_runtime(registry_path=registry_path, stage="shadow")

    data = result.to_dict()
    assert result.found is True
    assert result.blocked_by == ()
    assert result.bundle is not None
    assert result.bundle.parameter_bundle_id == bundle.parameter_bundle_id
    assert data["ok"] is True
    assert data["would_send_to_broker"] is False
    assert data["bundle"]["parameter_bundle_id"] == bundle.parameter_bundle_id


def test_load_parameter_bundle_runtime_reports_missing_bundle_file(tmp_path) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    write_bundle_registry(
        registry_path,
        ParameterSetBundleRegistry(active_shadow_bundle_id="pb_missing"),
    )

    result = load_parameter_bundle_runtime(registry_path=registry_path, stage="shadow")

    assert result.found is False
    assert result.bundle is None
    assert result.bundle_id == "pb_missing"
    assert result.bundle_path is not None
    assert "parameter_bundle_file_missing" in result.blocked_by
    assert result.to_dict()["ok"] is False


def test_load_parameter_bundle_runtime_explicit_bundle_id_overrides_stage(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    bundle_path = parameter_bundle_json_path(registry_path.parent, bundle.parameter_bundle_id)

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "autotrade_parameter_bundle_registry.v1",
                "active_shadow_bundle_id": "pb_other",
                "active_paper_bundle_id": None,
                "active_live_bundle_id": None,
                "last_known_good_bundle_id": None,
                "rollback_bundle_id": None,
                "pending_draft_bundle_id": None,
                "retired_bundle_ids": [],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    write_parameter_bundle(bundle_path, bundle)

    result = load_parameter_bundle_runtime(
        registry_path=registry_path,
        stage="shadow",
        bundle_id=bundle.parameter_bundle_id,
    )

    assert result.found is True
    assert result.bundle is not None
    assert result.bundle.parameter_bundle_id == bundle.parameter_bundle_id
