# path: ./btcts_next/src/btcts/apps/operator_ui/health_snapshot_read_model.py
# desc: Compose Operator UI Health snapshot read model from already-built bounded bundles.

from __future__ import annotations

from typing import Any

HEALTH_SNAPSHOT_READ_MODEL_VERSION = "health_snapshot_read_model.v1"
HEALTH_SNAPSHOT_BUNDLE_KEYS = (
    "current_state_bundle",
    "timeline_bundle",
    "continuity_bundle",
    "anomaly_bundle",
    "page_meta_bundle",
)


def build_health_snapshot_read_model(
    *,
    range_key: str,
    current_state_bundle: dict[str, Any],
    timeline_bundle: dict[str, Any],
    continuity_bundle: dict[str, Any],
    anomaly_bundle: dict[str, Any],
    page_meta_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Return the backwards-compatible Health snapshot read model.

    This module is intentionally pure composition.  It must not read audit
    files, scan data roots, call Streamlit, mutate collector runtime state, or
    own upstream collector/market contracts.  The caller provides already-built
    bounded bundles; this function only preserves legacy top-level keys and
    attaches the explicit nested bundle boundaries.
    """
    bundles = {
        "current_state_bundle": current_state_bundle,
        "timeline_bundle": timeline_bundle,
        "continuity_bundle": continuity_bundle,
        "anomaly_bundle": anomaly_bundle,
        "page_meta_bundle": page_meta_bundle,
    }

    snapshot: dict[str, Any] = {}
    for key in HEALTH_SNAPSHOT_BUNDLE_KEYS:
        bundle = bundles[key]
        snapshot.update(dict(bundle or {}))

    snapshot.update(bundles)
    snapshot["health_snapshot_read_model"] = {
        "source_kind": "operator_ui_health_snapshot_read_model",
        "version": HEALTH_SNAPSHOT_READ_MODEL_VERSION,
        "range_key": range_key,
        "bundle_keys": list(HEALTH_SNAPSHOT_BUNDLE_KEYS),
        "compose_existing_bundles_only_no_io": True,
        "views_are_render_only": True,
    }
    return snapshot
