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

##### タスクとして扱われたが完了したか不明なタスク

UI: 検索・期間プリセット・CSV ダウンロード、長文折りたたみ。
しきい値設定の統一
monitoring.yaml を本番値へ戻し、UI 設定から保存/読込を正式化。
色分けや閾値を動的変更可能に。
カード ⇄ グラフ並びリンク（保存対応）
並び順を config/ui/health.yaml: order へ保存/復元。
各取引所アダプタのループ（stub 実装）を用意し、status.json 定期更新まで実現。
例外処理・リトライ・監査書き込みを組み込み。
providers.audit で audit.tail.jsonl を読み込み、期間・feature・level でフィルタリング。

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

- B1: leader_lock（単一アクティブ収集のロックと心拍）
- B2: worker 側からのロック利用（多重起動ガードの実効化）
- B3: storage_router スケルトン（primary=NAS/secondary=local ルーティング下地）
- B4: status に leader/storage/sync フィールド拡張（28.2）
- B5: Health 表示の注釈（leader.host / storage.primary / sync.pending）
- B6: diag/sync スケルトン（ops/sync/sync_to_nas.ps1 の雛形）

---

##### 以下直近の作業報告

## 2025-10-15 フェーズ A 完了（status 安定化）

- 追加: ./btc_trade_system/features/collector/core/status.py（StatusWriter）
- 監査: collector.status.update を soft 出力（common.audit があれば）
- 診断: ./scripts/diag/diag_env.ps1 を新規作成（UI 書込副作用=無し、netstat null 安全）
- 動作: status.json の last_iso/updated_at の更新を確認、Health は読取専用で契約通り
- 既知: ダッシュボードは停止中（8501/8503 リスナ無し）

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

## 2025-10-18 アダプタ設置・監査安定化

### 完了タスク

- `collector/adapters/api_bf.py` を新設し、bitFlyer 公開 API（/board, /executions）に対応する最小アダプタを実装。
- 監査システム（audit.jsonl 出力・UI 反映・collector 連携）の全体動作を確認。基盤として完成。
- `local/` および ルート直下 `collector/` の残存フォルダを解析し、安全に削除可能と確認。
- `status.json` の正しい出力パス `data/collector/status.json` を確認し、collector 健全稼働を確認。
- ダッシュボード上の監査モード（PROD/DEBUG/DIAG）動作と ENV 優先設定の挙動を確認。

### 次回タスク（優先度順）

- [P0] `collector/adapters/` 配下に bitFlyer 以外（Binance / Bybit / OKX）のアダプタを順次追加。
- [P1] `api_bf.py` の board/trades 取得における rate-limit 時の再試行制御・リトライバックオフを追加。
- [P2] board データの `rows` 精密化を他取引所アダプタでも統一化（count_bids/count_asks を標準化）。
- [P3] 監査 UI の保存ボタンを不要化し、操作即時反映型に改善（要 Streamlit 側再構成）。

### 共有/注意

- **監査基盤は完成済み。** collector・dashboard・audit 出力の三点は同期動作を確認。
- **重要情報：** 現在 collector は正規ディレクトリ `btc_trade_system/features/collector/` を使用中。誤ってルート`collector/`直下を再生成しないよう注意。
- **重要情報：** `BTC_TS_MODE` の環境変数が UI 設定を上書きする（ENV > UI）。調整時は再起動が必要。
- 次回以降、アダプタ群の拡張に入るため `collector/adapters/` 構成を共通化して進行する。

---
