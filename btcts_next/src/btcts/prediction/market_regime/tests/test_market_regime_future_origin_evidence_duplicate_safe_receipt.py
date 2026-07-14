# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_duplicate_safe_receipt.py
# desc: MR-F6.21 duplicate-safe receipt classification and safety-boundary tests.

from __future__ import annotations

from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.future_origin_evidence_dry_run_writer_adapter import (
    MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_duplicate_safe_receipt import (
    DESTINATION_STATE_ABSENT,
    DESTINATION_STATE_ALREADY_SATISFIED,
    DESTINATION_STATE_CONFLICTING,
    DESTINATION_STATE_INCONSISTENT,
    build_origin_evidence_duplicate_safe_receipt,
)

ADAPTER_HASH = "a" * 64
EXPECTED_ARTIFACT_HASH = "b" * 64
CONFLICTING_ARTIFACT_HASH = "c" * 64


def _adapter_result() -> dict[str, object]:
    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_DRY_RUN_WRITER_ADAPTER_VERSION,
        "artifact_kind": "future_origin_evidence_dry_run_writer_adapter_result",
        "adapter_result_id": f"origin-evidence-dry-run-writer-adapter:{ADAPTER_HASH}",
        "adapter_result_hash": ADAPTER_HASH,
        "execution_plan_hash": "d" * 64,
        "artifact_relpath": (
            "prediction/market_regime/future_origin_evidence/"
            "date=2026-07-14/batch-fixture.json"
        ),
        "dedupe_key": "fixture",
        "dry_run_contract_exercised": True,
        "writer_preflight_invoked": True,
        "writer_write_function_imported": False,
        "writer_write_function_invoked": False,
        "writer_invoked": False,
        "execution_performed": False,
        "filesystem_write_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    }


def _receipt(**overrides: object) -> MappingProxyType:
    values = dict(
        adapter_result=_adapter_result(),
        observed_at="2026-07-14T01:30:00Z",
        destination_artifact_exists=False,
        destination_artifact_matches_expected=False,
        expected_adapter_result_hash=ADAPTER_HASH,
        expected_artifact_hash=EXPECTED_ARTIFACT_HASH,
        observed_artifact_hash=None,
    )
    values.update(overrides)
    return build_origin_evidence_duplicate_safe_receipt(**values)


def test_absent_destination_allows_only_separate_write_consideration() -> None:
    result = _receipt()
    assert result["destination_state"] == DESTINATION_STATE_ABSENT
    assert result["blockers"] == ()
    assert result["write_may_be_considered_by_separate_step"] is True
    assert result["duplicate_safely_satisfied"] is False
    assert result["conflict_detected"] is False
    assert result["inconsistent_observation"] is False
    assert result["receipt_is_authorization"] is False


def test_matching_existing_destination_is_already_satisfied() -> None:
    result = _receipt(
        destination_artifact_exists=True,
        destination_artifact_matches_expected=True,
        observed_artifact_hash=EXPECTED_ARTIFACT_HASH,
    )
    assert result["destination_state"] == DESTINATION_STATE_ALREADY_SATISFIED
    assert result["blockers"] == ("destination_artifact_already_satisfied",)
    assert result["write_may_be_considered_by_separate_step"] is False
    assert result["duplicate_safely_satisfied"] is True
    assert result["conflict_detected"] is False


def test_nonmatching_existing_destination_is_conflicting() -> None:
    result = _receipt(
        destination_artifact_exists=True,
        destination_artifact_matches_expected=False,
        observed_artifact_hash=CONFLICTING_ARTIFACT_HASH,
    )
    assert result["destination_state"] == DESTINATION_STATE_CONFLICTING
    assert result["blockers"] == ("destination_artifact_conflict",)
    assert result["write_may_be_considered_by_separate_step"] is False
    assert result["duplicate_safely_satisfied"] is False
    assert result["conflict_detected"] is True


@pytest.mark.parametrize(
    (
        "exists",
        "matches",
        "observed_hash",
        "expected_blocker",
    ),
    (
        (False, True, None, "destination_artifact_state_inconsistent"),
        (False, False, EXPECTED_ARTIFACT_HASH, "destination_artifact_state_inconsistent"),
        (True, False, None, "destination_artifact_hash_missing"),
        (
            True,
            True,
            CONFLICTING_ARTIFACT_HASH,
            "destination_artifact_match_claim_inconsistent",
        ),
        (
            True,
            False,
            EXPECTED_ARTIFACT_HASH,
            "destination_artifact_match_claim_inconsistent",
        ),
    ),
)
def test_inconsistent_destination_observations_fail_closed(
    exists: bool,
    matches: bool,
    observed_hash: str | None,
    expected_blocker: str,
) -> None:
    result = _receipt(
        destination_artifact_exists=exists,
        destination_artifact_matches_expected=matches,
        observed_artifact_hash=observed_hash,
    )
    assert result["destination_state"] == DESTINATION_STATE_INCONSISTENT
    assert result["blockers"] == (expected_blocker,)
    assert result["write_may_be_considered_by_separate_step"] is False
    assert result["inconsistent_observation"] is True


def test_external_adapter_hash_mismatch_fails_closed() -> None:
    with pytest.raises(PermissionError, match="external_adapter_hash_mismatch"):
        _receipt(expected_adapter_result_hash="e" * 64)


def test_adapter_id_and_safety_flags_are_revalidated() -> None:
    bad = _adapter_result()
    bad["adapter_result_id"] = "other"
    with pytest.raises(ValueError, match="adapter_result_id_mismatch"):
        _receipt(adapter_result=bad)

    bad = _adapter_result()
    bad["writer_invoked"] = True
    with pytest.raises(ValueError, match="unsafe_adapter_flag:writer_invoked"):
        _receipt(adapter_result=bad)


def test_artifact_hashes_must_be_sha256_hex() -> None:
    with pytest.raises(ValueError, match="expected_artifact_hash_invalid"):
        _receipt(expected_artifact_hash="not-a-hash")
    with pytest.raises(ValueError, match="observed_artifact_hash_invalid"):
        _receipt(
            destination_artifact_exists=True,
            observed_artifact_hash="not-a-hash",
        )


def test_receipt_is_deterministic_immutable_and_nonexecuting() -> None:
    first = _receipt()
    second = _receipt()
    assert first["receipt_id"] == second["receipt_id"]
    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["writer_write_function_imported"] is False
    assert first["writer_write_function_invoked"] is False
    assert first["writer_invoked"] is False
    assert first["execution_performed"] is False
    assert first["filesystem_read_performed"] is False
    assert first["filesystem_write_performed"] is False
    assert first["writes_dhot"] is False
    assert first["scheduler_enabled"] is False
    with pytest.raises(TypeError):
        first["destination_state"] = DESTINATION_STATE_CONFLICTING


def test_module_exposes_no_writer_filesystem_cli_or_scheduler_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_duplicate_safe_receipt as module

    assert hasattr(module, "build_origin_evidence_duplicate_safe_receipt")
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "Path")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
