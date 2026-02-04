## 目的

-このCTXは「次のGPTが30分以内に安全に作業再開できる」ことを目的とし、日々の作業・課題・決定・次アクションを \*\*1 か所\*\に集約し、チャットをまたいだ瞬時の再開を可能にする。

## 記入フォーマット（必須）

```
## <YYYY-MM-DD <短い見出し
  - 作業メモ
    ...

  - 完了タスク
    ...

  - 次の候補タスク
    A) ...

    B) ...

  - 参照: PR/コミット/スクショ/ログ へのリンク or 要約
```

- 作業報告は末尾に追記していくこと。
- 無駄な改行は避け無駄に長くしない事。
- “意味のある粒度”で書く（誰でも追従できるように）。
- 決定事項は `docs/` の該当ファイル（計画/ADR 等）へ\*\*要約のみ\*\*反映。

---

##### 以下直近の作業報告

---

作業報告書（handover 追記用）
概要

Codex 導入を前提とした 開発環境の整地フェーズとして、
Collector / Health / RateControl / Watchdog 周辺の テストツール群の整理・配置統一・挙動確認を実施した。

目的は以下の3点。

GPT / Codex が迷わない構成にする

Phase1（24/7運用前）の安全確認を自動テストで再現できる状態にする

実運用コードとテストコードの責務を明確に分離する

今回やったこと
1. テストスクリプトの配置・命名ルール統一

すべてのテスト用スクリプトを以下に統一

C:\BtcTradeSystem\tools


命名規則

test_*.ps1
test_*.py


テスト成果物（config / data / logs）はすべて

C:\BtcTradeSystem\tmp\<test_name>\...


に出力する方針を確定。

2. 各テストスクリプトの実態把握・動作確認
確認済みテストツール

test_collector.ps1

test_collector_entry.py

test_health.ps1

test_rate_control_phase1.py

test_phase1_cc_checks.ps1

watchdog_collector.ps1（※実運用寄りだが Phase1 テストでも使用）

それぞれについて：

何をテストするか

単体 / 結合 / 疑似運用のどれか

依存関係（watchdog / dummy collector など）

生成物（status.json / audit.jsonl / log）

を確認し、
仕様書として記述できる状態まで理解を整理した。

3. watchdog_collector.ps1 の安全性・挙動確認

-UseDummyCollector モードでの挙動を重点確認

以下を確認済み：

lock ファイルの生成・解放

watchdog 起動 / exit の reason 出力

dummy collector（test_collector_entry.py）の起動

loop.tick の定期出力

status / audit が存在しなくても異常終了しないこと

特に重要な点：

watchdog_collector.ps1 は test ツールではない

実運用 Supervisor

test 側（test_phase1_cc_checks.ps1 等）から「被験体」として起動される

4. 「狙った結果が出ない」原因の切り分け

昨日から挙動が安定しなかった主因は以下。

テストコードと運用コードの責務境界が曖昧だった

相対パス／PSScriptRoot／PYTHONPATH の前提が混在

watchdog / dummy collector / test runner が 同一キャンバスで混線

→ 配置と役割を分離したことで、現在は再現性が取れている

現在の到達点

Phase1 周辺のテストツールは すべて tools 配下に集約

watchdog / collector / dummy collector の関係性が明確化

テスト結果（status / audit / log）を人間が読んで判断できる状態

Codex が参照しても「どれがテストで、どれが本体か」迷わない構成

次回タスク（おすすめ順）
優先度 高

各 test_.ps1 / test_.py の仕様書を docs 化

test_collector.ps1 と同レベルの説明を全テストに付与

「何を壊すテストか」「PASS とは何か」を明示

Phase1 完了条件チェックリストの明文化

どのテストが PASS すれば Phase1 OK なのか

手動確認が必要な項目の切り分け

優先度 中

watchdog の exitReason を前提にした 監視ルール整理

loop.ended_or_external_stop

watchdog.stop.too_many_fails

guard.disk.stop など

テスト用 ENV 一覧の docs 化

BTC_TS_* 系

PYTHONPATH

BTC_TS_TEST_MODE 系

作業中の気づき・注意点

「差し替え指示は行番号 or 一意なコード断片必須」

catch / finally が多い PowerShell では曖昧指示は事故る

watchdog / collector は

「動いているように見えて何もしていない」状態が最も危険

log / jsonl を必ずセットで確認する運用が必須

dummy collector は テストの命

実取引所を叩かず Phase1 を検証できるのは非常に強い

総評

今回の作業は「機能追加」ではないが、

将来の開発スピードと事故率を決定づける、非常に重要な整地

になっている。

この状態で Codex を使い始めるのは 正解。
次フェーズは安心して進めてよい。