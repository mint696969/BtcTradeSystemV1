# path: ./tools/test_collector_vnext_board_internal_risk_audit.py
# desc: Audit internal collector_vnext WS board risks before blaming exchange-side behavior.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8")


def _contains(text: str, needle: str) -> bool:
    return needle in text


def _risk(
    *,
    risk_id: str,
    severity: str,
    title: str,
    evidence: list[str],
    why_it_matters: str,
    likely_effect: str,
    suggested_action: str,
) -> dict:
    return {
        "risk_id": risk_id,
        "severity": severity,
        "title": title,
        "evidence": evidence,
        "why_it_matters": why_it_matters,
        "likely_effect": likely_effect,
        "suggested_action": suggested_action,
    }


def main() -> int:
    ws_provider = _read_text("btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py")
    ws_canonical = _read_text("btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py")
    book_rebuilder = _read_text("btcts_next/src/btcts/collector_vnext/orderbook/book_rebuilder.py")
    book_apply = _read_text("btcts_next/src/btcts/collector_vnext/orderbook/book_apply.py")
    rebuild_long = _read_text("tools/test_collector_vnext_board_ws_rebuild_long.py")
    rebuild_zone = _read_text("tools/test_collector_vnext_board_ws_rebuild_zone_diagnose.py")

    risks: list[dict] = []

    if _contains(rebuild_long, "for live_row, snap_row in zip("):
        risks.append(
            _risk(
                risk_id="compare_positional_zip",
                severity="high",
                title="比較器が順位依存すぎる",
                evidence=[
                    "tools/test_collector_vnext_board_ws_rebuild_long.py: _top_match_count() uses zip(live_top, snap_top)",
                ],
                why_it_matters="1段の挿入/削除や順位ずれだけで後続レベルが大量不一致になる。",
                likely_effect="片側崩れ・全面崩れを実態以上に大きく見せる可能性がある。",
                suggested_action="positional exact とは別に set-overlap / price-overlap / same-price-size-mismatch 指標を追加する。",
            )
        )

    if _contains(ws_canonical, '"continuity_state": "unknown"') or _contains(ws_canonical, '"continuity_state": "unknown",'):
        risks.append(
            _risk(
                risk_id="canonical_continuity_unknown",
                severity="high",
                title="canonical 化で連続性情報が unknown 固定",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py: continuity_state = 'unknown'",
                ],
                why_it_matters="後段が gap / resync / stable continuity を機械的に区別できない。",
                likely_effect="trust 判定や rebuild 必要判定が鈍る。",
                suggested_action="少なくとも snapshot / delta / first-after-snapshot / gap-like observation を区別できる暫定 continuity metadata を入れる。",
            )
        )

    if _contains(ws_canonical, '"prev_event_id": None') and _contains(ws_canonical, '"snapshot_id": None'):
        risks.append(
            _risk(
                risk_id="canonical_linkage_missing",
                severity="medium",
                title="canonical 化で event linkage が欠落",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/transforms/ws_board_to_canonical.py: prev_event_id/base_snapshot_id/snapshot_id are None",
                ],
                why_it_matters="どの snapshot に対する差分列かを後段で追えない。",
                likely_effect="rebuild credibility を later-stage で説明しにくい。",
                suggested_action="内部採番でもよいので chain linkage を保持する。",
            )
        )

    if _contains(ws_provider, "source_sequence=None"):
        risks.append(
            _risk(
                risk_id="provider_source_sequence_missing",
                severity="high",
                title="provider 側で source_sequence が無い",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py: source_sequence=None",
                ],
                why_it_matters="snapshot / diff の厳密順序軸が後段に渡らない。",
                likely_effect="比較時点ズレと rebuild failure を分離しにくい。",
                suggested_action="message local sequence / receive local sequence を少なくとも採番する。",
            )
        )

    if _contains(ws_provider, 'snapshot_channel = f"lightning_board_snapshot_') and _contains(ws_provider, 'diff_channel = f"lightning_board_'):
        risks.append(
            _risk(
                risk_id="dual_channel_alignment_risk",
                severity="medium",
                title="snapshot と diff が別 channel で時点整合に注意が必要",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/providers/bitflyer_ws_board.py: snapshot_channel and diff_channel are subscribed independently",
                ],
                why_it_matters="次 snapshot をそのまま diff chain の truth とみなす比較は時点ズレを含む可能性がある。",
                likely_effect="比較器が exchange-side limitation を rebuild failure と誤認する。",
                suggested_action="比較時に receive_ts / local seq / compare window metadata を必ず添える。",
            )
        )

    if _contains(book_rebuilder, 'if not self.snapshot_loaded:\n                return'):
        risks.append(
            _risk(
                risk_id="pre_snapshot_diff_drop",
                severity="medium",
                title="snapshot 前 diff は無言で捨てる",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/orderbook/book_rebuilder.py: delta before snapshot is silently ignored",
                ],
                why_it_matters="接続直後の状態遷移を記録せずに捨てるので continuity 監査情報が残らない。",
                likely_effect="初期ズレの説明が弱くなる。",
                suggested_action="drop count / first_snapshot_wait / pre_snapshot_diff_seen を明示メトリクスにする。",
            )
        )

    if not _contains(book_rebuilder, "spread(") and not _contains(book_rebuilder, "crossed"):
        risks.append(
            _risk(
                risk_id="rebuilder_no_sanity_guard",
                severity="medium",
                title="rebuilder に妥当性チェックが無い",
                evidence=[
                    "btcts_next/src/btcts/collector_vnext/orderbook/book_rebuilder.py: no crossed/sanity validation",
                    "btcts_next/src/btcts/collector_vnext/orderbook/book_apply.py: raw updates applied directly",
                ],
                why_it_matters="片側崩れや crossed をその場で異常として検出できない。",
                likely_effect="壊れた state がそのまま比較や downstream signal に流れる。",
                suggested_action="best bid <= best ask sanity check と anomaly flag を追加する。",
            )
        )

    if _contains(rebuild_zone, "connect_and_stream_board(") and not _contains(rebuild_zone, "canonical_board_event("):
        risks.append(
            _risk(
                risk_id="diagnostics_bypass_canonical_path",
                severity="medium",
                title="診断ツールが canonical 経路を通っていない",
                evidence=[
                    "tools/test_collector_vnext_board_ws_rebuild_zone_diagnose.py: provider payload is used directly",
                ],
                why_it_matters="本番導線と診断導線の意味差が残る。",
                likely_effect="本番で起きる欠落と、診断で見える欠落が一致しない可能性がある。",
                suggested_action="provider -> canonical -> rebuild を通す監査系を別途用意する。",
            )
        )

    summary = {
        "risk_count": len(risks),
        "high_count": sum(1 for x in risks if x["severity"] == "high"),
        "medium_count": sum(1 for x in risks if x["severity"] == "medium"),
        "low_count": sum(1 for x in risks if x["severity"] == "low"),
    }

    report = {
        "ok": True,
        "audit_type": "collector_vnext_board_internal_risk",
        "summary": summary,
        "risks": risks,
        "operator_conclusion": (
            "internal_risks_exist_and_should_be_reduced_before_strong_exchange-side conclusions"
            if risks
            else "no_obvious_internal_risk_found_in_quick_audit"
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())