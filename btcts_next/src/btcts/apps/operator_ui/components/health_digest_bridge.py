# path: ./btcts_next/src/btcts/apps/operator_ui/components/health_digest_bridge.py
# desc: Thin UI bridge for reading operator_ui-ready health digest bundle.

from __future__ import annotations

from typing import Any

from btcts.processing.l4_consumer_models.operator_ui import (
    HealthDigestWidgetModel,
    health_digest_status_payload,
    health_digest_widget_model,
)
from btcts.processing.l4_consumer_models.shared import HealthDigest


def build_health_digest_ui_bundle(
    digest: HealthDigest | None,
) -> dict[str, Any]:
    widget = health_digest_widget_model(digest)
    payload = health_digest_status_payload(digest)

    return {
        "widget": widget,
        "payload": payload,
    }


def build_health_digest_widget(
    digest: HealthDigest | None,
) -> HealthDigestWidgetModel:
    bundle = build_health_digest_ui_bundle(digest)
    return bundle["widget"]


def build_health_digest_payload(
    digest: HealthDigest | None,
) -> dict[str, Any]:
    bundle = build_health_digest_ui_bundle(digest)
    return bundle["payload"]