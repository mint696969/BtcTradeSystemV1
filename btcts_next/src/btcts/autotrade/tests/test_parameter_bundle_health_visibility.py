# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_health_visibility.py
# desc: Guards read-only parameter bundle runtime status visibility in AutoTrade health.

from __future__ import annotations

from btcts.autotrade.config.bundle_runtime_store import initialize_default_parameter_bundle_runtime
from btcts.autotrade.health import build_autotrade_runtime_health_snapshot


def test_health_snapshot_includes_missing_parameter_bundle_runtime_status(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    snapshot = build_autotrade_runtime_health_snapshot(max_lines=0, max_observer_run_age_sec=1.0)
    data = snapshot.to_dict()
    status = data["parameter_bundle_runtime"]

    assert status["schema_version"] == "autotrade_parameter_bundle_runtime_status.v1"
    assert status["would_send_to_broker"] is False
    assert status["registry_exists"] is False
    assert status["event_ledger_exists"] is False
    assert "parameter_bundle_registry_missing" in status["warnings"]
    assert "parameter_bundle_event_ledger_missing" in status["warnings"]
    assert not (runtime_root / "autotrade" / "parameter_sets" / "registry.json").exists()


def test_health_snapshot_reports_initialized_parameter_bundle_runtime_status(monkeypatch, tmp_path) -> None:
    runtime_root = tmp_path / "btc_ts_hot"
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(runtime_root))

    initialized = initialize_default_parameter_bundle_runtime(
        event_ts="2026-06-16T20:00:00+09:00",
        reason="Initialize before health visibility.",
        created_by="human_gpt",
        source_decision_ids=("dec_health_bundle",),
        gpt_review_ids=("gpt_health_bundle",),
        human_approval_id="approval_health_bundle",
    )

    snapshot = build_autotrade_runtime_health_snapshot(max_lines=0, max_observer_run_age_sec=1.0)
    status = snapshot.to_dict()["parameter_bundle_runtime"]

    assert status["registry_exists"] is True
    assert status["event_ledger_exists"] is True
    assert status["registry"]["active_shadow_bundle_id"] == initialized.registry.active_shadow_bundle_id
    assert status["event_count"] == 1
    assert status["latest_event_type"] == "bundle_created"
    assert status["recent_events"][0]["parameter_bundle_id"] == initialized.registry.active_shadow_bundle_id
    assert status["would_send_to_broker"] is False
