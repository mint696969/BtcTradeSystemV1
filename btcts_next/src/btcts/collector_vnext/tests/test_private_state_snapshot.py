# path: ./btcts_next/src/btcts/collector_vnext/tests/test_private_state_snapshot.py
# desc: Tests for SR-FX private state snapshot/redaction/readiness.

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.private_state import (
    account_clear_summary,
    assert_no_secret_fields,
    build_private_state_snapshot,
    build_readiness,
    endpoint_snapshot,
    persisted_credential_diagnostics,
    summarize_payload,
)
from btcts.collector_vnext.providers.bitflyer_private_rest import PrivateRestResult


def _result(name: str, endpoint: str, request_class: str, payload: dict, *, ok: bool = True) -> PrivateRestResult:
    return PrivateRestResult(
        ok=ok,
        provider="bitflyer_private_rest",
        exchange="bitflyer",
        transport="rest",
        endpoint=endpoint,
        request_class=request_class,
        status_code=200 if ok else 500,
        payload=payload,
        error="" if ok else "boom",
        retry_after_sec=0.0,
        received_ts="2026-06-14T00:00:00Z",
        response_meta={"headers": {"rate_limit_remaining": "499"}},
    )


def test_summarize_collateral_payload() -> None:
    summary = summarize_payload(
        "collateral",
        {
            "collateral": 1000,
            "keep_rate": 2.0,
            "require_collateral": 100,
            "open_position_pnl": 0,
        },
    )

    assert summary["has_collateral"] is True
    assert summary["has_keep_rate"] is True
    assert summary["has_require_collateral"] is True
    assert summary["has_open_position_pnl"] is True


def test_endpoint_snapshot_rejects_secret_like_fields() -> None:
    result = _result(
        "collateral",
        "/v1/me/getcollateral",
        "private_rest_account_state",
        {"api_secret": "must-not-persist"},
    )

    with pytest.raises(ValueError, match="secret-like field"):
        endpoint_snapshot("collateral", result)


def test_build_readiness_all_fresh_ok() -> None:
    endpoints = {
        "collateral": endpoint_snapshot(
            "collateral",
            _result("collateral", "/v1/me/getcollateral", "private_rest_account_state", {"collateral": 1}),
        ),
        "positions": endpoint_snapshot(
            "positions",
            _result("positions", "/v1/me/getpositions", "private_rest_account_state", {"items": []}),
        ),
        "child_orders": endpoint_snapshot(
            "child_orders",
            _result("child_orders", "/v1/me/getchildorders", "private_rest_order_state", {"items": []}),
        ),
        "own_executions": endpoint_snapshot(
            "own_executions",
            _result("own_executions", "/v1/me/getexecutions", "private_rest_own_fills", {"items": []}),
        ),
    }

    readiness = build_readiness(
        endpoints,
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        now=datetime(2026, 6, 14, 0, 0, 5, tzinfo=timezone.utc),
    )

    assert readiness["private_state_ok"] is True
    assert readiness["private_state_known_and_fresh"] is True
    assert readiness["all_endpoints_ok"] is True
    assert readiness["all_endpoints_fresh"] is True
    assert readiness["account_clear_for_new_auto_entry"] is True
    assert readiness["existing_positions_detected"] is False
    assert readiness["existing_open_orders_detected"] is False
    assert readiness["order_send_allowed"] is False


def test_build_readiness_stale_blocks_private_state() -> None:
    endpoints = {
        "collateral": endpoint_snapshot(
            "collateral",
            _result("collateral", "/v1/me/getcollateral", "private_rest_account_state", {"collateral": 1}),
        )
    }

    readiness = build_readiness(
        endpoints,
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        now=datetime(2026, 6, 14, 0, 1, 0, tzinfo=timezone.utc),
    )

    assert readiness["private_state_ok"] is False
    assert readiness["all_endpoints_fresh"] is False
    assert readiness["reason"] == "private_state_not_ready"


def test_private_state_snapshot_contains_no_secret_fields() -> None:
    cfg = load_config()
    endpoints = {
        "collateral": endpoint_snapshot(
            "collateral",
            _result("collateral", "/v1/me/getcollateral", "private_rest_account_state", {"collateral": 1}),
        )
    }
    readiness = build_readiness(
        endpoints,
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        now=datetime(2026, 6, 14, 0, 0, 5, tzinfo=timezone.utc),
    )

    snapshot = build_private_state_snapshot(
        cfg=cfg,
        execution_market=cfg.execution_market,
        endpoints=endpoints,
        credential_diagnostics={
            "exchange": "bitflyer",
            "api_key_masked": "abcd...wxyz",
            "api_secret_loaded": True,
            "permission_mode": "read_only",
            "order_send_enabled": False,
        },
        readiness=readiness,
    )

    assert snapshot["market_role"] == "execution"
    assert snapshot["product_code"] == "FX_BTC_JPY"
    assert snapshot["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert snapshot["credential"]["credential_pair_loaded"] is True
    assert "api_secret_loaded" not in snapshot["credential"]
    assert_no_secret_fields(snapshot)


def test_persisted_credential_diagnostics_uses_state_safe_names() -> None:
    out = persisted_credential_diagnostics(
        {
            "exchange": "bitflyer",
            "credential_name": "unit_test",
            "permission_mode": "read_only",
            "api_key_masked": "abcd...wxyz",
            "api_secret_loaded": True,
            "private_api_enabled": True,
            "order_send_enabled": False,
        }
    )

    assert out["credential_pair_loaded"] is True
    assert "api_secret_loaded" not in out
    assert_no_secret_fields(out)


def test_account_clear_summary_blocks_existing_positions_and_orders() -> None:
    endpoints = {
        "positions": endpoint_snapshot(
            "positions",
            _result("positions", "/v1/me/getpositions", "private_rest_account_state", {"items": [{"side": "BUY"}]}),
        ),
        "child_orders": endpoint_snapshot(
            "child_orders",
            _result("child_orders", "/v1/me/getchildorders", "private_rest_order_state", {"items": [{"child_order_id": "x"}]}),
        ),
    }

    summary = account_clear_summary(endpoints)

    assert summary["account_clear_for_new_auto_entry"] is False
    assert summary["existing_positions_detected"] is True
    assert summary["existing_open_orders_detected"] is True
    assert summary["position_item_count"] == 1
    assert summary["open_order_item_count"] == 1


def test_build_readiness_known_fresh_but_not_clear_when_positions_exist() -> None:
    endpoints = {
        "collateral": endpoint_snapshot(
            "collateral",
            _result("collateral", "/v1/me/getcollateral", "private_rest_account_state", {"collateral": 1}),
        ),
        "positions": endpoint_snapshot(
            "positions",
            _result("positions", "/v1/me/getpositions", "private_rest_account_state", {"items": [{"side": "BUY"}]}),
        ),
        "child_orders": endpoint_snapshot(
            "child_orders",
            _result("child_orders", "/v1/me/getchildorders", "private_rest_order_state", {"items": []}),
        ),
        "own_executions": endpoint_snapshot(
            "own_executions",
            _result("own_executions", "/v1/me/getexecutions", "private_rest_own_fills", {"items": []}),
        ),
    }

    readiness = build_readiness(
        endpoints,
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        now=datetime(2026, 6, 14, 0, 0, 5, tzinfo=timezone.utc),
    )

    assert readiness["private_state_known_and_fresh"] is True
    assert readiness["account_clear_for_new_auto_entry"] is False
    assert readiness["existing_positions_detected"] is True
    assert readiness["reason"] == "account_not_clear_for_new_auto_entry"
    assert readiness["order_send_allowed"] is False
