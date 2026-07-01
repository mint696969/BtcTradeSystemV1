# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/preview_binding.py
# desc: Gated WarRoom market-regime preview binding. Disabled by default; no Streamlit mount, scheduler, broker, ledger, or runtime writes.

from __future__ import annotations

from pathlib import Path
from typing import Any

from .live_preview_dry_run import build_market_regime_live_preview_dry_run_packet

WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION = "prediction_warroom.market_regime_preview_binding.ps_q27m.v1"


def _safety_flags() -> dict[str, bool]:
    return {
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }


def build_market_regime_warroom_preview_binding_packet(
    *,
    preview_enabled: bool = False,
    hot_root: str | Path | None = None,
    generated_at: str,
) -> dict[str, Any]:
    """Return a gated preview binding packet for market-regime cards.

    The default path is disabled and intentionally does not read any source root.
    The enabled path requires an explicit root and delegates to the Q27L dry-run
    composer. This module does not mount WarRoom UI or write artifacts.
    """
    base: dict[str, Any] = {
        "ok": True,
        "binding_version": WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION,
        "generated_at": generated_at,
        "market_regime_only": True,
        "preview_binding_gated": True,
        "preview_enabled": bool(preview_enabled),
        "default_disabled": True,
        "explicit_source_root_required": True,
        "explicit_source_root_read_performed": False,
        "dry_run_invoked": False,
        "card_count": 0,
        "horizons": [],
        "cards": [],
        "disabled_reason": "preview_enabled_false" if not preview_enabled else "",
        "missing_required_inputs": [],
        "ui_binding_added": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "renderer_changed": False,
        "streamlit_render_invoked_by_page": False,
        "live_data_connected": False,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
    }
    base.update(_safety_flags())

    if not preview_enabled:
        return base

    if hot_root is None or str(hot_root) == "":
        base["ok"] = False
        base["disabled_reason"] = "explicit_hot_root_required"
        base["missing_required_inputs"] = ["hot_root"]
        return base

    dry_run_packet = build_market_regime_live_preview_dry_run_packet(Path(hot_root), generated_at=generated_at)
    base.update({
        "ok": bool(dry_run_packet.get("ok")),
        "disabled_reason": "",
        "explicit_source_root_read_performed": True,
        "dry_run_invoked": True,
        "hot_root": str(hot_root),
        "dry_run_version": dry_run_packet.get("dry_run_version"),
        "stage_versions": dict(dry_run_packet.get("stage_versions", {})),
        "source_snapshot_ok": bool(dry_run_packet.get("source_snapshot_ok")),
        "source_snapshot_missing_sources": list(dry_run_packet.get("source_snapshot_missing_sources", [])),
        "source_snapshot_warnings": list(dry_run_packet.get("source_snapshot_warnings", [])),
        "prediction_warnings": list(dry_run_packet.get("prediction_warnings", [])),
        "feature_bundle_available_signal_count": int(dry_run_packet.get("feature_bundle_available_signal_count", 0)),
        "card_count": int(dry_run_packet.get("card_count", 0)),
        "horizons": list(dry_run_packet.get("horizons", [])),
        "cards": list(dry_run_packet.get("cards", [])),
        "live_data_connected": False,
        "ui_binding_added": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "renderer_changed": False,
        "streamlit_render_invoked_by_page": False,
    })
    base.update(_safety_flags())
    return base
