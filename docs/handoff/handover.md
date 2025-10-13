## Btc Ts-ライブ引継ぎ（固定）

※このキャンバスは引継ぎの内容以外書き込みを禁ずる
　大切な内容につきその他の目的で使用せず上書きは禁止です

## 目的

-日々の作業・課題・決定・次アクションを \*\*1 か所\*\に集約し、チャットをまたいだ瞬時の再開を可能にする。

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

##### 以下引継ぎ用の作業報告

---

## 2025-10-13 作業報告・進捗サマリ

### ✅ 今日終わらせた作業

1. **`git_rp_make.ps1` の完全動作化**

   - リポジトリルート誤検出（`C:\Users\mint777` 誤判定）を修正。
   - `.git` 探索ロジックを「スクリプトから 2 階層上優先」へ改修。
   - `git add/commit` の標準エラーを無視し、タグ作成を確実化。
   - 出力警告（CRLF 置換, Permission denied）を完全解消。
   - `git_rp_list.ps1` と連携して **Restore Point の正常登録と一覧表示**を確認。

2. **動作検証ログ**

   - PowerShell 7.5.3 環境で `rp_YYYYMMDD_HHMMSS` 形式のタグ生成を確認。
   - 不要なワーニングなしで終了。UTF-8 入出力・改行問題も解消。
   - `git_rp_list.ps1` の一覧に 4 件の正常タグが出力され、最新タグを確認。

3. **スクリプト安定化**

   - 子 PowerShell 起動時の `-Commit:$true` パラメータ変換問題を把握。
   - 同セッション実行 (`& .\scripts\git\git_rp_make.ps1`) により確実に動作。
   - コミット ON/OFF 両動作の再確認を完了。

### 💡 気づいたこと

- `Find-RepoRoot` のフォールバックが上位フォルダまで登ると **ユーザープロファイル誤認識**を招くため、明示的ルート固定が最も安定。
- `.vscode/` 配下を `.gitignore` に追加すると CRLF 警告を根本的に防げる。
- PowerShell の `-File` 引数では boolean パラメータが string 扱いされるため、直接実行 (`& script.ps1`) の方がトラブルが少ない。
- タグ作成後の出力にメモを短く記録できるため、日単位でのバックアップ運用に最適。

### 🧩 明日（次回）やること

1. **`git_rp_make.ps1` と連携する自動復元スクリプトの試作**

   - 例: `git_rp_restore.ps1` — 最新タグ or 指定タグに一発で戻す仕組み。
   - 安全モード（`--soft`）と強制モード（`--hard`）の 2 段階実装。

2. **`tools/` 下にバックアップ統合ツール作成**

   - `tools/backup_repo.ps1`：`data/`, `logs/`, `config/` の ZIP 化（日時タグ付き）
   - `tools/restore_repo.ps1`：`rp-タグ`と整合するバックアップを選択して展開。

3. **REPO_MAP と Restore Point の自動連携テスト**

   - タグ生成時に `REPO_MAP` のスナップショットを `logs/restore_points/` に保存。
   - Dashboard の「開発者設定」タブからタグを閲覧・選択できるようにする。

4. **監査出力の統合化**

   - `logs/audit.jsonl` に `restore_point.create` イベントを自動記録（actor/site/session/commit/tag）。

### ⚙️ 状況まとめ

- `scripts/git/git_rp_make.ps1` → **安定稼働確認済み（v1.2）**。
- `scripts/git/git_rp_list.ps1` → **一覧正常動作確認済み**。
- `.vscode/` 内警告 → `.gitignore` 追記で抑止予定。
- 次フェーズは **「復元 → 監査 → バックアップ連携」** の 3 段階統合へ。

---

## 引継ぎメモ（Live Handover 用）

**今日やったこと:**

- git バックアップ機構の安定化。タグ・コミット・メモ入力・一覧出力のすべてが正常化。
- これにより作業終了時の「復元ポイント保存」が完全自動化可能になった。

**気付いたこと:**

- PowerShell の boolean 変換仕様が混乱を生む。CLI スクリプトは単一セッション起動を推奨。
- `.vscode/cli` 配下は Git 対象外にすべき（権限・CRLF 問題回避）。
- タグ名・日時形式を統一しているため、リスト/復元/自動保存連携の基盤は完成済み。

**明日やること:**

