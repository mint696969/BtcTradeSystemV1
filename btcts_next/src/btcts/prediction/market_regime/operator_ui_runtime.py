# path: ./btcts_next/src/btcts/prediction/market_regime/operator_ui_runtime.py
# desc: Operator UI runtime helper for manual market-regime preflight/run-once controls. No scheduler, daemon loop, broker, AutoTrade, or UI render-path inference.

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btcts.core import paths as core_paths

from .tools.write_latest import preflight_market_regime_latest_artifacts_once, write_market_regime_latest_artifacts_once

MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION = "prediction.market_regime.operator_ui_runtime.2026_07_08.v1"
MARKET_REGIME_OPERATOR_UI_STATE_DIRNAME = "market_regime_inference"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_hot_root(root: Path) -> Path:
    candidate = Path(root)
    if candidate.name.lower() == "data":
        return candidate.parent
    return candidate


def market_regime_hot_root() -> Path:
    hot_root = str(os.environ.get("BTCTS_HOT_ROOT") or "").strip()
    if hot_root:
        return _normalize_hot_root(Path(hot_root))
    data_root = str(os.environ.get("BTCTS_DATA_ROOT") or os.environ.get("BTC_TS_DATA_DIR") or "").strip()
    if data_root:
        return _normalize_hot_root(Path(data_root))
    return _normalize_hot_root(core_paths.data_dir(ensure=False))


def market_regime_operator_ui_paths(hot_root: Path | None = None) -> dict[str, Path]:
    root = _normalize_hot_root(hot_root or market_regime_hot_root())
    state_dir = root / "state" / MARKET_REGIME_OPERATOR_UI_STATE_DIRNAME
    return {
        "hot_root": root,
        "state_dir": state_dir,
        "status": state_dir / "status.json",
        "latest_cards": root / "prediction" / "market_regime" / "latest_cards.json",
        "latest_read_model": root / "prediction" / "market_regime" / "latest_read_model.json",
        "trace_ledger_dir": root / "prediction" / "market_regime" / "ledgers",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def market_regime_operator_ui_snapshot(hot_root: Path | None = None) -> dict[str, Any]:
    paths = market_regime_operator_ui_paths(hot_root)
    status = _read_json(paths["status"])
    latest_cards = _read_json(paths["latest_cards"])
    first_card = {}
    cards = latest_cards.get("cards") if isinstance(latest_cards.get("cards"), list) else []
    if cards and isinstance(cards[0], dict):
        first_card = dict(cards[0])
    return {
        "ok": True,
        "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
        "mode": str(status.get("mode") or "READY"),
        "hot_root": str(paths["hot_root"]),
        "state_dir": str(paths["state_dir"]),
        "status_path": str(paths["status"]),
        "latest_cards_path": str(paths["latest_cards"]),
        "latest_cards_available": bool(paths["latest_cards"].exists()),
        "latest_run_id": latest_cards.get("run_id") or status.get("latest_run_id") or "",
        "latest_generated_at": latest_cards.get("generated_at") or status.get("generated_at") or "",
        "card_count": int(latest_cards.get("horizon_count") or len(cards) or 0),
        "first_card_label": str(first_card.get("regime_label") or first_card.get("regime_code") or ""),
        "first_card_confidence": first_card.get("confidence_percent"),
        "first_card_freshness": str(first_card.get("freshness_badge") or ""),
        "last_preflight_can_write": bool(status.get("can_write_live_once")),
        "last_preflight_missing_sources": list(status.get("missing_sources") or []),
        "last_preflight_warnings": list(status.get("warnings") or []),
        "last_action": status.get("last_action") or "",
        "last_error": status.get("last_error") or "",
        "status": status,
        "active": False,
        "preflight_only_supported": True,
        "run_once_supported": True,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
    }


def request_market_regime_preflight(hot_root: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    paths = market_regime_operator_ui_paths(hot_root)
    try:
        result = preflight_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
        status = {
            "ok": True,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "PREFLIGHT_OK" if result.get("can_write_live_once") else "PREFLIGHT_BLOCKED",
            "last_action": "preflight",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "can_write_live_once": bool(result.get("can_write_live_once")),
            "source_snapshot_ok": bool(result.get("source_snapshot_ok")),
            "missing_sources": list(result.get("missing_sources") or []),
            "warnings": list(result.get("warnings") or []),
            "card_count": int(result.get("card_count") or 0),
            "latest_cards_validation": dict(result.get("latest_cards_validation") or {}),
            "expected_artifacts": dict(result.get("expected_artifacts") or {}),
            "last_error": "",
            "preflight_only": True,
            "would_write": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return True, f"market_regime preflight can_write_live_once={status['can_write_live_once']}", status
    except Exception as exc:
        status = {
            "ok": False,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "PREFLIGHT_ERROR",
            "last_action": "preflight",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "last_error": str(exc),
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return False, f"market_regime preflight failed: {exc}", status


def request_market_regime_run_once(hot_root: Path | None = None) -> tuple[bool, str, dict[str, Any]]:
    paths = market_regime_operator_ui_paths(hot_root)
    preflight_ok, preflight_msg, preflight_status = request_market_regime_preflight(paths["hot_root"])
    if not preflight_ok or not preflight_status.get("can_write_live_once"):
        status = dict(preflight_status)
        status.update({
            "mode": "RUN_ONCE_BLOCKED",
            "last_action": "run_once",
            "run_once_blocked_reason": preflight_msg,
            "would_write": False,
            "ts": _now_iso(),
        })
        _write_json(paths["status"], status)
        return False, f"market_regime run_once blocked: {preflight_msg}", status
    try:
        result = write_market_regime_latest_artifacts_once(hot_root=paths["hot_root"])
        status = {
            "ok": True,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "RUN_ONCE_OK",
            "last_action": "run_once",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "latest_run_id": str(result.get("run_id") or ""),
            "generated_at": str(result.get("generated_at") or ""),
            "source_snapshot_ok": bool(result.get("source_snapshot_ok")),
            "card_count": int(result.get("card_count") or 0),
            "latest_cards_validation": dict(result.get("latest_cards_validation") or {}),
            "trace_ledger_append": dict(result.get("trace_ledger_append") or {}),
            "written": list(result.get("written") or []),
            "last_error": "",
            "would_write": True,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return True, f"market_regime run_once ok run_id={status['latest_run_id']}", status
    except Exception as exc:
        status = {
            "ok": False,
            "version": MARKET_REGIME_OPERATOR_UI_RUNTIME_VERSION,
            "mode": "RUN_ONCE_ERROR",
            "last_action": "run_once",
            "ts": _now_iso(),
            "hot_root": str(paths["hot_root"]),
            "last_error": str(exc),
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        }
        _write_json(paths["status"], status)
        return False, f"market_regime run_once failed: {exc}", status
