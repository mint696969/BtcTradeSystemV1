# path: ./docs/architecture/L2_L3_SEPARATION_LIGHTWEIGHT_VERIFICATION_SPEC_2026-04-04.md
# desc: Specification for lightweight verification of L2 and L3 separation.
# L2 / L3 分離 lightweight verification 仕様書

更新日: 2026-04-04
位置づけ: 構造分離 closeout 用の軽量検証仕様 / docs 再配置用ドラフト
対象: `btcts_next/src/btcts/`

---

## 1. この仕様書の目的
本仕様書は、BTC Trade System vNext における L2 / L3 分離が、

- 構造上
- import 依存上
- live runtime 上
- 運用導線上

の各観点で最低限成立しているかを、軽量かつ継続可能な方法で確認するための仕様書である。

ここで言う lightweight verification は、完全証明ではない。
目的は次の3つである。

1. 分離済みと主張してよい最低ラインを固定する
2. 次の docs 整合と L4 設計へ進むための gate を明文化する
3. 将来の review / GPT handoff / runbook 化で再利用できる形にする

---

## 2. 前提
2026-04-04 時点で、repository の基準状態は次のとおりである。

- L2 の正規 ownership は `ingestion/l2_canonical/`
- L3 の正規 ownership は `processing/l3_market_semantics/`
- 現行 live runtime の主系は `collector_vnext/`
- 旧 UI / 旧 collector / 旧 watchdog 系は `archive/legacy_2026-04-04/` 側へ退避済み
- live restart 検証では unified watchdog / daemon / ws lanes / raw / canonical 継続出力に白が付いている

この仕様書は、その現実を前提に検証項目を定義する。

---

## 3. 何をもって「分離できている」とみなすか
L2 / L3 分離の lightweight 合格条件は、次の4系統を満たすこととする。

### A. ownership 分離
- L2 の事実整形・構造再構成の owner が `ingestion/l2_canonical/` にある
- L3 の市場意味解釈の owner が `processing/l3_market_semantics/` にある

### B. import 分離
- collector 実行系が L3 の truth owner に直接依存していない
- ingestion 側から processing への逆流依存がない
- consumer 側が ingestion を直接使って意味解釈していない

### C. runtime 分離
- collector の restart / live 取得が成立する
- raw / canonical 出力が継続する
- board / executions が再接続し live に戻る

### D. legacy 隔離
- 旧 mainline 導線が archive に追いやられている
- mainline 側の active path が legacy package を参照しない

---

## 4. 検証の考え方
この検証は「L3 が全部完成しているか」を問うものではない。
問うのは、

- L2 と L3 の owner が混ざっていないか
- collector が再び semantic owner に戻っていないか
- 新構造の上で live runtime が成立しているか

である。

したがって、本仕様書では以下を明確に区別する。

### この検証で白が付くこと
- 分離方向が壊れていない
- collector は主に L1/L2 寄り責務で動いている
- L3 owner は processing 側に維持されている

### この検証だけでは白が付かないこと
- L3 のすべての semantic quality
- L4 shared-first 設計の完成
- consumer bridge 統一の完了
- market_engine と L3 の全接続品質

---

## 5. 検証項目

# 5.1 構造 verification

## 5.1.1 目的
フォルダ構造と ownership の分離が repository 上で維持されているかを確認する。

## 5.1.2 合格条件
- `ingestion/l2_canonical/` が存在する
- `processing/l3_market_semantics/` が存在する
- `market_engine/execution/` が存在する
- `collector_vnext/` が live runtime 実装として存在する
- 旧 mainline 系は `archive/legacy_2026-04-04/` へ退避済みである

## 5.1.3 確認方法
- repo tree / file list 確認
- active path と archive path の分離確認

## 5.1.4 判定観点
### OK
- ownership 用 package が存在し、役割が分かれている

### NG
- collector 側に semantic owner 相当の package が再作成されている
- L3 owner が consumer 側へ散乱している

---

# 5.2 import verification

## 5.2.1 目的
責務分離が import 方向でも壊れていないかを確認する。

## 5.2.2 合格条件
### collector 側
- `collector_vnext/` から `processing/l3_market_semantics` への直接 import がない
- `collector_vnext/` から `market_engine/execution` への直接 import がない

### ingestion 側
- `ingestion/` から `processing/` への逆流 import がない

### consumer 側
- `apps/operator_ui/` から `ingestion/` 直参照で意味解釈していない

### market_engine 側
- `market_engine` が再び assembler 的な巨大 mixed ownership に戻っていない

## 5.2.3 既知の事実
2026-04-04 時点の静的確認では、次は良好であった。

