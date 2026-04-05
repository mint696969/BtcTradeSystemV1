# path: ./docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_CHECKLIST_2026-04-04.md
# desc: Checklist for lightweight verification of L2 and L3 separation.
# L2 / L3 分離 lightweight verification チェックリスト

更新日: 2026-04-04
位置づけ: 運用・レビュー・handoff 用チェックリスト / docs 再配置用ドラフト
対象: `btcts_next/src/btcts/`
前提仕様:
- `tmp/LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md`
- `tmp/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_SPEC_2026-04-04.md`

---

## 1. このチェックリストの使い方
このチェックリストは、L2 / L3 分離が壊れていないかを軽量に確認するための実務用 runbook である。

想定用途は次のとおり。

- docs closeout 前の最終確認
- 再起動前後の健全性確認
- 次 GPT への handoff
- 仕様と実装のズレ点の棚卸し

判定は次の3段階で記録する。

- ✅ OK
- ⚠️ 要注意
- ❌ NG

---

## 2. 最終判定ルール
以下を満たせば lightweight verification は合格とする。

- 構造チェックが OK
- import チェックが OK
- runtime チェックが OK
- legacy isolation チェックが OK
- 要注意が残っていても、active path を壊していなければ conditional pass とする

以下があれば不合格とする。

- collector が semantic owner に戻っている
- ingestion から processing への逆流依存がある
- consumer が ingestion を直接使って意味解釈している
- 旧 mainline 導線が active path に残っている
- restart / live recovery / raw / canonical 継続が崩れている

---

## 3. 構造チェック

### 3.1 package existence
- [ ] `btcts_next/src/btcts/ingestion/l2_canonical/` が存在する
- [ ] `btcts_next/src/btcts/processing/l3_market_semantics/` が存在する
- [ ] `btcts_next/src/btcts/processing/features/` が存在する
- [ ] `btcts_next/src/btcts/market_engine/execution/` が存在する
- [ ] `btcts_next/src/btcts/collector_vnext/` が存在する

### 3.2 ownership 読み分け
- [ ] L2 ownership は `ingestion/l2_canonical/` 側で説明可能
- [ ] L3 ownership は `processing/l3_market_semantics/` 側で説明可能
- [ ] collector_vnext は live runtime / L1-L2 寄りとして説明可能
- [ ] market_engine は execution / profiles / onboarding 文脈として説明可能

### 3.3 legacy archive
- [ ] `archive/legacy_2026-04-04/` が存在する
- [ ] 旧 UI / 旧 collector / 旧 health 系が archive 側へ移っている

---

## 4. import チェック

### 4.1 collector 側の逆流確認
- [ ] `collector_vnext/` から `processing/l3_market_semantics` 直接 import がない
- [ ] `collector_vnext/` から `market_engine/execution` 直接 import がない
- [ ] collector が semantic helper の owner に戻っていない

### 4.2 ingestion 側の逆流確認
- [ ] `ingestion/` から `processing/` 逆流 import がない
- [ ] L2 package に意味解釈 helper が混入していない

### 4.3 consumer 側の越境確認
- [ ] `apps/operator_ui/` が ingestion を直接使って意味解釈していない
- [ ] consumer 側に L3 相当の truth owner が生えていない

### 4.4 market_engine 側の再混入確認
- [ ] assembler package が mainline に存在しない
- [ ] execution が L3 owner を再内包していない
- [ ] profiles が execution と L3 を仲介する薄い policy 層として保たれている

### 4.5 naming / residue の記録
- [ ] `assembler_engine.py` など名称残りを記録した
- [ ] legacy import 候補があれば記録した
- [ ] ただし active path へ悪影響がないことを確認した

---

## 5. runtime チェック

### 5.1 supervisor / daemon
- [ ] restart request が受理される
- [ ] `unified_supervisor_status.json` の `last_requested_at` が更新される
- [ ] `unified_supervisor_status.json` の `last_completed_at` が更新される
- [ ] `acked_request_id` が更新される
- [ ] `daemon_pid` が切り替わる

