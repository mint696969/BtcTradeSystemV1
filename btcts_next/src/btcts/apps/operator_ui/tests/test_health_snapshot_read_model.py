# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_snapshot_read_model.py
# desc: Verify Health snapshot read-model composer preserves legacy top-level keys and explicit bundle boundaries.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.health_snapshot_read_model import (  # noqa: E402
    HEALTH_SNAPSHOT_BUNDLE_KEYS,
    HEALTH_SNAPSHOT_READ_MODEL_VERSION,
    build_health_snapshot_read_model,
)


def main() -> int:
    current_state_bundle = {
        "collector_state": {"mode": "unified"},
        "health_digest": {"digest_type": "health_digest"},
    }
    timeline_bundle = {
        "api_ws_series": [{"series": "api"}],
        "rate_overlay": [{"series": "rate"}],
        "layer3_series": [{"series": "layer3"}],
    }
    continuity_bundle = {
        "api_continuity_rail": [{"rail": "api"}],
        "ws_continuity_rail": [{"rail": "ws"}],
    }
    anomaly_bundle = {
        "source_kind": "audit_recent_anomaly_feed",
        "items": [{"event": "gap"}],
        "recent_anomalies": [{"event": "gap"}],
    }
    page_meta_bundle = {
        "selected_range_key": "1h",
        "paths": {"logs_dir": "D:/logs"},
    }

    snapshot = build_health_snapshot_read_model(
        range_key="1h",
        current_state_bundle=current_state_bundle,
        timeline_bundle=timeline_bundle,
        continuity_bundle=continuity_bundle,
        anomaly_bundle=anomaly_bundle,
        page_meta_bundle=page_meta_bundle,
    )

    assert snapshot["collector_state"] == {"mode": "unified"}
    assert snapshot["api_ws_series"] == [{"series": "api"}]
    assert snapshot["api_continuity_rail"] == [{"rail": "api"}]
    assert snapshot["recent_anomalies"] == [{"event": "gap"}]
    assert snapshot["selected_range_key"] == "1h"

    assert snapshot["current_state_bundle"] == current_state_bundle
    assert snapshot["timeline_bundle"] == timeline_bundle
    assert snapshot["continuity_bundle"] == continuity_bundle
    assert snapshot["anomaly_bundle"] == anomaly_bundle
    assert snapshot["page_meta_bundle"] == page_meta_bundle

    read_model = snapshot["health_snapshot_read_model"]
    assert read_model["source_kind"] == "operator_ui_health_snapshot_read_model"
    assert read_model["version"] == HEALTH_SNAPSHOT_READ_MODEL_VERSION
    assert read_model["range_key"] == "1h"
    assert read_model["bundle_keys"] == list(HEALTH_SNAPSHOT_BUNDLE_KEYS)
    assert read_model["compose_existing_bundles_only_no_io"] is True
    assert read_model["views_are_render_only"] is True

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