- `collector_vnext` から `processing.l3_market_semantics` 直接 import 痕跡は未確認
- `ingestion` から `processing` 逆流 import 痕跡は未確認
- `apps/operator_ui` から `ingestion` 直参照痕跡は未確認
- `market_engine.assembler` package 参照痕跡は未確認

## 5.2.4 要注意観点
- `collector_vnext/rate_runtime.py` の legacy 依存
- `market_engine/execution/assembler_engine.py` という命名残り

これらは即 NG ではないが、closeout 対象として監視する。

---

# 5.3 runtime verification

## 5.3.1 目的
分離後の live runtime が、新構造の mainline 上で実際に成立しているかを確認する。

## 5.3.2 合格条件
- Unified Supervisor から restart request が通る
- watchdog が request を ack する
- 新 daemon PID が立つ
- board WS が `LIVE` に復帰する
- executions WS が `LIVE` に復帰する
- raw / canonical 出力が継続する
- checkpoint が更新される

## 5.3.3 実測で確認できたこと
2026-04-04 の live 実測で次を確認済み。

- restart request 受理
- daemon PID 切替
- cycle_no 再起動後に再進行
- `unified_origin_status.json` が `LIVE` に復帰
- `unified_executions_status.json` が `LIVE` に復帰
- trade_count が再び増加
- `collector_raw` / `market_data` への出力継続

## 5.3.4 何を意味するか
この runtime 検証は、少なくとも次を示す。

- 現在動いている collector は新構造の `collector_vnext` 系である
- 旧 mainline collector をそのまま回しているわけではない
- L1/L2 寄りの実運転経路は実地で成立している

## 5.3.5 この runtime 検証でまだ言い切れないこと
- L3 が常時独立出力として完成していること
- L4 が shared-first で完成していること
- consumer bridge 統一が終わっていること

---

# 5.4 legacy isolation verification

## 5.4.1 目的
旧 mainline 実装が active path に混入していないかを確認する。

## 5.4.2 合格条件
- 旧 UI / 旧 collector / 旧 watchdog 系が archive 側に移されている
- mainline の active path が archive を参照していない
- 運用導線が `collector_vnext` unified 系へ寄っている

## 5.4.3 確認観点
- `archive/legacy_2026-04-04/` の存在
- mainline における旧 import の有無
- launcher / tools の active path

## 5.4.4 注意点
一部 scripts / tools に命名や旧導線の残りがある可能性はある。
ただし lightweight verification では、mainline active path に悪影響がないことを最低ラインとする。

---

## 6. テスト項目一覧

### 6.1 静的テスト
1. package existence check
2. import grep check
3. active path / archive path separation check
4. legacy import residue check

### 6.2 実行テスト
1. unified supervisor restart
2. daemon pid rollover check
3. board ws live recovery check
4. executions ws live recovery check
5. raw / canonical output continuity check
6. checkpoint update check

---

## 7. lightweight verification の合格基準
以下をすべて満たした場合、L2 / L3 分離 lightweight verification は合格とする。

### 必須
- 構造 verification 合格
- import verification 合格
- runtime verification 合格
- legacy isolation verification 合格

### 許容される残課題
- naming 残り
- docs の理想構造と現実構造の未完全一致
- L4 package 未展開
- audit path などの運用付帯課題

### 不合格条件
- collector が semantic owner に戻っている
- ingestion から processing への逆流依存が発生している
- consumer が ingestion を直接使って意味解釈している
- 旧 mainline collector 導線が active path に残っている
- restart / live 継続が成立しない

---

## 8. 2026-04-04 時点の暫定判定
2026-04-04 時点では、lightweight verification は次の暫定判定が妥当である。

### 判定
- conditional pass

### 根拠
- ownership 分離は package 上で成立
- import 分離は静的確認で大きな逆流が見つかっていない
- live restart と raw / canonical 継続出力は実測で成立
- legacy mainline の大部分は archive 側に退避済み

### 条件付きとする理由
- L3 / L4 の downstream 接続までは未完
- 一部 naming / legacy residue / docs 不整合が残る
- tools / scripts の active path 完全整理は後続対象

---

## 9. この検証の次にやるべきこと
本仕様書で lightweight verification が定義できた後の次アクションは次の順とする。

1. docs 再配置
2. lightweight verification の runbook 化
3. import 監査の再利用可能化
4. L4 shared-first 設計
5. consumer bridge 統一

---

## 10. 一言でまとめると

```text
L2/L3 分離の lightweight verification とは、
ownership・import・runtime・legacy isolation の4点で、
分離方向が壊れていないことを確認する検証である。
```
