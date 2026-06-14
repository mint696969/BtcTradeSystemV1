# path: ./btcts_next/src/btcts/collector_vnext/secrets.py
# desc: Local secret loader for Collector vNext private exchange credentials.

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


DEFAULT_BITFLYER_SECRET_FILE = Path(
    r"E:\btc_ts\secrets\bitflyer\private_api.local.json"
)
BITFLYER_SECRET_FILE_ENV = "BTCTS_BITFLYER_SECRET_FILE"

_PLACEHOLDER_VALUES = {
    "",
    "PUT_REAL_API_KEY_HERE",
    "PUT_REAL_API_SECRET_HERE",
}


class SecretLoadError(RuntimeError):
    pass


@dataclass(frozen=True)
class BitflyerPrivateCredential:
    exchange: str
    credential_name: str
    permission_mode: str
    api_key: str
    api_secret: str
    private_api_enabled: bool
    order_send_enabled: bool
    source_path: Path

    def redacted(self) -> Dict[str, Any]:
        return {
            "exchange": self.exchange,
            "credential_name": self.credential_name,
            "permission_mode": self.permission_mode,
            "api_key_masked": mask_api_key(self.api_key),
            "api_secret_loaded": bool(self.api_secret),
            "private_api_enabled": self.private_api_enabled,
            "order_send_enabled": self.order_send_enabled,
            "source_path": str(self.source_path),
        }


def bitflyer_secret_file_from_env() -> Path:
    raw = os.getenv(BITFLYER_SECRET_FILE_ENV, "").strip()
    return Path(raw) if raw else DEFAULT_BITFLYER_SECRET_FILE


def mask_api_key(value: str) -> str:
    text = str(value or "")
    if not text:
        return ""
    if len(text) <= 8:
        return "****"
    return f"{text[:4]}...{text[-4:]}"


def _require_text(data: Dict[str, Any], key: str) -> str:
    value = str(data.get(key) or "").strip()
    if value in _PLACEHOLDER_VALUES:
        raise SecretLoadError(f"bitFlyer credential field is missing or placeholder: {key}")
    return value


def _bool_value(data: Dict[str, Any], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def load_bitflyer_private_credential(
    path: Path | None = None,
    *,
    require_enabled: bool = True,
) -> BitflyerPrivateCredential:
    secret_path = path or bitflyer_secret_file_from_env()

    if not secret_path.exists():
        raise SecretLoadError(f"bitFlyer secret file not found: {secret_path}")
    if not secret_path.is_file():
        raise SecretLoadError(f"bitFlyer secret path is not a file: {secret_path}")

    try:
        data = json.loads(secret_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise SecretLoadError(f"bitFlyer secret file could not be parsed as JSON: {secret_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise SecretLoadError("bitFlyer secret JSON root must be an object")

    exchange = str(data.get("exchange") or "bitflyer").strip().lower()
    if exchange != "bitflyer":
        raise SecretLoadError(f"unsupported exchange in bitFlyer secret file: {exchange}")

    permission_mode = str(data.get("permission_mode") or "read_only").strip().lower()
    if permission_mode not in {"read_only", "trade_enabled"}:
        raise SecretLoadError(f"unsupported bitFlyer permission_mode: {permission_mode}")

    private_api_enabled = _bool_value(data, "private_api_enabled", False)
    order_send_enabled = _bool_value(data, "order_send_enabled", False)

    if require_enabled and not private_api_enabled:
        raise SecretLoadError("bitFlyer private_api_enabled is false")

    if order_send_enabled and permission_mode != "trade_enabled":
        raise SecretLoadError("order_send_enabled requires permission_mode=trade_enabled")

    return BitflyerPrivateCredential(
        exchange="bitflyer",
        credential_name=str(data.get("credential_name") or "bitflyer_private_api").strip(),
        permission_mode=permission_mode,
        api_key=_require_text(data, "api_key"),
        api_secret=_require_text(data, "api_secret"),
        private_api_enabled=private_api_enabled,
        order_send_enabled=order_send_enabled,
        source_path=secret_path,
    )
