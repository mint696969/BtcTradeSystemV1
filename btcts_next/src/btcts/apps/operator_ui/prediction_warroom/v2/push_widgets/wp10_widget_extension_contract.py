# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/wp10_widget_extension_contract.py
# desc: WP10 widget extension contract. Validates future WarRoom push widgets without page edits, socket open, send, broker, order, ledger, or prediction.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .wp1_architecture_contracts import build_wp1_no_send_flags
from .wp2_widget_registry_manifest import DEFAULT_BINDINGS, DEFAULT_MANIFESTS, PushWidgetManifest, PushWidgetTopicBinding
from .wp9_warroom_page_mount import build_wp9_warroom_page_mount_packet

WP10_VERSION = "warroom.manual_trade_support.push_widgets.wp10.widget_extension_contract.v1"
FORBIDDEN_EXTENSION_KEYS = {"raw", "raw_payload", "endpoint", "token", "callable", "secret", "broker", "order", "ledger"}


@dataclass(frozen=True)
class WidgetExtensionContract:
    extension_id: str
    manifest: PushWidgetManifest
    topic_bindings: tuple[PushWidgetTopicBinding, ...]
    owner: str = "operator_ui"
    read_only: bool = True
    receive_only: bool = True
    page_edit_required: bool = False
    streamlit_control_allowed: bool = False
    socket_open_allowed: bool = False
    send_allowed: bool = False
    broker_allowed: bool = False
    order_allowed: bool = False
    prediction_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["manifest"] = self.manifest.to_dict()
        data["topic_bindings"] = [binding.to_dict() for binding in self.topic_bindings]
        return data


def _existing_widget_ids() -> set[str]:
    return {manifest.widget_id for manifest in DEFAULT_MANIFESTS}


def _existing_topic_keys() -> set[str]:
    return {binding.topic_key for binding in DEFAULT_BINDINGS}


def _has_forbidden_key(value: Mapping[str, Any]) -> list[str]:
    return sorted({str(key) for key in value if str(key) in FORBIDDEN_EXTENSION_KEYS})


def validate_widget_extension_contract(contract: WidgetExtensionContract, *, sample_value: Mapping[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    manifest = contract.manifest
    binding_topic_keys = [binding.topic_key for binding in contract.topic_bindings]
    if manifest.widget_id in _existing_widget_ids():
        errors.append(f"duplicate_widget_id:{manifest.widget_id}")
    if any(topic in _existing_topic_keys() for topic in binding_topic_keys):
        errors.append("duplicate_topic_key")
    if set(manifest.topic_keys) != set(binding_topic_keys):
        errors.append("manifest_binding_topic_mismatch")
    if not contract.read_only or not manifest.read_only:
        errors.append("not_read_only")
    if not contract.receive_only or any(not binding.receive_only for binding in contract.topic_bindings):
        errors.append("not_receive_only")
    if contract.page_edit_required:
        errors.append("page_edit_required")
    if contract.streamlit_control_allowed:
        errors.append("streamlit_control_allowed")
    if contract.socket_open_allowed:
        errors.append("socket_open_allowed")
    if contract.send_allowed:
        errors.append("send_allowed")
    if contract.broker_allowed:
        errors.append("broker_allowed")
    if contract.order_allowed:
        errors.append("order_allowed")
    if contract.prediction_allowed:
        errors.append("prediction_allowed")
    if not manifest.reducer_key or not manifest.render_adapter_key:
        errors.append("missing_reducer_or_render_adapter")
    forbidden = _has_forbidden_key(dict(sample_value or {}))
    for key in forbidden:
        errors.append(f"forbidden_sample_key:{key}")
    return {"ok": not errors, "errors": errors, "extension_id": contract.extension_id, "widget_id": manifest.widget_id, "topic_count": len(contract.topic_bindings)}


def build_example_safe_widget_extension_contract() -> WidgetExtensionContract:
    manifest = PushWidgetManifest(
        "orderbook_imbalance_widget",
        "Orderbook imbalance",
        "market_microstructure_extension",
        ("market.orderbook_imbalance",),
        "orderbook_imbalance_reducer",
        "orderbook_imbalance_render_packet",
        "core_grid",
        60,
        extension_tags=("extension", "imbalance"),
    )
    bindings = (PushWidgetTopicBinding("orderbook_imbalance_widget", "market.orderbook_imbalance", "market.orderbook_imbalance.BTC_JPY"),)
    return WidgetExtensionContract("extension.orderbook_imbalance.v1", manifest, bindings)


def build_wp10_widget_extension_contract_packet() -> dict[str, Any]:
    contract = build_example_safe_widget_extension_contract()
    validation = validate_widget_extension_contract(contract, sample_value={"symbol": "BTC_JPY", "imbalance": 0.12})
    page_packet = build_wp9_warroom_page_mount_packet()
    packet = {
        "ok": bool(validation["ok"]),
        "packet_kind": "warroom_push_widget_wp10_extension_contract_packet",
        "version": WP10_VERSION,
        "wp10_completed": bool(validation["ok"]),
        "next_checkpoint": "WP11_Top_layout_push_widget_polish" if validation["ok"] else "WP10_extension_contract_fix",
        "widget_extension_contract_ready": bool(validation["ok"]),
        "extension_validator_ready": bool(validation["ok"]),
        "future_widget_addition_ready": bool(validation["ok"]),
        "extension_without_page_edit_ready": bool(validation["ok"]),
        "extension_no_action_boundary_ready": bool(validation["ok"]),
        "extension_render_adapter_contract_ready": bool(validation["ok"]),
        "extension_health_contract_ready": bool(validation["ok"]),
        "example_extension_id": contract.extension_id,
        "example_widget_id": contract.manifest.widget_id,
        "base_widget_count": int(page_packet["widget_count"]),
        "validation": validation,
        "contract": contract.to_dict(),
    }
    packet.update(build_wp1_no_send_flags())
    packet["warroom_page_modified"] = False
    packet["warroom_page_mount_added"] = False
    packet["websocket_opened"] = False
    packet["websocket_send_enabled"] = False
    packet["broker_send_enabled"] = False
    packet["order_intent_submitted"] = False
    return packet
