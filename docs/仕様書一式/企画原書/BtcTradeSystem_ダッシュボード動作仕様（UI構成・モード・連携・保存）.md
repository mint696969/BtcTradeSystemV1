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



============================================================================



📘 ダッシュボード／アラート／設定 仕様書（改訂 2025-10-26）
BtcTradeSystem V1 — ダッシュボード／アラート／設定 仕様書（改訂）

最終更新: 2025-10-26 (JST)

0. この改訂の要点（マージ内容）

タブ配色は固定：タブの背景色は選択/非選択とも白を維持。タブ切替は文字色のみで表現。

文字色仕様：

選択タブ: 文字色 オレンジ（既定）。

非選択タブ: 文字色 黒（既定）。

ホバー中のタブ: 文字色 オレンジでハイライト（遷移前の視認向上）。

クリックで遷移すると、旧タブは黒、新タブはオレンジになる。

アラートはヘッダー右の 1 行チップに集約。タブ配色はアラートで変更しない。

色は HEX（#RRGGBB）で設定可能。UI から最小限の入力で変更可能。

縦幅は最小のヘッダー 1 行を維持（タイトル｜アラートチップ｜歯車）。

1. ヘッダー構成（最小 1 行）

左: タイトル BtcTradeSystem V1 ダッシュボード

右: アラートチップ領域（歯車の左隣）→ 歯車（設定入口）

横幅調整:

スクロールバー出現有無で幅が揺れないよう scrollbar-gutter: stable both-edges を採用

右カラムは 〔アラート列｜歯車列〕 の 2 分割。縦方向は 1 行固定

1.1 アラートチップ仕様

表示場所: タイトルと歯車の間の細いスペース（右寄せ）

形態: チップボタン（1 行内で横並び）

種別:

重大 (crit): 赤系チップ「! {件数}件 {HH:MM:SS}」

注意 (warn): 黄系チップ「▲ {件数}件 {HH:MM:SS}」

平常 (normal): 非表示

並び順: 左から crit → warn

×ボタンは設けない（非表示）

オーバーフロー: 同時表示上限 max_inline を超えた分は 「+N」チップで折り畳み、ポップオーバー内に一覧表示

クリック:

該当タブへ遷移（タブ名キーで解決）

遷移後、該当タブの未確認件数を既読化し、チップ件数を更新

折り畳み解除条件は、未確認件数の解消により 1 行に収まると自動的に通常表示へ戻る

再ポップ: 重大 (crit) 未確認が残る限り、タブ遷移時に再表示（見落とし防止）

表示時刻: 最新発生時刻を HH:MM:SS 表示

2. タブ UI 仕様（配色固定／文字色切替）

背景色: 選択/非選択とも白（固定）

文字色:

選択タブ: オレンジ（既定色。設定で変更可）

非選択タブ: 黒（既定色）

ホバー中: オレンジ（視認性向上）

下線: 選択タブのみ下線（on/off は設定 appearance.yaml の underline_active）

並び/有効/初期タブ: tabs.yaml を唯一の正とする（UI で並び替えはしない）

3. 設定ファイル（YAML）
3.1 dash.yaml
schema_rev: 1
language: "ja"
time: { format: "24h", display: "HH:MM:SS" }
# タブ文字色（背景は常に白）
colors:
  tab_text:
    normal: "#000000"   # 非選択
    active: "#FF7F27"   # 選択（既定オレンジ）
    hover:  "#FF7F27"   # ホバー
  # 既存 popup 色は存置（他UIで使用）。
alerts:
  max_inline: 2
  chip:
    warn: { bg: "#FFF2CC", fg: "#000000" }
    crit: { bg: "#FFCCCC", fg: "#FFFFFF" }
3.2 tabs.yaml

例: order: ["main","health","audit"] / enabled / initial（初期は order 先頭）

3.3 appearance.yaml
schema_rev: 1
underline_active: true   # 選択タブの下線
3.4 network.yaml / monitoring.yaml

既定どおり（今回の改訂では変更なし）

4. 設定 UI（ui_settings.py）

セクション: 「基本」「外観」「ネットワーク」「監視/ヘルス」

今回の追加点:

タブ文字色（normal / active / hover）を HEX 入力で編集可

アラートチップ色（warn/crit の bg/fg）を HEX 入力で編集可

それぞれに 「既定に戻す」個別復元ボタンを配置

（任意）小さなプレビューボックスで色の視認テスト

保存: 入力が #RRGGBB（or #RGB） 形式のときのみ反映

5. ダッシュボード（dashboard.py）の要件

ヘッダー右を 〔アラート列｜歯車列〕 に分割

1 行のままアラートチップを描画（+N ポップオーバー対応）

色は dash.yaml の alerts.chip.* を参照

タブ配色は背景白固定、文字色の切替は dash.yaml colors.tab_text.* を参照

既読処理: 各タブの UI から未確認件数/時刻を st.session_state["__alerts"] に集約・更新

6. データ受け渡し（最小プロトコル）

ダッシュボードが読む値（セッションステート）

__alerts = [
  {"level":"crit","tab":"health","count":2,"ts":"12:34:56"},
  {"level":"warn","tab":"audit","count":1,"ts":"12:40:02"},
]
# タブ遷移要求（チップ押下でセット）
__goto_tab = "health"

各タブ側は、既読化時に自タブ分を減算し __alerts を更新

7. 非機能要件

縦幅はヘッダー 1 行を厳守（視線移動と実効表示領域の最大化）

CSS はスコープ付きで注入し、他 UI へ副作用を出さない

設定変更は即時反映（次リランで反映）。頻繁に変更しない前提で UI はシンプルに保つ

8. 今後の拡張（任意）

歯車バッジ: 重大未確認時のみ微小赤ドット表示（視認性アップ／ノイズ最小）

トークン化の拡張: 余白・角丸・下線の太さなども dash.yaml に寄せて一括管理

テーマ注入ヘルパ: ui_theme.py を追加して CSS 変数を 1 箇所で生成・注入（保守性アップ）
