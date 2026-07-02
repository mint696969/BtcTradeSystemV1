# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/model_views.py
# desc: Read-only helpers for selecting WarRoom v2 placeholder read models by layout zone.

from __future__ import annotations

from typing import Any

WARROOM_V2_MODEL_VIEWS_VERSION = "prediction_warroom.v2.panel_model_views.ps_q29d.v1"


def warroom_v2_models_by_zone(shell: dict[str, Any], zone: str) -> list[dict[str, Any]]:
    models = shell["placeholder_read_models"]["read_models"]
    return [model for model in models if model.get("payload", {}).get("zone") == zone]
