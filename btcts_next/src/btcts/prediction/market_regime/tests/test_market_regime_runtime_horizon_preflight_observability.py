# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_preflight_observability.py
# desc: MR-F9.19A structural guard for canonical 8-horizon artifact observability in read-only one-shot preflight.

from __future__ import annotations

from pathlib import Path


def test_preflight_source_builds_but_never_persists_runtime_horizon_artifact() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "tools" / "shadow_runtime_preflight_once.py").read_text(encoding="utf-8")
    assert "build_market_regime_runtime_horizon_artifact" in text
    assert '"runtime_horizon_artifact": _json_native(runtime_horizon_artifact)' in text
    assert '"runtime_horizon_artifact_built": True' in text
    assert '"runtime_horizon_artifact_persisted": False' in text
    assert '"writer_invoked": False' in text
    assert '"writes_dhot": False' in text
    assert '"scheduler_enabled": False' in text
    assert '"producer_loop_enabled": False' in text
    assert '"order_submission_allowed": False' in text


def test_runtime_artifact_contract_keeps_ui_and_ws_non_executing() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "runtime_horizon_artifact.py").read_text(encoding="utf-8")
    assert '"ui_inference_allowed": False' in text
    assert '"ui_confidence_recalculation_allowed": False' in text
    assert '"websocket_opened": False' in text
    assert '"writes_dhot": False' in text
    assert '"order_submission_allowed": False' in text
