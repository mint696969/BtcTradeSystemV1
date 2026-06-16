# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_operator_ui_visibility.py
# desc: Guards parameter bundle runtime read-only projection helpers used by Operator UI AutoTrade page.

from __future__ import annotations

from btcts.apps.operator_ui.views.autotrade_page import _parameter_bundle_runtime_summary_view


def test_parameter_bundle_runtime_summary_view_projects_registry_fields() -> None:
    payload = {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "event_count": 3,
        "latest_event_type": "bundle_activated_live",
        "latest_event_ts": "2026-06-16T21:00:00+09:00",
        "registry": {
            "active_shadow_bundle_id": "pb_shadow",
            "active_paper_bundle_id": "pb_paper",
            "active_live_bundle_id": "pb_live",
            "last_known_good_bundle_id": "pb_good",
            "rollback_bundle_id": "pb_rollback",
            "pending_draft_bundle_id": "pb_draft",
            "retired_bundle_ids": ["pb_old"],
        },
        "warnings": [],
        "blocked_by": [],
        "would_send_to_broker": False,
    }

    view = _parameter_bundle_runtime_summary_view(payload)

    assert view["schema_version"] == "autotrade_parameter_bundle_runtime_status.v1"
    assert view["registry_exists"] is True
    assert view["event_ledger_exists"] is True
    assert view["event_count"] == 3
    assert view["latest_event_type"] == "bundle_activated_live"
    assert view["active_shadow_bundle_id"] == "pb_shadow"
    assert view["active_paper_bundle_id"] == "pb_paper"
    assert view["active_live_bundle_id"] == "pb_live"
    assert view["last_known_good_bundle_id"] == "pb_good"
    assert view["rollback_bundle_id"] == "pb_rollback"
    assert view["pending_draft_bundle_id"] == "pb_draft"
    assert view["retired_bundle_ids"] == ["pb_old"]
    assert view["would_send_to_broker"] is False
    assert view["read_only"] is True


def test_parameter_bundle_runtime_summary_view_handles_missing_registry() -> None:
    view = _parameter_bundle_runtime_summary_view(
        {
            "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
            "registry_exists": False,
            "event_ledger_exists": False,
            "event_count": 0,
            "warnings": ["parameter_bundle_registry_missing"],
            "blocked_by": [],
        }
    )

    assert view["registry_exists"] is False
    assert view["event_ledger_exists"] is False
    assert view["active_live_bundle_id"] is None
    assert view["warnings"] == ["parameter_bundle_registry_missing"]
    assert view["would_send_to_broker"] is False
    assert view["read_only"] is True
