# path: ./btcts_next/src/btcts/apps/operator_ui/ui_state_store.py
# desc: Operator UI の表示言語・最後に開いていたページなどの軽量UI状態を JSON で永続化する。

from __future__ import annotations

from pathlib import Path

from btcts.core import io, paths


def ui_state_path() -> Path:
    return paths.config_dir() / "operator_ui" / "ui_state.json"


def load_ui_state() -> dict:
    data = io.read_json(ui_state_path(), default={})
    if not isinstance(data, dict):
        data = {}

    return {
        "ui_lang": str(data.get("ui_lang") or "en"),
        "ui_scale": str(data.get("ui_scale") or "100%"),
        "ui_auto_refresh": bool(data.get("ui_auto_refresh", True)),
        "ui_refresh_interval": int(data.get("ui_refresh_interval") or 5),
        "ui_selected_page_key": str(data.get("ui_selected_page_key") or "collector"),
    }


def save_ui_state(row: dict) -> bool:
    normalized = {
        "ui_lang": str(row.get("ui_lang") or "en"),
        "ui_scale": str(row.get("ui_scale") or "100%"),
        "ui_auto_refresh": bool(row.get("ui_auto_refresh", True)),
        "ui_refresh_interval": int(row.get("ui_refresh_interval") or 5),
        "ui_selected_page_key": str(row.get("ui_selected_page_key") or "collector"),
    }

    try:
        io.write_json(ui_state_path(), normalized, indent=2, sort_keys=True)
        return True
    except Exception:
        return False