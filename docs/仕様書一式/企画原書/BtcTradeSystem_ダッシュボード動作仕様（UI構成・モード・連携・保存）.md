# BtcTradeSystem\_ダッシュボード動作仕様（UI 構成・モード・連携・保存）

> 版: 2025-10-06 20:10:15 / この文書は `apps/` の実ソースを自動読解した仕様サマリです。コレクター仕様書と対で運用してください。

## 1. 起動・環境設定

- 実行入口（推奨）: `scripts/run.ps1`（Collector と Dashboard の同時起動ランチャ）/ `scripts/dash.ps1`（UI 単体）
- 既定ポート: 8501（Streamlit）
- 参照する環境変数（パス解決の優先度は下記 `paths.py` に準拠）
  - `BTC_TS_DATA_DIR` / `BTS_GENERAL_DATA_DIR` … データディレクトリ
  - `BTC_TS_LOGS_DIR` / `BTS_GENERAL_LOGS_DIR` … ログディレクトリ
  - `BTC_TS_MODE` … ダッシュボードの監査トレース用（`obs.setup(mode=...)`）

### 1.1 パス解決ポリシー（apps/lib/paths.py）

- データ/ログの共通優先順位：
  1. 明示引数（関数引数）
  2. 環境変数 `BTC_TS_*` / `BTS_GENERAL_*`
  3. **リポジトリ直下**の `./data`, `./logs`（`.git` があれば採用）
  4. CWD の `./data`, `./logs`
- `ensure_dir(path)` は存在しない場合に作成して返す。

## 2. UI 構成（タブと右ドロワ／翻訳）

- 起点: `apps/dashboard.py`（タブの生成と配線のみ担当。中身は `boards/dashboard/tabs/` 配下）
- 主要タブ（インポート定義）:
  - `tabs.main` … メインダッシュボード（価格・指標・グラフ）
  - `tabs.health` … Collector の健全性ビュー（Now Health）
  - `tabs.signals` … シグナル履歴（※ファイルの存在により有効化）
- 右ドロワ（歯車）: `settings_panel.py` が存在すれば表示。
- 例外耐性: 各タブ・パネルは `try/except` で保護され、不足時は警告/UI フォールバックを表示。

### 2.1 国際化（i18n）

- `apps/i18n_ja.json` … UI 全体の翻訳辞書。タブ名・ボタン・ラベルをカバー。
- `config/i18n_ja.json` … UI 設定 YAML（`config/ui/*.yaml`）向けの軽量版。**内容重複あり**。
  - 改善提案: 将来的に `apps/i18n_ja.json` に集約し、`apps/lib/i18n.py` 経由で 1 本化。

## 3. 運転モードと反映機構

- モード: `PROD` / `DEBUG` / `DIAG`（UI 上の切替は **設定ドロワ**で操作）
- 永続化: `config/settings.yaml` 内の `runtime.mode` を**単一の真実**として採用。
- UI からの変更は即時反映（`apps/lib/settings.py` 経由で保存、下記 §4 参照）。
- 監査: `obs.setup(mode=os.getenv("BTC_TS_MODE"), component="dashboard")` → `obs.audit("dashboard.start", ...)` などのトレース出力。

## 4. 設定保存とスナップショット

- ランタイム UI 設定は **名前空間ごと**に YAML で保存：
  - 実値保存先: `config/ui/`
  - 既定定義: `config/ui_defaults/`
  - 名前空間: `dash`, `engine`, `risk`, `policy`（`settings_snapshot.py` の `_NAMESPACES`）
- API（apps/lib/settings.py）:
  - `load(feature) / save(feature, data)` … YAML のロード/保存
  - `get(feature, key, fallback)` … 既存 or デフォルトから値を返却
  - `set(feature, key, val)` … 値を更新して即保存
- スナップショット（apps/lib/settings_snapshot.py）:
  - 保存先: `config/ui_snapshots/ops/`（タイムスタンプ付）
  - `_ensure_dirs()` により必要ディレクトリは自動生成。

## 5. データ連携（Collector → Dashboard）

- `apps/lib/paths.get_data_dir()` で `data/` を確定し、UI は以下を参照：
  - **最新系**: `data/latest/*.csv`（`signal-latest.csv`, `ticker-<ex>.csv` 等）
  - **ヘルス**: `data/debug/health/index.json`（`filename / size_kb / age_sec / status`）
- `boards/dashboard/freshness.py` / `providers.py`（存在する場合）で**最新更新時刻**や**健全性**を表示。
- Collector が未起動/停止中でも UI は落ちず、ファイル未検出時は警告・空表示でフォールバック。

## 6. ログと監査

- ダッシュボードログ: `logs/dashboard.out.log` / `logs/dashboard.err.log`（ランチャ経由）
- 監査イベント（obs）: `dashboard.start`, `enter_app("dashboard")` などを記録。
- コマンドライン起動時: `--server.headless=true --server.port=8501 --browser.gatherUsageStats=false` を推奨。

## 7. 既知のエラー耐性・フォールバック設計

