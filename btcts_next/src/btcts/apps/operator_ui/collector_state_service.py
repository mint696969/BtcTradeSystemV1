# path: ./btcts_next/src/btcts/apps/operator_ui/collector_state_service.py
# desc: Load collector vNext status, health, rate, and origin state files for the operator UI.

from pathlib import Path
import json
from typing import Dict, Any

STATE_DIR = Path("var/collector_vnext/state/collector_vnext")


def _safe_read(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_state() -> Dict[str, Any]:
    return {
        "status": _safe_read(STATE_DIR / "status.json"),
        "health": _safe_read(STATE_DIR / "daemon_health.json"),
        "rate": _safe_read(STATE_DIR / "rate_state.json"),
        "origin": _safe_read(STATE_DIR / "origin_status.json"),
    }