# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_family_read_model.py
# desc: MR-VS6.1 common family read-model and receive-only push contract guards.

from __future__ import annotations

import ast
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.family_read_model import (  # noqa: E402
    PREDICTION_FAMILY_PUSH_MESSAGE_CONTRACT_VERSION,
    PREDICTION_FAMILY_READ_MODEL_CONTRACT_VERSION,
    build_prediction_family_push_message,
    build_prediction_family_read_model,
    validate_prediction_family_push_message,
    validate_prediction_family_read_model,
)


def _model() -> dict:
    return build_prediction_family_read_model(
        prediction_family_id="market_regime",
        generated_at="2026-07-11T00:00:00Z",
        run_id="run-1",
        prediction_id="prediction-1",
        model_id="market_regime_v1",
        logic_version="logic-v1",
        parameter_set_id="params-v1",
        feature_set_version="features-v1",
        target_definition_version="targets-v1",
        horizon_rows=[
            {
                "horizon_key": "15m",
                "horizon_sec": 900,
                "horizon_group": "short_horizon",
                "primary_label": "range",
                "primary_label_display": "レンジ",
                "confidence_percent": 15,
                "confidence_kind": "heuristic_support",
                "freshness_state": "fresh",
                "evidence_quality": "limited",
                "warnings": ["comparison_not_ready"],
                "family_payload": {
                    "regime_code": "RANGE",
                    "tactical_hint": "WAIT",
                },
            }
        ],
    )


def test_build_common_family_read_model_is_family_neutral_and_safe() -> None:
    model = _model()
    assert model["contract_version"] == PREDICTION_FAMILY_READ_MODEL_CONTRACT_VERSION
    assert model["prediction_family_id"] == "market_regime"
    assert model["horizon_count"] == 1
    assert model["horizon_rows"][0]["confidence_percent"] == 15
    assert model["horizon_rows"][0]["family_payload"]["regime_code"] == "RANGE"
    assert model["safety"]["read_only"] is True
    assert model["safety"]["ui_render_invokes_prediction"] is False
    assert model["safety"]["ui_confidence_recalculation"] is False
    assert model["safety"]["would_send_to_broker"] is False
    assert validate_prediction_family_read_model(model)["ok"] is True


def test_validator_rejects_raw_payload_and_unsafe_flags() -> None:
    model = _model()
    model["horizon_rows"][0]["family_payload"]["raw_orderbook"] = {"bids": []}
    model["safety"]["broker_private_api_allowed"] = True
    validation = validate_prediction_family_read_model(model)
    assert validation["ok"] is False
    assert "forbidden_raw_payload_key_present" in validation["failures"]
    assert "safety_broker_private_api_allowed_not_false" in validation["failures"]


def test_push_message_is_receive_only_and_transport_time_is_separate() -> None:
    model = _model()
    push = build_prediction_family_push_message(
        topic_key="prediction.family.market_regime",
        value=model,
        received_at_ms=1_725_000_000_000,
        sequence=7,
    )
    assert push["contract_version"] == PREDICTION_FAMILY_PUSH_MESSAGE_CONTRACT_VERSION
    assert push["receive_only"] is True
    assert push["received_at_ms"] == 1_725_000_000_000
    assert push["value"]["generated_at"] == "2026-07-11T00:00:00Z"
    assert push["value"]["generated_at"] != str(push["received_at_ms"])
    assert validate_prediction_family_push_message(push)["ok"] is True


def test_push_validator_rejects_non_receive_only_and_unsafe_flags() -> None:
    push = build_prediction_family_push_message(
        topic_key="prediction.family.market_regime",
        value=_model(),
        received_at_ms=1,
    )
    push["receive_only"] = False
    push["safety"]["autotrade_trigger_allowed"] = True
    validation = validate_prediction_family_push_message(push)
    assert validation["ok"] is False
    assert "receive_only_not_true" in validation["failures"]
    assert "safety_autotrade_trigger_allowed_not_false" in validation["failures"]


def test_common_module_has_no_family_or_runtime_dependencies() -> None:
    module_path = Path(__file__).resolve().parents[1] / "family_read_model.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

    imported_modules: set[str] = set()
    called_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    forbidden_import_prefixes = (
        "btcts.prediction.market_regime",
        "streamlit",
        "subprocess",
        "requests",
    )
    forbidden_calls = {
        "write_text",
        "run",
        "Popen",
        "post",
        "put",
        "delete",
        "submit_order",
        "send_order",
    }

    assert [
        module
        for module in imported_modules
        if module.startswith(forbidden_import_prefixes)
    ] == []
    assert sorted(called_names & forbidden_calls) == []
