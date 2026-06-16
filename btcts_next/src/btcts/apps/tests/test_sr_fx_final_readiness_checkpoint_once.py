# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_final_readiness_checkpoint_once.py
# desc: Final SR-FX data/UI readiness checkpoint tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

import json
from pathlib import Path

from btcts.apps import sr_fx_final_readiness_checkpoint_once as app


class DummyConfig:
    def __init__(self, root: Path) -> None:
        self.root = root

    def roots(self):
        return {"state": self.root / "state"}


def _audit_ok() -> dict:
    return {
        "ok": True,
        "parity_complete": True,
        "blocked_by": [],
        "decision": "eligible_for_final_human_review_before_autotrade_resume",
        "read_only": True,
        "would_send_to_broker": False,
        "context": {
            "product_code": "FX_BTC_JPY",
            "symbol_raw": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "market_type": "fx",
            "market_role": "execution",
        },
        "summary": {
            "primary_lineage": "continuous_ws",
            "continuous_ws_l3_lineage_present": True,
            "service_stale": False,
            "l4_service_input_blocked": False,
            "orderbook_context_available": True,
            "semantic_context_available": True,
            "trusted_structural_market_state": True,
        },
        "stages": [
            {"stage_id": "l1_public_ws_board", "status": "ok"},
            {"stage_id": "l1_public_ws_executions", "status": "ok"},
            {"stage_id": "l3_market_state_overview", "status": "ok"},
            {"stage_id": "l4_execution_market_service_input", "status": "ok"},
        ],
    }


def test_build_checkpoint_marks_ready_for_human_review_only(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(app, "load_config", lambda: DummyConfig(tmp_path))

    payload = app.build_sr_fx_final_readiness_checkpoint_payload(
        audit_payload=_audit_ok(),
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["ok"] is True
    assert payload["data_ui_integrity_ready_for_final_human_review"] is True
    assert payload["autotrade_resume_authorized"] is False
    assert payload["final_human_review_required"] is True
    assert payload["mode_changed"] is False
    assert payload["blocked_by"] == []
    assert payload["checks"]["primary_lineage_continuous_ws"] is True
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_build_checkpoint_blocks_stale_or_non_fx_audit(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(app, "load_config", lambda: DummyConfig(tmp_path))
    audit = _audit_ok()
    audit["context"]["product_code"] = "BTC_JPY"
    audit["context"]["market_uid"] = "bitflyer.spot.BTC_JPY"
    audit["summary"]["service_stale"] = True

    payload = app.build_sr_fx_final_readiness_checkpoint_payload(
        audit_payload=audit,
        generated_at="2026-06-14T00:00:00Z",
    )

    assert payload["ok"] is False
    assert "execution_product_code_ok" in payload["blocked_by"]
    assert "execution_market_uid_ok" in payload["blocked_by"]
    assert "service_not_stale" in payload["blocked_by"]
    assert payload["autotrade_resume_authorized"] is False
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_main_writes_checkpoint_json(monkeypatch, tmp_path) -> None:
    cfg = DummyConfig(tmp_path)
    state = cfg.roots()["state"]
    audit_path = state / "operator_ui" / "sr_fx_data_lineage_parity_audit.json"
    checkpoint_path = state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(_audit_ok()), encoding="utf-8")
    monkeypatch.setattr(app, "load_config", lambda: cfg)

    rc = app.main()
    data = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert data["ok"] is True
    assert data["paths"]["audit_path"] == str(audit_path)
    assert data["paths"]["checkpoint_path"] == str(checkpoint_path)
    assert data["autotrade_resume_authorized"] is False
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False
