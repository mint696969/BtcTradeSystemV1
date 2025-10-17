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

本日の完了タスク（2025-10-14）
git_rp_make.ps1：ブール引数修正、差分 ZIP 出力・メモ付き復元ポイント作成を安定化
git_full_backup.ps1：出力先を外部 BtcTradeSystemV1_git\git_full に統一、bundle 検証・clone テスト完了
git_rp_list.ps1：rp 差分・full bundle の重複排除と統合一覧出力を安定化（詳細表示含む）
make_handoff.ps1：外部保存変更に対応（git 関連の影響なし確認済）
差分検証手順を確立（git apply --check によるパッチ整合性テスト）
フルバックアップ＋差分検証の最終統合テスト完了（final-check OK）
Git Rp List の仕様書を docs に正式配置

次回タスク
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

2025-10-15 作業報告・進捗サマリ
✅ 今日終わらせた作業
bitFlyer 公開 API アダプタ bitflyer_public.py 実装・完成
/v1/executions（約定履歴）と /v1/board（板情報）の両エンドポイントを標準ライブラリのみで実装。
Execution dataclass を追加し、整形済み出力を保証。
board() で mid_price / best_bid / best_ask / bids / asks / raw_count を返す軽量サマリを構築。
スモークテストで mid_price, bids3, asks3 を正常取得確認。
collector core ワーカー (worker.py) 拡張
fetch() に bitflyer board 分岐を新規追加。
→ BitflyerPublic.board() を呼び出し mid/best などを返却。
run_once() で trades と board の両ケースを正しく JSONL スナップショット出力化。
保存は UTC 運用（JST 表示は UI 層で吸収）で統一。
status.json に topic=board を追加し、OK 判定および retries/cause/notes 更新を確認。
common/audit.py の安定化
監査出力を StorageRouter 対応へ一本化（ENV → local 自動フォールバック）。
環境文脈 actor/site/session/task/mode を set_context() で設定可能に。
\_redact() による簡易マスキングを追加。
core/status.py 強化
StorageRouter 連携による primary/secondary 切替を実装。
flush() で tmp→rename 原子的更新を保証。
StatusItem を dataclass 化し to_ui() で ISO 時刻変換。
統合スモークテスト成功
bitflyer:trades および bitflyer:board の両トピックで fetch→status→snapshot 連携確認。
audit.jsonl 出力・status.json 更新・data/collector/.../\*.jsonl 追記すべて OK。

🧩 次の候補タスク
A) 監査プロバイダ（providers.audit）プリセット一元化対応
providers.audit で presets モジュールの LOOKBACKS と is_valid_lookback() を参照。
期間選択値が None または不正の場合、既定（"1h"）へフォールバックする \_resolve_lookback() を追加。
各関数（load_for_ui / export_csv / export_csv_compact / export_csv_compact_localtime）の 引数を lookback=None 化。
スモークテストで None / "3h" 入力時も正常動作確認。

B) Bybit 公開 API アダプタ作成（bybit_public.py）
/v5/market/trades を標準ライブラリで叩く最小実装（依存ゼロ）。
BitflyerPublic と同一インターフェース（executions() 返却型 List[Execution]）。
worker.fetch() へ exchange=="bybit" 分岐を追加。

C) ダッシュボード統合試験
JST 変換済み status 表示確認。
board/trades 両トピックの色分け・更新間隔・監査 CSV 連携チェック。

D) Phase 1B 最終仕上げ
監査タブ（期間プリセット、CSV、長文折り畳み）を UI 統合。
各種 export 機能を UI 側ボタンから呼び出す連携コードを追加。

🔗 参照
実装: features/collector/adapters/bitflyer_public.py
実装: features/collector/core/worker.py
実装: common/audit.py, core/status.py
検証: PowerShell 7.5.3 スモークログ （bitflyer:trades / board OK）

---

## 2025-10-15 フェーズ A 完了（status 安定化）

