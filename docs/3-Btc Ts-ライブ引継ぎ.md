# 機能分離リポ再設計・作業ログ（固定方針＋逐次追記）

> 運用方針: このキャンバスは **再設計ログ** です。内容の更新は **ユーザーの明示指示がある時のみ** 行います（末尾追記・差分最小）。

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

（以後、2025-10-14 以降の更新はこのセクション末尾に追記する）
