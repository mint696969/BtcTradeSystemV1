# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_ws_tls_readiness_once.py
# desc: SR-FX WS TLS/CA readiness gate tests. Network-free; no broker calls.

from __future__ import annotations

from btcts.apps import sr_fx_ws_tls_readiness_once as app


def _preflight_ok() -> dict:
    return {
        "ok": True,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "attempts": {
            "board": {"ok": True, "actual_channel": "lightning_board_snapshot_FX_BTC_JPY"},
            "executions": {"ok": True, "actual_channel": "lightning_executions_FX_BTC_JPY"},
        },
        "read_only": True,
        "would_send_to_broker": False,
    }


def _preflight_tls_fail() -> dict:
    return {
        "ok": False,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "attempts": {
            "board": {"ok": False, "error_class": "SSLCertVerificationError"},
            "executions": {"ok": False, "error_class": "SSLCertVerificationError"},
        },
        "read_only": True,
        "would_send_to_broker": False,
    }


def _diag_ok(*, preflight):
    return {
        "ok": True,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "ssl_verify": True,
        "blocked_by": [],
        "warnings": [],
        "suggested_btcts_ws_ca_file": None,
        "read_only": True,
        "would_send_to_broker": False,
    }


def _diag_tls_fail(*, preflight):
    return {
        "ok": False,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "ssl_verify": True,
        "blocked_by": ["ws_tls_certificate_verification_failed"],
        "warnings": ["no_existing_ca_bundle_path_detected"],
        "suggested_btcts_ws_ca_file": None,
        "read_only": True,
        "would_send_to_broker": False,
    }


def test_tls_readiness_ok_when_preflight_and_diagnostics_ok() -> None:
    payload = app.build_sr_fx_ws_tls_readiness_payload(
        preflight_func=_preflight_ok,
        diagnostics_func=_diag_ok,
    )

    assert payload["stage"] == "sr_fx_ws_tls_readiness_once"
    assert payload["ok"] is True
    assert payload["blocked_by"] == []
    assert payload["preflight"]["ok"] is True
    assert payload["diagnostics"]["ok"] is True
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_tls_readiness_blocks_certificate_failure() -> None:
    payload = app.build_sr_fx_ws_tls_readiness_payload(
        preflight_func=_preflight_tls_fail,
        diagnostics_func=_diag_tls_fail,
    )

    assert payload["ok"] is False
    assert "ws_preflight_not_ok" in payload["blocked_by"]
    assert "ws_tls_certificate_verification_failed" in payload["blocked_by"]
    assert "do_not_disable_ssl_verification_for_live_readiness" in payload["operator_next_actions"]
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_tls_readiness_wraps_preflight_exception() -> None:
    def boom():
        raise RuntimeError("synthetic preflight failure")

    payload = app.build_sr_fx_ws_tls_readiness_payload(
        preflight_func=boom,
        diagnostics_func=_diag_tls_fail,
    )

    assert payload["ok"] is False
    assert "ws_preflight_exception" in payload["blocked_by"]
    assert payload["preflight_error"]["error_class"] == "RuntimeError"
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False
