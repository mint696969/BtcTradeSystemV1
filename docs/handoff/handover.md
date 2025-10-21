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

- [P0] `collector/adapters/` 配下に bitFlyer 以外（Binance / Bybit / OKX）のアダプタを順次追加。
- [P1] `api_bf.py` の board/trades 取得における rate-limit 時の再試行制御・リトライバックオフを追加。
- [P2] board データの `rows` 精密化を他取引所アダプタでも統一化（count_bids/count_asks を標準化）。
- [P3] 監査 UI の保存ボタンを不要化し、操作即時反映型に改善（要 Streamlit 側再構成）。

---

##### 以下直近の作業報告

## 日報（2025-10-19）

### 本日の目的

開発監査（Audit）タブの UI を安定化・仕様確定し、将来の開発引継ぎ精度を高める。具体的には：

- モード切替ボタンの正常化と再設計
- スナップショット／handover 生成動作の確認
- 開発監査（BOOST/DEBUG/OFF）運用仕様の最終確定

---

### 実施作業内容

#### 1. モード切替ボタンの再構築

- 複数ボタン（OFF/DEBUG/BOOST）から、**単一の循環ボタン**（OFF→DEBUG→BOOST→OFF）へ仕様変更。
- クリック即反映＋`st.session_state`同期を維持。
- ボタン色や CSS は未適用（後で装飾追加可能な構造を保持）。
- 結果：UI 崩れ解消、モード状態遷移を安定確認。

#### 2. スナップショット／handover 生成の動作確認

- `boost_svc.export_snapshot(force=True)` および `build_handover_text()` の単体テストを実施。
- スナップショット生成時の Streamlit API 例外を確認し、UI 側の呼び出しタイミング問題と判明。
- 一時的に UI を簡素化し、モード切替・監査ログの安定性を優先する設計へ移行。

#### 3. 開発監査仕様の最終確定

- **監査モード 3 種（OFF/DEBUG/BOOST）** の役割を正式定義：
  - **OFF**：監査無効。負荷軽減／通常運用。
  - **DEBUG**：開発時の状態可視化・一般ログ収集。
  - **BOOST**：全出力・プロセス内 DOM プローブ・スナップショット自動生成（開発集中解析向け）。
- **スナップショットは手動トリガー方式**へ統一。
  - UI 上の「📸 スナップショット」ボタンを押下時のみ生成。
  - 出力は UI に直接表示され、「📋 コピー」でチャット貼付可能にする（将来実装予定）。
- **モード切替時の自動スナップショット生成は廃止**。
  - 手動制御で運用効率と障害率のバランスを確保。

#### 4. audit_ui.py の Git リセット

- 一時的な UI 崩壊発生（縦書き化／CSS 破損）。
- `audit_ui.py` のみを**Git 既知安定版へ巻き戻し**。
- 状態確認済み：再描画・監査ログフィルタ・件数表示とも正常。

---

### 開発監査機能の概要と最終形

開発監査は、**開発状況・環境状態・処理挙動をログ化／構造化**する仕組みであり、GPT への開発引継ぎ時に以下の恩恵を与える：

1. **文脈保持**：システム内部状態（モード・動作履歴・設定値）を再現可能。
2. **問題解析支援**：BOOST モードで取得される詳細ログにより、UI・Collector・Service の同期不整合を短時間で再現。
3. **GPT 引継ぎ最適化**：`handover_gpt.txt` と連動し、チャット開始直後に「現状の全開発状態」を即共有できる。

> 結果として、次チャット時のコンテキスト欠落・誤推定を最小化し、引継ぎ負荷を減少させる。

---

### 引継ぎ情報（handover 反映対象）

- **現行モード**：`st.session_state.dev_mode`
- **audit ログファイル**：`D:\BtcTS_V1\logs\dev_audit.jsonl`
- **BOOST スナップショット**：`D:\BtcTS_V1\logs\boost_snapshot.json`
- **handover 出力ファイル**：`D:\BtcTS_V1\logs\handover_gpt.txt`
- **監査構成モジュール**：
  - `features/dash/audit_ui.py`（UI）
  - `features/audit_dev/writer.py`（出力・トリム・flush/fsync）
  - `common/boost_svc.py`（スナップショット／handover 生成）

---

### 次回タスク（開発ロードマップ続き）

