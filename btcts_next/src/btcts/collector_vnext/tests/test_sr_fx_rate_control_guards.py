# path: ./btcts_next/src/btcts/collector_vnext/tests/test_sr_fx_rate_control_guards.py
# desc: Guard tests proving SR-FX public/private REST use shared bitFlyer rate control.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pytest

from btcts.collector_vnext.fx_public_rest import emit_fx_rest_board_snapshot, emit_fx_rest_trades
from btcts.collector_vnext.ids import SequenceManager
from btcts.collector_vnext.providers.bitflyer_private_rest import fetch_collateral
from btcts.collector_vnext.providers.bitflyer_rest import RestFetchResult
from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.rate_control import RateController, RatePolicy
from btcts.collector_vnext.rate_runtime import VNextRateRuntime
from btcts.collector_vnext.secrets import BitflyerPrivateCredential


class FakeRateRuntime:
    def __init__(self) -> None:
        self.acquire_calls: list[str] = []
        self.sent_calls: list[tuple[str, str | None]] = []
        self.success_calls: list[str] = []
        self.on_429_calls: list[tuple[str, float]] = []

    def acquire(self, exchange: str) -> tuple[bool, int]:
        self.acquire_calls.append(exchange)
        return True, 0

    def note_request_sent(self, exchange: str, request_class: str | None = None) -> None:
        self.sent_calls.append((exchange, request_class))

    def on_success(self, exchange: str) -> None:
        self.success_calls.append(exchange)

    def on_429(self, exchange: str, retry_after_sec: float = 0.0) -> None:
        self.on_429_calls.append((exchange, retry_after_sec))


@dataclass
class FakePrivateResponse:
    status_code: int
    payload: Any
    headers: Dict[str, str]

    def json(self) -> Any:
        return self.payload


def _rest_result(endpoint: str, payload: Dict[str, Any]) -> RestFetchResult:
    return RestFetchResult(
        ok=True,
        provider="bitflyer_rest",
        exchange="bitflyer",
        transport="rest",
        endpoint=endpoint,
        status_code=200,
        payload=payload,
        error="",
        retry_after_sec=0.0,
        request_meta={"endpoint": endpoint},
        response_meta={"headers": {"rate_limit_remaining": "499"}},
        received_ts="2026-06-14T00:00:00Z",
    )


