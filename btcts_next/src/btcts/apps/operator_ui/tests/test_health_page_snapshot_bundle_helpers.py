# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_snapshot_bundle_helpers.py
# desc: Verify health_page snapshot bundle helpers prefer grouped bundles and keep flat fallback.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.views.health_page as page  # noqa: E402


def main() -> int:
    flat_snapshot = {
        "collector_state": {"status": {"mode": "RUNNING"}},
        "api_ws_series": [{"series": "flat"}],
        "api_continuity_rail": [{"rail": "flat-api"}],
        "ws_continuity_rail": [{"rail": "flat-ws"}],
        "recent_anomalies": [{"event": "flat"}],
        "health_digest": {"source": "flat"},
    }

    grouped_snapshot = {
        **flat_snapshot,
        "current_state_bundle": {
            "collector_state": {"status": {"mode": "GROUPED"}},
            "health_digest": {"source": "grouped"},
        },
        "timeline_bundle": {
            "api_ws_series": [{"series": "grouped"}],
        },
        "continuity_bundle": {
            "api_continuity_rail": [{"rail": "grouped-api"}],
            "ws_continuity_rail": [{"rail": "grouped-ws"}],
        },
        "anomaly_bundle": {
            "source_kind": "audit_recent_anomaly_feed",
            "feed_kind": "health_recent_anomalies",
            "max_items": 12,
            "items": [{"event": "grouped"}],
            "recent_anomalies": [{"event": "grouped"}],
        },
    }

    # grouped bundle 優先
    current_state_bundle = page._snapshot_current_state_bundle(grouped_snapshot)
    timeline_bundle = page._snapshot_timeline_bundle(grouped_snapshot)
    continuity_bundle = page._snapshot_continuity_bundle(grouped_snapshot)
    anomaly_bundle = page._snapshot_anomaly_bundle(grouped_snapshot)
    anomaly_items = page._snapshot_anomaly_items(grouped_snapshot)

    assert current_state_bundle["collector_state"]["status"]["mode"] == "GROUPED"
    assert timeline_bundle["api_ws_series"] == [{"series": "grouped"}]
    assert continuity_bundle["api_continuity_rail"] == [{"rail": "grouped-api"}]
    assert continuity_bundle["ws_continuity_rail"] == [{"rail": "grouped-ws"}]
    assert anomaly_bundle["recent_anomalies"] == [{"event": "grouped"}]
    assert anomaly_bundle["items"] == [{"event": "grouped"}]
    assert anomaly_items == [{"event": "grouped"}]

    # flat fallback
    flat_current_state_bundle = page._snapshot_current_state_bundle(flat_snapshot)
    flat_timeline_bundle = page._snapshot_timeline_bundle(flat_snapshot)
    flat_continuity_bundle = page._snapshot_continuity_bundle(flat_snapshot)
    flat_anomaly_bundle = page._snapshot_anomaly_bundle(flat_snapshot)
    flat_anomaly_items = page._snapshot_anomaly_items(flat_snapshot)

    assert flat_current_state_bundle is flat_snapshot
    assert flat_timeline_bundle is flat_snapshot
    assert flat_continuity_bundle is flat_snapshot
    assert flat_anomaly_bundle is flat_snapshot
    assert flat_anomaly_items == [{"event": "flat"}]

    captured_digests: list[object] = []
    original_builder = page.build_health_digest_ui_bundle

    try:
        def _fake_builder(digest):
            captured_digests.append(digest)
            return {
                "widget": {"digest": digest},
                "payload": {"source": digest.get("source") if isinstance(digest, dict) else None},
            }

        page.build_health_digest_ui_bundle = _fake_builder

        grouped_digest_bundle = page._snapshot_health_digest_ui_bundle(grouped_snapshot)
        flat_digest_bundle = page._snapshot_health_digest_ui_bundle(flat_snapshot)

        assert captured_digests[0] == {"source": "grouped"}
        assert grouped_digest_bundle["payload"]["source"] == "grouped"

        assert captured_digests[1] == {"source": "flat"}
        assert flat_digest_bundle["payload"]["source"] == "flat"
    finally:
        page.build_health_digest_ui_bundle = original_builder

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())