1. **BOOST モード限定 DOM プローブ同梱**

   - Collector/Dashboard 間の DOM・描画同期を記録。
   - audit ログへ挿入し、BOOST 時のみ有効化。

2. **スナップショットコピー機能実装**

   - UI 上の 📋 ボタンで内容をクリップボードへ。
   - ChatGPT チャットへ即貼り付け可能な形式で出力。

3. **レイアウト整備（CSS レス最適化）**

   - Streamlit 純正ウィジェット構成に限定し、環境差を排除。
   - 右ペインのタイトル／フィルタエリア比率を微調整。

4. **監査データ可視化拡張**

   - dev_audit.jsonl の件数・サイズ・最終更新時刻を UI 表示。
   - BOOST 時のみ詳細統計（bytes/s, events/s）を付与。

5. **handover 自動化プロセス再設計**
   - 開発監査情報を handover 生成スクリプトへ統合。
   - ChatGPT への引継ぎに必要な最小情報構造を定義化。

---

### 補足

本日までの作業により、Audit タブは安定化し、
「監査・引継ぎ・問題解析」の三要素を統合した基盤が完成しました。

---

【日報 - 2025/10/20】

### 本日の成果

- 開発監査 UI（audit_ui.py）の安定稼働を確認。
- OFF / DEBUG / BOOST 各モードの切替動作およびスナップショット取得を完全に同期。
- スナップショット表示ウインドウを常設化し、OFF 時には固定メッセージを表示するよう改善。
- BOOST/DEBUG それぞれのスナップショット内容の差異を確認（正常動作）。
- コピーボタンの挙動を検証し、次フェーズでのブラウザ Clipboard 対応に向けた課題を洗出し。

### 残課題

- コピーボタンで全文を確実にクリップボードへコピーできるよう修正が必要（pyperclip 依存を使わずに）。
- Streamlit 内部の clipboard API 制御で一部ブラウザ挙動未統一のため検証要。

### 次回タスク（2025/10/21 予定）

1. コピーボタン機能の最終修正（安全な Clipboard API 実装）
2. 開発監査 UI の軽量化・レイアウト整備（ボタン下余白調整・scroll 固定化）
3. audit_dev.writer / boost_svc の監査出力テスト自動化
4. 開発監査ログ(dev_audit.jsonl)のエントリ検証およびサマリ出力整備

---

## 2025-10-22 UI 整備と P0 完了確認

- 作業メモ
  P0 タスク群の実装・動作テストを完了。REPO_MAP 抜粋、Errors only tail 抽出、Config ハッシュ・更新時刻確認の 3 機能を全て正常に動作確認。ワンライナーテストでオールグリーンを達成。UI 側ではスナップショット表示窓の高さ固定が未反映のため、CSS 再調整を次回タスクへ持ち越し。snapshot_ui.py 内 ensure_snapshot_code_css()の min/max height 設定見直しが必要。

- 完了タスク

  - **REPO_MAP 抜粋機能の追加**：boost_snapshot.json から抽出し、各ファイルの#path/#desc を整理表示。最大 200 件（DEBUG は 50 件）までのサマリ出力を実装。
  - **Errors only tail 機能の追加**：dev_audit.jsonl から ERROR/CRITICAL のみ抽出し、直近 N 件（デフォルト 150 件）を整形して UI に表示。
  - **Config ダイジェスト機能の追加**：config/settings.yaml(.yml)を走査し、存在確認・ファイルサイズ・更新時刻・SHA256 ハッシュを取得。欠落時は N/A として扱う安全設計。
  - **audit_ui.py の整理**：render_snapshot_code()呼び出しへ一本化し、ensure_snapshot_code_css()の二重注入を解消。スナップショット表示をコードウィンドウ方式へ統一。
  - **テストスクリプトの整備**：PowerShell 上で REPO_MAP/ERR_ONLY/CFG を単独・一括検証できるワンライナーを追加。すべて TRUE で動作確認済み。

- 次の候補タスク
  A) snapshot_ui.py の CSS を再調整し、空でも 10 行固定かつスクロール動作を保証。
  B) UI テスト後、P3（ディスク容量・ストレージ実体確認）へ移行。
  C) snapshot_ui のコードと CSS 調整を分離し、他コンポーネント影響を最小化する。

- 参照
  PowerShell テストログ（P0_ALL_OK=True）、UI スクリーンショット（監査ログタブ表示）確認済み。

---