def _set_runtime_paths(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")


def test_private_rest_collateral_uses_bitflyer_rate_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    import btcts.collector_vnext.providers.bitflyer_private_rest as private_rest

    fake_rate = FakeRateRuntime()
    cred = BitflyerPrivateCredential(
        exchange="bitflyer",
        credential_name="unit",
        permission_mode="read_only",
        api_key="dummy-api-key",
        api_secret="dummy-api-secret",
        private_api_enabled=True,
        order_send_enabled=False,
        source_path=__file__,  # type: ignore[arg-type]
    )

    def fake_get(*args: Any, **kwargs: Any) -> FakePrivateResponse:
        return FakePrivateResponse(
            status_code=200,
            payload={"collateral": 1, "keep_rate": 1.0},
            headers={"Content-Type": "application/json", "X-RateLimit-Remaining": "499"},
        )

    monkeypatch.setattr(private_rest.requests, "get", fake_get)

    result = fetch_collateral(cred, rate_runtime=fake_rate)

    assert result.ok is True
    assert fake_rate.acquire_calls == ["bitflyer"]
    assert fake_rate.sent_calls == [("bitflyer", "private_rest_account_state")]
    assert fake_rate.success_calls == ["bitflyer"]
    assert fake_rate.on_429_calls == []


def test_private_rest_429_reports_shared_bitflyer_rate_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    import btcts.collector_vnext.providers.bitflyer_private_rest as private_rest

    fake_rate = FakeRateRuntime()
    cred = BitflyerPrivateCredential(
        exchange="bitflyer",
        credential_name="unit",
        permission_mode="read_only",
        api_key="dummy-api-key",
        api_secret="dummy-api-secret",
        private_api_enabled=True,
        order_send_enabled=False,
        source_path=__file__,  # type: ignore[arg-type]
    )

    def fake_get(*args: Any, **kwargs: Any) -> FakePrivateResponse:
        return FakePrivateResponse(
            status_code=429,
            payload={"error_message": "rate limit"},
            headers={"Content-Type": "application/json", "Retry-After": "2.5"},
        )

    monkeypatch.setattr(private_rest.requests, "get", fake_get)

    result = fetch_collateral(cred, rate_runtime=fake_rate)

    assert result.ok is False
    assert result.status_code == 429
    assert fake_rate.acquire_calls == ["bitflyer"]
    assert fake_rate.sent_calls == [("bitflyer", "private_rest_account_state")]
    assert fake_rate.on_429_calls == [("bitflyer", 2.5)]


def test_fx_public_board_uses_public_market_data_rate_class(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    import btcts.collector_vnext.fx_public_rest as fx_public_rest

    _set_runtime_paths(monkeypatch, tmp_path)
    fake_rate = FakeRateRuntime()

    monkeypatch.setattr(
        fx_public_rest,
        "fetch_board",
        lambda **kwargs: _rest_result(
            "/v1/board",
            {"mid_price": 100, "bids": [{"price": 99, "size": 1}], "asks": [{"price": 101, "size": 1}]},
        ),
    )

    out = emit_fx_rest_board_snapshot(SequenceManager.start(), "unit-session", rate_runtime=fake_rate)

    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["request_class"] == "public_rest_market_data"
    assert "symbol=FX_BTC_JPY" in str(out["raw_path"])
    assert fake_rate.acquire_calls == ["bitflyer"]
    assert fake_rate.sent_calls == [("bitflyer", "public_rest_market_data")]
    assert fake_rate.success_calls == ["bitflyer"]


def test_fx_public_executions_uses_public_market_data_rate_class(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    import btcts.collector_vnext.fx_public_rest as fx_public_rest

    _set_runtime_paths(monkeypatch, tmp_path)
    fake_rate = FakeRateRuntime()

    monkeypatch.setattr(
        fx_public_rest,
        "fetch_executions",
        lambda **kwargs: _rest_result(
            "/v1/executions",
            {"items": [{"id": 1, "side": "BUY", "price": 100, "size": 0.01, "exec_date": "2026-06-14T00:00:00Z"}]},
        ),
    )

    out = emit_fx_rest_trades(SequenceManager.start(), "unit-session", rate_runtime=fake_rate)

    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["request_class"] == "public_rest_market_data"
    assert out["trade_count"] == 1
    assert "symbol=FX_BTC_JPY" in str(out["raw_path"])
    assert fake_rate.acquire_calls == ["bitflyer"]
    assert fake_rate.sent_calls == [("bitflyer", "public_rest_market_data")]
    assert fake_rate.success_calls == ["bitflyer"]


def test_rate_runtime_snapshot_exposes_sr_fx_request_classes(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    _set_runtime_paths(monkeypatch, tmp_path)
    cfg = load_config()
    rc = RateController()
    rc.set_policy(
        "bitflyer",
        RatePolicy(official_max_rps=10.0, soft_ratio=0.9, hard_ratio=0.8, burst_base_sec=1.0),
    )
    runtime = VNextRateRuntime(cfg=cfg, rc=rc, rate_cfg={"util_window_warn_sec": 10.0})

    runtime.note_request_sent("bitflyer", "public_rest_market_data")
    runtime.note_request_sent("bitflyer", "private_rest_account_state")
    runtime.note_request_sent("bitflyer", "private_rest_order_state")
    runtime.note_request_sent("bitflyer", "private_rest_own_fills")

    item = runtime.snapshot()["items"]["bitflyer"]
    classes = item["request_classes"]

    assert classes["public_rest_market_data"]["requests_60s"] == 1
    assert classes["private_rest_account_state"]["requests_60s"] == 1
    assert classes["private_rest_order_state"]["requests_60s"] == 1
    assert classes["private_rest_own_fills"]["requests_60s"] == 1
    assert "order_send" in classes
    assert "order_cancel" in classes