### 5.2 daemon health
- [ ] `unified_daemon_status.json` が `RUNNING` に戻る
- [ ] `cycle_no` が再進行する
- [ ] `last_success_ts` が更新され続ける
- [ ] `lane_health.rest_lane` が `running` である

### 5.3 board ws recovery
- [ ] `unified_origin_status.json` が `LIVE` に戻る
- [ ] `lane_state` が `live` に戻る
- [ ] `last_error` が null である
- [ ] `saw_snapshot = true`
- [ ] `saw_delta = true`

### 5.4 executions ws recovery
- [ ] `unified_executions_status.json` が `LIVE` に戻る
- [ ] `lane_state` が `live` に戻る
- [ ] `trade_count` が再び増え始める
- [ ] `last_error` が null である

### 5.5 output continuity
- [ ] raw 出力が継続する
- [ ] canonical 出力が継続する
- [ ] checkpoint が更新される
- [ ] 再起動後もしばらく更新が止まらない

---

## 6. legacy isolation チェック

### 6.1 active path
- [ ] 現行 live runtime が `collector_vnext` 系で説明できる
- [ ] 旧 `collector/` 主系を直接回していない
- [ ] 旧 `ui/` 主系を直接回していない

### 6.2 archive separation
- [ ] archive 内コードが mainline 運用導線に再混入していない
- [ ] tools / scripts に旧導線が残っていても、active path ではないと説明できる

### 6.3 notes
- [ ] archive 化済み legacy の残件をメモした
- [ ] closeout で整理すべき scripts / tools をメモした

---

## 7. レイヤ理解チェック
仕様理解が崩れていないかを確認するための口頭説明用チェック。

### 7.1 L1 を説明できるか
- [ ] L1 は取得責務だと説明できる
- [ ] L1 は raw と運転状態を書くと説明できる
- [ ] L1 は意味を作らないと説明できる

### 7.2 L2 を説明できるか
- [ ] L2 は canonical 化と構造再構成だと説明できる
- [ ] L2 は事実整形であり意味付けではないと説明できる
- [ ] L2 は canonical / checkpoint / structural state に関与すると説明できる

### 7.3 Features を説明できるか
- [ ] Features は中立特徴量だと説明できる
- [ ] Features はまだ semantic label を作らないと説明できる

### 7.4 L3 を説明できるか
- [ ] L3 は市場意味の owner だと説明できる
- [ ] pressure / wall / sweep / trust / continuity は L3 だと説明できる
- [ ] L3 は consumer を知らないと説明できる

### 7.5 L4 を説明できるか
- [ ] L4 は truth を再定義しないと説明できる
- [ ] L4 は consumer 向け shared-first 整形だと説明できる
- [ ] L4 は next phase の主要対象だと説明できる

---

## 8. 実行ログ記録欄

### 実施日
- [ ] 実施日時を記録した

### 実施者
- [ ] 実施者を記録した

### 実施対象
- [ ] 対象 branch / snapshot / build 状態を記録した

### 主要観測値
- [ ] supervisor_pid
- [ ] daemon_pid (before/after)
- [ ] request_id / acked_request_id
- [ ] cycle_no (before/after)
- [ ] board ws state
- [ ] executions ws state
- [ ] trade_count
- [ ] checkpoint ts

---

## 9. 判定メモ欄

### 構造
- 判定:
- 根拠:

### import
- 判定:
- 根拠:

### runtime
- 判定:
- 根拠:

### legacy isolation
- 判定:
- 根拠:

### 総合
- 判定:
- 補足:

---

## 10. 2026-04-04 時点の参考判定
参考として、2026-04-04 時点の観測ベースでは次の評価が妥当である。

### 構造
- ✅ OK

### import
- ✅ OK
- ⚠️ naming residue / legacy residue は一部あり

### runtime
- ✅ OK
- restart / daemon rollover / board live / executions live / raw-canonical continuity を実測で確認

### legacy isolation
- ✅ OK
- 一部 tools / scripts の整理余地は残る

### 総合
- ✅ conditional pass

---

## 11. 一言でまとめると

```text
このチェックリストで確認するのは、
L2/L3 分離が「理想どおり完璧か」ではなく、
ownership・import・runtime・legacy isolation の4点で
壊れていないかどうかである。
```