- 追加: ./btc_trade_system/features/collector/core/status.py（StatusWriter）
- 監査: collector.status.update を soft 出力（common.audit があれば）
- 診断: ./scripts/diag/diag_env.ps1 を新規作成（UI 書込副作用=無し、netstat null 安全）
- 動作: status.json の last_iso/updated_at の更新を確認、Health は読取専用で契約通り
- 既知: ダッシュボードは停止中（8501/8503 リスナ無し）

次回（フェーズ B）:

- B1: leader_lock（単一アクティブ収集のロックと心拍）
- B2: worker 側からのロック利用（多重起動ガードの実効化）
- B3: storage_router スケルトン（primary=NAS/secondary=local ルーティング下地）
- B4: status に leader/storage/sync フィールド拡張（28.2）
- B5: Health 表示の注釈（leader.host / storage.primary / sync.pending）
- B6: diag/sync スケルトン（ops/sync/sync_to_nas.ps1 の雛形）

---

## 2025-10-15 Collector / Health / Audit 統合・整理

- 作業メモ

  - Collector の状態記録 (`status.json`) を拡張し、`leader` と `storage` 情報を統合。Bridge スクリプト (`leader_status_bridge.py` / `storage_status_bridge.py`) を `tools/collector` に設置。
  - `features/collector/core/status.py` の再構成完了。データ構造を統一し、`StatusWriter.flush()` で leader・storage 両方のメタデータを安全書込。
  - `features/dash/tabs/health.py` を正式位置へ移動し、デバッグ専用キャプション（storage/path 等）は `BTC_TS_DEBUG_UI=1` でのみ表示されるよう調整。
  - `apps/dashboard.py` の import 構造をリファクタリング：apps→features の自動フェイルオーバーを導入。`settings_modal`, `health`, `audit` の各参照を整理。
  - `features/dash/tabs/audit.py` の ImportError（`get_audit_rows`）を修正し、動的 import で安定化。

- 完了タスク

  1. Health タブを正式移設 (`apps/boards/dashboard/tabs/health.py` → `features/dash/tabs/health.py`)。
  2. Leader／Storage 情報の status.json 統合・自動更新。
  3. `dashboard.py` の import 経路を apps→features 対応で二重解消。
  4. Audit タブ ImportError 修正・正常動作確認。
  5. UI デバッグ要素の ON/OFF 制御（環境変数）実装。

- 次の候補タスク
  A) `features/dash/tabs/health.py` の age_sec None 表示を明示的にハイフン化 or 非表示。
  B) Audit タブのログ整形と重要イベントの強調（level 別カラーリング）
  C) 残 B シリーズの B6：`ops/sync`（バックアップ・同期機構）雛形設計
  D) Dashboard／Health／Audit の統合テストスクリプト整備 (`tools/test_ui_health_audit.py`)

- 参照:

  - `tools/collector/leader_status_bridge.py`, `tools/collector/storage_status_bridge.py`
  - `features/collector/core/status.py`, `features/dash/tabs/health.py`, `features/dash/tabs/audit.py`
  - 実行ログ: PowerShell 出力 `storage -> status.json updated`, `ok: D:\BtcTS_V1\data\collector\status.json`

---

2025-10-17 パッケージ構造最適化・命名整理

完了タスク:
apps/boards 残骸を完全削除し、features/dash・features/settings に統合。
UI/Service 層の命名を統一：ui_xxx.py → xxx_ui.py、svc_xxx.py → xxx_svc.py。
設定モジュールも同様に ui_settings.py → settings_ui.py、ui_modal.py → modal_ui.py へ変更。
import 構文と #path コメントを全自動置換し、Streamlit 起動・設定モーダル動作ともに確認済み。
features/ パッケージ階層の整理完了。
不要フォルダ (apps/boards, components, core/svc_health.py) の安全除去完了。
Git 復元ポイント機構の完全修復（差分指定のバグ修正含む）。

次の候補タスク:
A) 監査出力（restore_point.create）と Dashboard タグ閲覧連携の設計
B) UI/Service の責務整理ドキュメントを docs/arch に追加。
C) import パス検証と REPO_MAP 自動更新スクリプトの改修。

---
