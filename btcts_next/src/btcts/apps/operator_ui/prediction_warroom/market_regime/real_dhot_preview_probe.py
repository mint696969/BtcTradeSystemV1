# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/real_dhot_preview_probe.py
# desc: Explicit-root read-only market-regime real D-hot preview probe. No Streamlit mount, scheduler, broker, ledger, or runtime writes.

from __future__ import annotations

from pathlib import Path
from typing import Any

from .preview_binding import build_market_regime_warroom_preview_binding_packet

WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION = "prediction_warroom.market_regime_real_dhot_preview_probe.ps_q27n.v1"


def build_market_regime_real_dhot_preview_probe_packet(hot_root: str | Path, *, generated_at: str) -> dict[str, Any]:
    """Run the gated preview binding against an explicit hot root in read-only mode.

    The caller must pass the root explicitly. This helper does not mount WarRoom,
    does not import Streamlit, and does not write probe output artifacts.
    """
    binding_packet = build_market_regime_warroom_preview_binding_packet(
        preview_enabled=True,
        hot_root=Path(hot_root),
        generated_at=generated_at,
    )
    packet = dict(binding_packet)
    packet.update({
        "probe_version": WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION,
        "real_d_hot_preview_probe": True,
        "explicit_source_root_required": True,
        "explicit_source_root_read_performed": bool(binding_packet.get("explicit_source_root_read_performed")),
        "probe_read_only": True,
        "probe_output_file_written": False,
        "ui_mount_requested": False,
        "ui_binding_added": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "renderer_changed": False,
        "streamlit_render_invoked_by_page": False,
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
    })
    return packet


def build_market_regime_real_dhot_preview_probe_summary(packet: dict[str, Any]) -> dict[str, Any]:
    """Return a compact operator-readable probe summary without card detail bulk."""
    cards = list(packet.get("cards", [])) if isinstance(packet.get("cards"), list) else []
    compact_cards = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        compact_cards.append({
            "horizon": card.get("horizon"),
            "regime_code": card.get("regime_code"),
            "confidence_percent": card.get("confidence_percent"),
            "freshness_badge": card.get("freshness_badge"),
            "short_tag": card.get("short_tag"),
            "background_tone": card.get("background_tone"),
        })
    return {
        "ok": bool(packet.get("ok")),
        "probe_version": packet.get("probe_version"),
        "hot_root": packet.get("hot_root"),
        "source_snapshot_ok": bool(packet.get("source_snapshot_ok")),
        "source_snapshot_missing_sources": list(packet.get("source_snapshot_missing_sources", [])),
        "source_snapshot_warnings": list(packet.get("source_snapshot_warnings", [])),
        "prediction_warnings": list(packet.get("prediction_warnings", [])),
        "card_count": int(packet.get("card_count", 0)),
        "horizons": list(packet.get("horizons", [])),
        "cards": compact_cards,
        "probe_read_only": bool(packet.get("probe_read_only")),
        "probe_output_file_written": bool(packet.get("probe_output_file_written")),
        "warroom_page_mounted": bool(packet.get("warroom_page_mounted")),
        "renderer_changed": bool(packet.get("renderer_changed")),
        "would_send_to_broker": bool(packet.get("would_send_to_broker")),
    }