1. `git_rp_restore.ps1` の実装（タグ指定ロールバック機構）
2. バックアップ統合スクリプト（`tools/backup_repo.ps1`）の雛形作成
3. 監査出力（restore_point.create）と Dashboard タグ閲覧連携の設計
4. `.gitignore` 更新で `.vscode/cli` フォルダを除外

**次回セッション開始時:**

- `git_rp_make.ps1` の安定動作確認済み。以降は **復元・監査連携フェーズ** へ移行。
- `scripts/git/` 系を `tools/backup/` に統合検討。

---

2025-10-13 作業報告・進捗サマリ
今日やったこと（抜粋）

ネットワーク疎通診断
scripts/diag/api_probe.ps1 を整備（IPv4/IPv6 対応、CSV/JSON 出力）。
4 取引所（bitFlyer・Binance・Bybit・OKX）の GET 応答を確認・可視化。

ダッシュボード健全性ビュー
providers.py → tabs/health.py → apps/dashboard.py の流れを統一。
表示順を config/ui/health.yaml: order: で制御し、テーブルは情報重視で非着色化。
カードとタイムラインの整合・色味（淡色系）を最終調整。

設定ポップアップ（歯車アイコン）
右上ギアクリックで設定モーダルを開閉。
警告（experimental_set_query_params など）を解消。
監査・安全書き込みまわり
common/io_safe.py（原子的書込・JSONL 追記）、common/audit.py、common/paths.py の動作確認完了。

ハンドオフ一式（zip）
scripts/handoff/make_handoff.ps1 と make_handoff.bat による ワンクリック生成を実装。
梱包物：env_manifest.yaml、repo_structure.yaml、diagnostics/\*、gpt_context_map.yaml、handover.md、git/HEAD.txt 等。
ZIP 構造の自動検証スクリプトも併設済み。
Git 復元ポイント（軽量タグ運用）
git_rp_make.ps1（タグ作成/任意コミット）と git_rp_list.ps1（一覧表示）を整備。
一覧の整形フォーマット（日時・短 SHA・件名・メモ）を最終確定。

次回タスク（最優先）
コメント付き・中間仕様の復元ポイント（差分パック）
目的: タグだけより「追跡しやすく」、フルバックアップより「軽量」。

仕様方針:
scripts/git/git_rp_make.ps1 に -Pack medium オプションを統合。

実行フロー:
任意コミット（-Commit ON/OFF）
タグ作成（メモ必須）
docs/restore_points/rp-YYYYMMDD_HHMMSS.zip を生成
patch.diff … HEAD との差分
filelist.txt … 変更・未追跡一覧
changed/... … 差分ファイル実体（\*.log など除外）
TAG.txt … タグ・メモ・UTC

除外規則: .gitignore + 明示的除外（.vscode/cli/_, _.lock, _.tmp, _.log など）。
メモ入力: プロンプトで 1 行入力（必須チェック）。
エラー処理: 警告を吸収し、ZIP 生成まで到達を保証。
一発実行: ルートに make_medium_rp.bat を配置し、-Pack medium -Commit ＋メモ入力を自動実行。

検証項目:
タグ作成 → ZIP 生成 → git_rp_list.ps1 一覧反映 → ZIP 内容確認。
大規模変更時の ZIP サイズと生成時間の許容範囲を確認。

次の候補タスク（昨夜のやり残し）
監査タブ（Phase 1B）
providers.audit で audit.tail.jsonl を読み込み、期間・feature・level でフィルタリング。

UI: 検索・期間プリセット・CSV ダウンロード、長文折りたたみ。
しきい値設定の統一
monitoring.yaml を本番値へ戻し、UI 設定から保存/読込を正式化。
色分けや閾値を動的変更可能に。
カード ⇄ グラフ並びリンク（保存対応）
並び順を config/ui/health.yaml: order へ保存/復元。

bitflyer Collector 再接続
IP 制限解除後の再疎通確認 (api_probe.ps1 で再確認)。
OK/WARN/CRIT の再評価を collector スレッドで実施。

Collector 本体の基礎構築（Phase 2 手前）
各取引所アダプタのループ（stub 実装）を用意し、status.json 定期更新まで実現。
例外処理・リトライ・監査書き込みを組み込み。
ユニットテスト最小セット整備
common/\*、svc_health.evaluate、providers.dashboard の smoke テストを tools/ に配置。

---

（以後、2025-10-14 以降の更新はこのセクション末尾に追記する）
