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

Supervisor（Watchdog）Phase1 完了報告書

（handover 記載用）

1. このチャットでやったこと（実績）
1.1 Supervisor（Watchdog）Phase1 実装・確定

scripts/watchdog_collector.ps1 を Phase1仕様として完成

Collector を 24/7 運用するための外部 Supervisor として以下を実装・検証

多重起動防止（watchdog.lock / watchdog.pid）

Collector 起動（実 / ダミー）

環境変数の 明示注入（手動起動との差異排除）

status.json(ts_unix) による進捗監視

ハング検知 → kill → backoff → 再起動

fails.reset による誤停止防止

max_failures 到達時の Supervisor 自己停止

no_data 連続検知の安全停止

logs ドライブ残量による安全弁

監査ログ（supervisor_collector.log / .jsonl）

1.2 Phase1 テスト方針の明確化

実 Collector は使わないと判断

取引所 / API / endpoint が未登録の現状では事故リスクが高い

ダミー Collector（tmp/test_collector_entry.py）で

「監視ロジックが正しく自己修復するか」のみを検証

ハング → kill → backoff → 再起動 → fails.reset のループを長時間確認

1.3 テスト再現性の固定

手動コマンドのバラつきを排除するため

scripts/collector_watchdog_test.ps1 を作成

env セット・起動条件・ログ確認を 1発で再現可能にした

1.4 仕様書の統合作業

追記が増えすぎたため、

Supervisor（Watchdog）正式仕様書を全文再構成

Phase1 の責務・運用ルール・禁止事項をすべて明文化

「lock busy が出るのは正常動作」など、運用時に迷いやすい点も明記

2. 作業中に気が付いたこと（重要な知見）
2.1 Supervisor と Collector の責務分離は必須

Collector に監視や再起動を持たせる設計は破綻しやすい

Supervisor を 完全に外部プロセスとして切った判断は正解

Phase2 以降もこの境界は絶対に崩さないほうが良い

2.2 環境変数は「明示注入」しないと事故る

PowerShell から python を起動すると

手動実行と env が微妙にズレる

Watchdog 側で PYTHONPATH / BTC_TS_* を 毎回注入することで

「起動するが import できない」系の事故を完全に排除できた

2.3 lock ファイルは「消せばいい」ではない

watchdog.lock が busy なのは 正常

status.json の ts を見て 安全条件付きで stale lock だけ消す

このルールを仕様に明文化したのは大きい

手動削除運用は明確に禁止したほうがよい

2.4 fails.reset が無いと実運用は破綻する

一時的な API 停滞・GC・IO詰まりなどで

fails が累積 → Supervisor が勝手に止まる

「進捗が見えた瞬間に fails を 0 に戻す」設計は必須

2.5 PSScriptAnalyzer 警告は早めに潰すべきだった

後回しにすると

参照箇所が増えて差分が大きくなる

今回は VSC 設定＋関数整理で 警告ゼロにできた

今後の ps1 は「警告ゼロを前提」に進めたほうが良い

3. 現在の到達点（Phase1 完了定義）

ダミー Collector で以下がすべて確認済み

ハング検知

kill → backoff → 再起動

fails.reset の動作

max_failures 到達時の Supervisor 停止

Ctrl+C による安全停止

Supervisor の 監視ロジック自体は Phase1 合格

4. 次回タスク（次フェーズ）
4.1 次の実装テーマ

設定（取引所登録・エンドポイント制御）

具体的には：

取引所定義（exchanges.yaml 等）

有効/無効の切り替え

エンドポイント粒度での制御

Collector が「何を回すか」を 設定だけで決められる構造

4.2 Supervisor 側でやらないこと（重要）

取引所の中身

API仕様

レート制御
→ これらは Collector / 設定層の責務

5. 次のタスクで気を付けること（注意点）

Supervisor を触らない

Phase1 で確定した仕様は凍結

Phase2 以降は「設定と Collector 側」で吸収する

設定は「追加」ではなく「差し替え前提」

exchanges.yaml / endpoints.yaml は

後から GPT が見ても意図が分かる構造にする

実 Collector テストは最後

設定が固まるまではダミーで良い

いきなり実 API を叩かない

「起動条件」を必ず固定化する

env / config / entrypoint が曖昧だと

再現不能なバグになる

6. 総括

Supervisor（Watchdog）Phase1 は 設計・実装・運用ルールまで含めて完了

次に進む準備は整っている

次フェーズは 「設定が主役」
Supervisor は触らず、Collector を設定駆動にしていく段階