- タブモジュールが欠落 → タブ名は出す/非表示にする等の UI 安全化。
- 設定 YAML が破損 → デフォルト（`ui_defaults/`）から再ロード。
- `data/` が未作成 → `paths.ensure_dir()` と UI 側のガードで**自動生成/空表示**。

## 8. 未確定点・次タスク（Dashboard 側）

- [PENDING] `dash_interval` などの **自動更新周期の既定値**（`config/ui_defaults/dash.yaml` を確認して表化）
- [PENDING] `health` 表示の更新間隔（`health.py: self.log_every_sec` などの実値と UI 反映）
- [PENDING] `tabs.signals` の仕様（列定義・CSV ソース）— ファイル有無でタブ表示可否の条件を明文化
- [PENDING] i18n 集約（`config/i18n_ja.json` → `apps/i18n_ja.json` への移行計画）

## 9. データ契約（I/O スキーマ）

### 9.1 data/latest/\*.csv

| ファイル           | 目的              | 主な列                 | 備考                                                        |
| ------------------ | ----------------- | ---------------------- | ----------------------------------------------------------- |
| signal-latest.csv  | 最新シグナル      | ts, score, prob, label | SafeWriter により追記。signal-latest.csv は最終行を常時反映 |
| ticker-<ex>.csv    | 各取引所の Ticker | ts, price, volume      | Collector → Dashboard 表示用                                |
| orderbook-<ex>.csv | 板情報            | ts, bid, ask, spread   | Depth 要約後に保存                                          |
| trades-<ex>.csv    | 約定履歴          | ts, side, price, size  | 各取引所 API 直出力を正規化                                 |

### 9.2 スキーマ共通規約

| 項目           | 内容                                                    |
| -------------- | ------------------------------------------------------- |
| タイムスタンプ | `ts` (epoch_ms, UTC)                                    |
| JSON 列        | ensure_ascii=False, separators=(",", ":")               |
| NULL           | 空セルで表現                                            |
| 互換性         | 列追加＝後方互換、列削除＝非互換（schema_version 更新） |
| 保存形式       | UTF-8 CSV、`newline=""`、QUOTE_MINIMAL                  |

---

## §10. 設定保存/復元・マイグレーション

### 10.1 バージョニング

- 各設定 YAML に `ui_schema_version` を追加することで、構造変更時の互換維持を管理。
- バージョン不一致時は自動マイグレーションまたは再生成。

#### 10.2 デフォルト展開フロー

1. 起動時、`config/ui/<feature>.yaml` が存在しなければ `config/ui_defaults/` からコピー。
2. 差分キーは `apps/lib/settings.py` で自動補完（`get(feature, key, fallback)`）。
3. 保存時は即時反映（overwrite モード）。

#### 10.3 ロールバック手順

- スナップショット保存先: `config/ui_snapshots/ops/`（`timestamp.yaml`）
- 復元: 対象ファイルを `config/ui/` に上書き → Dashboard 再起動。
- CLI からも可: `tools/test_settings_snapshot.py` により検証実行可能。

### 11. 国際化（i18n）運用ルール

#### 11.1 ファイル構成

| 種類       | ファイル            | 用途                               |
| ---------- | ------------------- | ---------------------------------- |
| メイン翻訳 | apps/i18n_ja.json   | タブ・ボタン・ラベル等すべての UI  |
| 軽量翻訳   | config/i18n_ja.json | 設定 UI でのラベル補助（重複あり） |

#### 11.2 運用指針

- apps/i18n_ja.json に一本化予定。
- 欠損キーは英語原文をそのまま表示（fallback）し、コンソール warn を出力。
- 翻訳キー命名規約: `scope.section.label` 形式（例: `tabs.health.title`）。
- 翻訳追加時は ja/en 両方を同期管理。
- 起動時に欠損キーを検出 → `logs/dashboard.err.log` に出力。

#### 11.3 将来計画

- `apps/lib/i18n.py` に統合ローダを追加し、  
  `config` 側ファイルは廃止方向（deprecated notice 予定）。

---

### 付録 A：ファイル/ディレクトリ早見表

- `apps/dashboard.py` … タブ生成・配線・監査イベント
- `apps/boards/dashboard/tabs/{main, health, signals}.py` … 各タブ本体（存在すれば）
- `apps/boards/dashboard/{hub.py, providers.py, freshness.py, settings_panel.py, plot.py}` … UI 補助
- `apps/lib/{paths.py, settings.py, settings_snapshot.py}` … パス解決、UI 設定、スナップショット
- `config/{i18n_ja.json, settings.yaml}` + `config/ui{,_defaults}/*.yaml` … 表示文言/モード/既定値

### 付録 B：運用 Tips

- UI だけ開きたい場合: `scripts/dash.ps1` → ブラウザ `http://localhost:8501`
- Collector と揃えて開く: `scripts/run.ps1`（UI 終了で Collector 自動停止まで一括管理）
- 不整合時: `ui_defaults/*.yaml` を **実値側 `ui/*.yaml` へ再展開** → 再読み込み
