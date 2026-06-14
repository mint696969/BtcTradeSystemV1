# path: ./btcts_next/src/btcts/apps/sr_fx_ws_tls_readiness_once.py
# desc: Read-only SR-FX public WS TLS/CA readiness gate. No broker/private/order calls.

from __future__ import annotations

import json
from typing import Any, Callable, Mapping

from btcts.collector_vnext.fx_public_ws import diagnose_fx_ws_tls_environment, preflight_fx_public_ws

STAGE = "sr_fx_ws_tls_readiness_once"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def build_sr_fx_ws_tls_readiness_payload(
    *,
    preflight_func: Callable[..., Mapping[str, Any]] = preflight_fx_public_ws,
    diagnostics_func: Callable[..., Mapping[str, Any]] = diagnose_fx_ws_tls_environment,
    run_preflight: bool = True,
) -> dict[str, Any]:
    preflight: Mapping[str, Any] | None = None
    preflight_error: dict[str, Any] | None = None

    if run_preflight:
        try:
            preflight = dict(preflight_func())
        except Exception as exc:
            preflight_error = {
                "error_class": exc.__class__.__name__,
                "error_message": str(exc),
            }
            preflight = {
                "ok": False,
                "attempts": {
                    "preflight": {
                        "ok": False,
                        "error_class": exc.__class__.__name__,
                        "error_message": str(exc),
                    }
                },
            }

    diagnostics = dict(diagnostics_func(preflight=preflight))

    blocked_by: list[str] = []
    if preflight_error is not None:
        blocked_by.append("ws_preflight_exception")
    if run_preflight and preflight is not None and not bool(preflight.get("ok")):
        blocked_by.append("ws_preflight_not_ok")
    blocked_by.extend(_as_list(diagnostics.get("blocked_by")))
    blocked_by = list(dict.fromkeys(blocked_by))

    return {
        "stage": STAGE,
        "ok": not blocked_by,
        "preflight": preflight,
        "preflight_error": preflight_error,
        "diagnostics": diagnostics,
        "blocked_by": blocked_by,
        "operator_next_actions": [
            "keep_BTCTS_WS_SSL_VERIFY_enabled",
            "use_BTCTS_WS_CA_FILE_to_point_to_existing_trusted_ca_bundle_if_required",
            "do_not_disable_ssl_verification_for_live_readiness",
            "rerun_sr_fx_ws_tls_readiness_once_after_ca_fix",
            "rerun_sr_fx_ws_canonical_refresh_once_after_tls_ok",
        ],
        "read_only": True,
        "would_send_to_broker": False,
    }


def main() -> int:
    try:
        payload = build_sr_fx_ws_tls_readiness_payload()
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        payload = {
            "stage": STAGE,
            "ok": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["sr_fx_ws_tls_readiness_failed"],
            "read_only": True,
            "would_send_to_broker": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
