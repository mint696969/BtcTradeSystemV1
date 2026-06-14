# path: ./btcts_next/src/btcts/collector_vnext/tests/test_fx_public_market_readiness.py
# desc: Tests for SR-FX public market readiness. No broker calls.

from __future__ import annotations

from btcts.collector_vnext.fx_public_market_readiness import build_fx_public_market_readiness


def _board(ok: bool = True, path: str = "E:/x/symbol=FX_BTC_JPY/board") -> dict:
    return {
        "ok": ok,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_role": "execution",
        "request_class": "public_rest_market_data",
        "raw_path": path,
        "canonical_path": path,
    }


def _trades(ok: bool = True, count: int = 50, path: str = "E:/x/symbol=FX_BTC_JPY/trades") -> dict:
    return {
        "ok": ok,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_role": "execution",
        "request_class": "public_rest_market_data",
        "trade_count": count,
        "raw_path": path,
        "canonical_path": path,
    }


def _ws(ok: bool = True, ssl_verify: bool = True) -> dict:
    return {
        "ok": ok,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_role": "execution",
        "ssl_verify": ssl_verify,
        "attempts": {
            "executions": {"ok": ok, "error_class": None if ok else "SSLCertVerificationError"},
            "board": {"ok": ok, "error_class": None if ok else "SSLCertVerificationError"},
        },
    }


def test_public_market_readiness_ok_when_rest_and_ws_ok() -> None:
    out = build_fx_public_market_readiness(board_check=_board(), executions_check=_trades(), ws_preflight=_ws())

    assert out.ok is True
    assert out.rest_market_ok is True
    assert out.ws_market_ok is True
    assert out.blocked_by == ()
    assert out.would_send_to_broker is False
    assert out.read_only is True


def test_public_market_readiness_blocks_when_ws_fails_by_default() -> None:
    out = build_fx_public_market_readiness(board_check=_board(), executions_check=_trades(), ws_preflight=_ws(ok=False))

    assert out.ok is False
    assert out.rest_market_ok is True
    assert out.ws_market_ok is False
    assert "fx_public_ws_preflight_not_ok" in out.blocked_by
    assert any(str(w).startswith("ws_executions_not_ok") for w in out.warnings)


def test_public_market_readiness_can_warn_when_ws_not_required() -> None:
    out = build_fx_public_market_readiness(
        board_check=_board(),
        executions_check=_trades(),
        ws_preflight=_ws(ok=False),
        require_ws_ok=False,
    )

    assert out.ok is True
    assert "fx_public_ws_preflight_not_ok" not in out.blocked_by
    assert "fx_public_ws_preflight_not_ok" in out.warnings


def test_public_market_readiness_blocks_spot_path() -> None:
    out = build_fx_public_market_readiness(
        board_check=_board(path="E:/x/symbol=BTC_JPY/board"),
        executions_check=_trades(),
        ws_preflight=_ws(),
    )

    assert out.ok is False
    assert "fx_public_rest_path_not_fx_symbol" in out.blocked_by
    assert "fx_public_rest_path_contains_spot_symbol" in out.blocked_by


def test_public_market_readiness_blocks_zero_rest_trades() -> None:
    out = build_fx_public_market_readiness(board_check=_board(), executions_check=_trades(count=0), ws_preflight=_ws())

    assert out.ok is False
    assert "fx_rest_trade_count_zero" in out.blocked_by
