# path: ./btcts_next/src/btcts/collector_vnext/tests/test_bitflyer_private_credentials.py
# desc: Unit tests for bitFlyer private credential loading and redaction.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.collector_vnext.secrets import (
    SecretLoadError,
    load_bitflyer_private_credential,
    mask_api_key,
)


def test_mask_api_key_keeps_only_edges() -> None:
    assert mask_api_key("abcdefghijklmnop") == "abcd...mnop"
    assert mask_api_key("short") == "****"
    assert mask_api_key("") == ""


def test_load_credential_redacts_secret(tmp_path: Path) -> None:
    path = tmp_path / "private_api.local.json"
    path.write_text(
        json.dumps(
            {
                "exchange": "bitflyer",
                "credential_name": "unit_test",
                "permission_mode": "read_only",
                "api_key": "abcd1234wxyz",
                "api_secret": "super-secret-value",
                "private_api_enabled": True,
                "order_send_enabled": False,
            }
        ),
        encoding="utf-8",
    )

    cred = load_bitflyer_private_credential(path)
    redacted = cred.redacted()

    assert redacted["api_key_masked"] == "abcd...wxyz"
    assert redacted["api_secret_loaded"] is True
    assert "super-secret-value" not in json.dumps(redacted)


def test_placeholder_values_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "private_api.local.json"
    path.write_text(
        json.dumps(
            {
                "exchange": "bitflyer",
                "credential_name": "unit_test",
                "permission_mode": "read_only",
                "api_key": "PUT_REAL_API_KEY_HERE",
                "api_secret": "PUT_REAL_API_SECRET_HERE",
                "private_api_enabled": True,
                "order_send_enabled": False,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SecretLoadError):
        load_bitflyer_private_credential(path)


def test_order_send_requires_trade_enabled(tmp_path: Path) -> None:
    path = tmp_path / "private_api.local.json"
    path.write_text(
        json.dumps(
            {
                "exchange": "bitflyer",
                "credential_name": "unit_test",
                "permission_mode": "read_only",
                "api_key": "abcd1234wxyz",
                "api_secret": "super-secret-value",
                "private_api_enabled": True,
                "order_send_enabled": True,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SecretLoadError):
        load_bitflyer_private_credential(path)
