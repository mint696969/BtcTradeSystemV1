# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_real_dhot_preview_probe_q27n.py
# desc: PS-Q27N tests for explicit-root read-only real D-hot preview probe. Uses tmp_path fixture; no actual D-hot in tests.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.market_regime import (  # noqa: E402
    WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION,
    build_market_regime_real_dhot_preview_probe_packet,
    build_market_regime_real_dhot_preview_probe_summary,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
PROBE_MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/real_dhot_preview_probe.py"
FEATURE_BUILDER = REPO_ROOT / "btcts_next/src/btcts/prediction/market_regime/features/feature_builder.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_actual_like_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/175500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:55:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/175500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 15,
            "primary_label": "range_candidate",
            "values_snapshot": {
                "volatility_state": "compressed",
                "cross_venue_agreement": "confirmed",
            },
        },
        {
            "family": "market_regime",
            "horizon_sec": 86400,
            "primary_label": "range_candidate",
            "values_snapshot": {
                "volatility_state": "compressed",
                "cross_venue_agreement": "confirmed",
            },
        },
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9764512.0,
        "last_best_ask": 9765366.0,
        "last_spread": 854.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 22016, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def test_q27n_probe_reads_explicit_tmp_root_and_builds_cards(tmp_path: Path) -> None:
    _build_actual_like_fixture(tmp_path)
    packet = build_market_regime_real_dhot_preview_probe_packet(tmp_path, generated_at="2026-07-01T17:55:03Z")
    assert packet["ok"] is True
    assert packet["probe_version"] == WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION
    assert packet["real_d_hot_preview_probe"] is True
    assert packet["explicit_source_root_read_performed"] is True
    assert packet["source_snapshot_ok"] is True
    assert packet["card_count"] == 8
    assert packet["cards"][0]["regime_code"] == "RANGE"
    assert packet["cards"][0]["short_tag"] == "NO_DIRECTION"


def test_q27n_values_snapshot_fallback_preserves_real_forecast_driver_lines(tmp_path: Path) -> None:
    _build_actual_like_fixture(tmp_path)
    packet = build_market_regime_real_dhot_preview_probe_packet(tmp_path, generated_at="2026-07-01T17:55:03Z")
    first_detail = packet["cards"][0]["detail"]
    joined = "\n".join(first_detail["reason_lines"] + first_detail["source_lines"])
    assert "volatility_state:compressed" in joined
    assert "cross_venue_agreement:confirmed" in joined
    assert "values_snapshot" in FEATURE_BUILDER.read_text(encoding="utf-8-sig")


def test_q27n_probe_summary_is_compact_and_read_only(tmp_path: Path) -> None:
    _build_actual_like_fixture(tmp_path)
    packet = build_market_regime_real_dhot_preview_probe_packet(tmp_path, generated_at="2026-07-01T17:55:03Z")
    summary = build_market_regime_real_dhot_preview_probe_summary(packet)
    assert summary["ok"] is True
    assert summary["card_count"] == 8
    assert len(summary["cards"]) == 8
    assert set(summary["cards"][0]) == {"horizon", "regime_code", "confidence_percent", "freshness_badge", "short_tag", "background_tone"}
    assert summary["probe_read_only"] is True
    assert summary["probe_output_file_written"] is False
    assert summary["would_send_to_broker"] is False


def test_q27n_missing_root_degrades_without_write(tmp_path: Path) -> None:
    packet = build_market_regime_real_dhot_preview_probe_packet(tmp_path, generated_at="2026-07-01T17:55:03Z")
    assert packet["ok"] is True
    assert packet["source_snapshot_ok"] is False
    assert "latest_manifest" in packet["source_snapshot_missing_sources"]
    assert packet["card_count"] == 8
    assert {card["regime_code"] for card in packet["cards"]} == {"UNKNOWN"}
    assert packet["probe_output_file_written"] is False


def test_q27n_probe_flags_do_not_mount_or_execute(tmp_path: Path) -> None:
    _build_actual_like_fixture(tmp_path)
    packet = build_market_regime_real_dhot_preview_probe_packet(tmp_path, generated_at="2026-07-01T17:55:03Z")
    assert packet["ui_mount_requested"] is False
    assert packet["ui_binding_added"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["renderer_changed"] is False
    assert packet["streamlit_render_invoked_by_page"] is False
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert packet[key] is False


def test_q27n_does_not_mount_page_or_renderer() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    renderer_text = RENDERER.read_text(encoding="utf-8-sig")
    assert "build_market_regime_real_dhot_preview_probe_packet" not in page_text
    assert "WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION" not in page_text
    assert "build_market_regime_real_dhot_preview_probe_packet" not in renderer_text
    assert "WARROOM_MARKET_REGIME_REAL_DHOT_PREVIEW_PROBE_VERSION" not in renderer_text


def test_q27n_probe_module_has_no_streamlit_or_write_paths() -> None:
    text = PROBE_MODULE.read_text(encoding="utf-8-sig")
    forbidden = ("import streamlit", "from streamlit", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for token in forbidden:
        assert token not in text, f"forbidden token {token!r} found in probe module"
