# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_shadow_packet_conditioning_observability.py
# desc: MR-F9.18A12A guard that one-shot preflight exposes the conditioned shadow packet read-only.

from __future__ import annotations

from pathlib import Path


def test_preflight_result_exposes_shadow_packet_without_enabling_runtime() -> None:
    source = Path(__file__).parents[1] / "tools" / "shadow_runtime_preflight_once.py"
    text = source.read_text(encoding="utf-8")
    assert '"shadow_packet": _json_native(shadow_packet)' in text
    assert '"writes_dhot": False' in text
    assert '"scheduler_enabled": False' in text
    assert '"producer_loop_enabled": False' in text
    assert '"broker_private_api_allowed": False' in text
    assert '"autotrade_trigger_allowed": False' in text
    assert '"order_submission_allowed": False' in text
