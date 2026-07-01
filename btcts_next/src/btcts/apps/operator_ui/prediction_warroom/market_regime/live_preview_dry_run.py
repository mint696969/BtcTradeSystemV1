# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/live_preview_dry_run.py
# desc: Read-only live-preview dry-run composer for market-regime cards. Explicit root only; no Streamlit mount, runtime writes, scheduler, broker, or ledger behavior.

from __future__ import annotations

from pathlib import Path
from typing import Any

from btcts.apps.operator_ui.prediction_warroom.market_regime.card_adapter import build_warroom_market_regime_card_adapter_packet
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle
from btcts.prediction.market_regime.inference import classify_market_regime_feature_bundle
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot

WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION = "prediction_warroom.market_regime_live_preview_dry_run.ps_q27l.v1"


def build_market_regime_live_preview_dry_run_packet(hot_root: str | Path, *, generated_at: str) -> dict[str, Any]:
    """Compose source snapshot -> feature bundle -> classifier -> WarRoom cards.

    This is intentionally an explicit-root, read-only dry run. It does not mount
    into WarRoom, does not import Streamlit, and does not write artifacts.
    Tests use tmp_path fixtures; production D-hot usage remains an explicit human
    action until a later scoped slice wires a preview path.
    """
    root = Path(hot_root)
    source_snapshot = build_market_regime_source_snapshot(root)
    feature_bundle = build_market_regime_feature_bundle(source_snapshot, generated_at=generated_at)
    prediction_packet = classify_market_regime_feature_bundle(feature_bundle, generated_at=generated_at)
    card_packet = build_warroom_market_regime_card_adapter_packet(prediction_packet)
    return {
        "ok": bool(card_packet.get("ok")),
        "dry_run_version": WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION,
        "generated_at": generated_at,
        "hot_root": str(root),
        "cards": card_packet.get("cards", []),
        "card_count": int(card_packet.get("card_count", 0)),
        "horizons": list(card_packet.get("horizons", [])),
        "source_snapshot_ok": source_snapshot.ok,
        "feature_bundle_available_signal_count": feature_bundle.available_signal_count(),
        "prediction_packet_logic_version": prediction_packet.logic_version,
        "card_adapter_version": card_packet.get("adapter_version"),
        "source_snapshot_missing_sources": list(source_snapshot.missing_sources),
        "source_snapshot_warnings": list(source_snapshot.warnings),
        "prediction_warnings": list(prediction_packet.warnings),
        "stage_versions": {
            "source_snapshot": source_snapshot.logic_version,
            "feature_bundle": feature_bundle.logic_version,
            "classifier": prediction_packet.logic_version,
            "card_adapter": card_packet.get("adapter_version"),
        },
        "market_regime_only": True,
        "live_preview_dry_run": True,
        "explicit_source_root_read_only": True,
        "ui_binding_added": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "renderer_changed": False,
        "streamlit_render_invoked_by_page": False,
        "live_data_connected": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }
