# path: ./tools/verify_phase4a_prediction_system_ps_q21k_warroom_fresh_badge_read_model.py
# desc: PS-Q21K read-only verification that D-hot latest prediction read model feeds WarRoom display packet and PS-Q21E data freshness badge as fresh/non-stale. No writes, no scheduler/producer enablement, no AutoTrade/broker.

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION,
    WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION,
    build_latest_prediction_warroom_display_panel_packet,
    latest_prediction_warroom_data_freshness_badge_packet,
    latest_prediction_warroom_refresh_live_badge_packet,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (  # noqa: E402
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
    load_latest_prediction_warroom_read_model,
)

VERIFY_VERSION = "prediction_warroom.warroom_fresh_badge_read_model_confirmation.ps_q21k.v1"
DEFAULT_HOT_ROOT = Path(r"D:\btc_ts_hot")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_warroom_fresh_badge_read_model_confirmation(
    *,
    read_model: Mapping[str, Any] | None,
    display_packet: Mapping[str, Any] | None,
    data_badge_packet: Mapping[str, Any] | None,
    live_badge_packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    model = _as_mapping(read_model or {})
    panel = _as_mapping(display_packet or {})
    data_badge = _as_mapping(data_badge_packet or {})
    live_badge = _as_mapping(live_badge_packet or {})
    data_fresh = data_badge.get("data_freshness_badge_fresh") is True
    data_delayed = data_badge.get("data_freshness_badge_delayed") is True
    data_non_stale = bool(data_fresh or data_delayed)
    panel_ok = panel.get("ok") is True and panel.get("prediction_row_count", 0) and not panel.get("panel_failures")
    live_ok = live_badge.get("refresh_live_badge_active") is True
    safety_ok = bool(
        panel.get("prediction_artifact_write_allowed") is False
        and panel.get("runtime_artifact_write_allowed") is False
        and panel.get("status_artifact_write_allowed") is False
        and panel.get("scheduler_enabled") is False
        and panel.get("producer_enabled") is False
        and panel.get("autotrade_trigger_allowed") is False
        and panel.get("broker_private_api_allowed") is False
        and panel.get("would_send_to_broker") is False
    )
    ok = bool(model.get("ok") is True and panel_ok and data_non_stale and live_ok and safety_ok)
    return {
        "ok": ok,
        "verify_version": VERIFY_VERSION,
        "verification_state": "warroom_read_model_badge_fresh_or_delayed_non_stale" if ok else "warroom_read_model_badge_attention",
        "read_model_version": str(model.get("read_model_version") or ""),
        "read_model_version_expected": LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
        "read_model_ok": model.get("ok") is True,
        "read_model_generated_at": str(model.get("generated_at") or ""),
        "read_model_age_sec": model.get("age_sec"),
        "read_model_freshness_state": str(model.get("freshness_state") or ""),
        "read_model_record_count": int(model.get("record_count") or 0),
        "read_model_warning_reason_codes": list(model.get("warning_reason_codes") or []),
        "read_model_blocker_reason_codes": list(model.get("blocker_reason_codes") or []),
        "display_panel_ok": panel.get("ok") is True,
        "display_panel_state": str(panel.get("display_panel_state") or ""),
        "display_generated_at": str(panel.get("generated_at") or ""),
        "display_age_sec": panel.get("age_sec"),
        "display_freshness_state": str(panel.get("freshness_state") or ""),
        "display_prediction_row_count": int(panel.get("prediction_row_count") or 0),
        "display_panel_failures": list(panel.get("panel_failures") or []),
        "data_freshness_badge_version": str(data_badge.get("data_freshness_badge_version") or ""),
        "data_freshness_badge_version_expected": WARROOM_PREDICTION_DATA_FRESHNESS_BADGE_VERSION,
        "data_freshness_badge_state": str(data_badge.get("data_freshness_badge_state") or ""),
        "data_freshness_badge_fresh": data_fresh,
        "data_freshness_badge_delayed": data_delayed,
        "data_freshness_badge_attention": data_badge.get("data_freshness_badge_attention") is True,
        "data_freshness_badge_message": str(data_badge.get("data_freshness_badge_message") or ""),
        "data_freshness_badge_generated_at": str(data_badge.get("data_freshness_badge_generated_at") or ""),
        "data_freshness_badge_age_sec": str(data_badge.get("data_freshness_badge_age_sec") or ""),
        "data_freshness_badge_prediction_row_count": str(data_badge.get("data_freshness_badge_prediction_row_count") or ""),
        "data_freshness_badge_non_stale": data_non_stale,
        "refresh_live_badge_version": str(live_badge.get("refresh_live_badge_version") or ""),
        "refresh_live_badge_version_expected": WARROOM_PREDICTION_REFRESH_LIVE_BADGE_VERSION,
        "refresh_live_badge_active": live_ok,
        "refresh_live_badge_state": str(live_badge.get("refresh_live_badge_state") or ""),
        "refresh_live_badge_message": str(live_badge.get("refresh_live_badge_message") or ""),
        "panel_and_data_freshness_separated": True,
        "warroom_expected_operator_visible_state": "fresh" if data_fresh else "delayed" if data_delayed else "attention",
        "safety_preserved": safety_ok,
        "read_only_verification_only": True,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enablement_allowed": False,
        "producer_enablement_allowed": False,
        "warroom_ui_trigger_allowed": False,
        "approval_or_ledger_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_send_to_broker": False,
    }


def run_verification() -> dict[str, Any]:
    read_model = load_latest_prediction_warroom_read_model(hot_latest_root_hint=DEFAULT_HOT_ROOT)
    display_packet = build_latest_prediction_warroom_display_panel_packet(
        read_model=read_model,
        fragment_enabled=True,
        lang="ja",
    )
    data_badge = latest_prediction_warroom_data_freshness_badge_packet(display_packet, lang="ja")
    live_badge = latest_prediction_warroom_refresh_live_badge_packet(display_packet, lang="ja")
    result = build_warroom_fresh_badge_read_model_confirmation(
        read_model=read_model,
        display_packet=display_packet,
        data_badge_packet=data_badge,
        live_badge_packet=live_badge,
    )
    result["hot_root"] = str(DEFAULT_HOT_ROOT)
    return result


def main() -> int:
    result = run_verification()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
