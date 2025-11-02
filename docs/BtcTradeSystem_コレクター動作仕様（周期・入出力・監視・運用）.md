# BtcTradeSystem コレクター動作仕様（周期・入出力・監視・運用）

> 版: 2025-10-06 16:08:05 / 対象: **BtcTradeSystem** / 範囲: `btc_trade_system/apps.collector` を起点とするデータ収集系（Collector）

この文書は、チャットをまたいでも**Collector の動作を正しく引き継ぐ**ための仕様・手順・監視ポイントをまとめたものです。
設計上の詳細や運転モードの具体コマンドは、別紙「BtcTradeSystem\_運転モードと監査（使い方・仕様・調べ方）」を参照。

---

## 0. 位置づけと構成要素（概要）

- **起動口**: `python -m btc_trade_system.apps.collector`（PowerShell: `btc_trade_system/ops/collector/start_collector.ps1` から起動）
- **主要モジュール**（リポ内）:
  - `core/collector/main.py` … 収集のエントリ/ランナー
  - `core/collector/bootstrap.py` … 依存初期化・前提確認
  - `core/collector/preflight.py` … 事前ヘルスチェック（API 通通性・設定検証）
  - `core/collector/health.py` … ランタイム健全性判定（status.json ベース）
  - `core/collector/okx_trades_worker.py` … 取引取得のワーカー例
  - `core/ingest/*` … 取得データの正規化（adapters/normalizer）
  - `core/feature_engine.py` … 特徴量生成の起点
  - `core/signal_builder.py` … シグナル組み立て
  - `core/storage/writer.py` + `core/writer_wrapper.py` … 永続化（SafeWriter）
  - `core/bus/pubsub.py` … 内部 Pub/Sub
- **運用スクリプト**（PowerShell）:
  - `ops/collector/start_collector.ps1`（起動） / `ops/collector/stop_collector.ps1`（停止）
  - `ops/collector/ensure_running.ps1`（多重起動防止・自動復帰）
  - `ops/collector/health.ps1`（Now Health）
  - `ops/collector/repair_status.ps1` / `repair_status_weekly.ps1`（status.json の修復・整形）
  - `ops/collector/logrotate.ps1`（ログローテ）
- **設定**: `config/settings.yaml`（UI の設定パネルから `runtime.mode` が永続化）
- **ランタイム出力**: `data/` と `logs/`（リポ直下。環境変数 `BTC_TS_DATA_DIR`/`BTC_TS_LOGS_DIR` で上書き可）

---

## 1. 起動シーケンス（観測ログ準拠）

```
[collector] REPAIR: normalize status.json (DropDays=7)
[collector] DATA=...\data LOGS=...\logs
[collector] PY=...\.venv\Scripts\python.exe ROOT=...\BtcTradeSystem
[collector] LAUNCH: ... -m btc_trade_system.apps.collector
[collector] MODE=FOREGROUND
[collector] OUT=...\logs\collector_latest.out.log
[collector] ERR=...\logs\collector_latest.err.log
[DBG] CONTRACT obj=SafeWriter ...
[DBG] subscribed: feature_engine.ingest (...)
[DBG] subscribed: sig_builder.ingest (...)
[OK] preflight: bitflyer.ticker.preflight
[OK] preflight: binance.ticker.preflight
[OK] preflight: bybit.ticker.preflight
[OK] preflight: okx.ticker.preflight
[START] collector with 12 threads: bitflyer.ticker, bitflyer.orderbook, bitflyer.trades, binance.ticker, binance.orderbook, binance.trades, bybit.ticker, bybit.orderbook, bybit.trades, okx.ticker, okx.orderbook, okx.trades
```

### 1.1 事前処理

- `status.json` の整形/再生成（欠損時は `REPAIR` ログ）
- 設定読込: `config/settings.yaml`（`runtime.mode` 等）
- ログ/データパスの解決: `BTC_TS_*` 環境変数 → `./data`,`./logs`

### 1.2 プロセス起動

- `start_collector.ps1` が Python を **FOREGROUND** で起動し、  
  `logs\collector_latest.out.log / err.log` に標準出力/エラーをスイッチ。

### 1.3 依存初期化

- `SafeWriter` の契約検証（`write_row` などの実装チェック）
- 内部 Pub/Sub で **feature_engine.ingest** / **sig_builder.ingest** に購読登録

### 1.4 Preflight

- 主要取引所の `ticker.preflight` が OK であることを確認（接続・鍵・レート制御など）。

---

## 2. 周期動作（メインループ）

### 2.1 スレッド構成

- **12 スレッド**（観測時）:
  - bitflyer: `ticker`, `orderbook`, `trades`
  - binance: `ticker`, `orderbook`, `trades`
  - bybit: `ticker`, `orderbook`, `trades`
  - okx: `ticker`, `orderbook`, `trades`

### 2.2 データフロー

1. **取得**（Fetchers）: 取引所 API から `ticker/orderbook/trades` を取得
2. **正規化**（Ingest/Normalizer）: 内部共通スキーマに変換
3. **配信**（Pub/Sub）: `feature_engine.ingest` / `sig_builder.ingest` トピックへ Publish
4. **特徴量**（FeatureEngine）: 必要なウィンドウ/集約を計算
5. **シグナル**（SignalBuilder）: ルール/モデルに応じた信号を構築
6. **永続化**（SafeWriter）: ストレージへ書き込み（エラーは隔離/リトライ）

> ログ例: `okx.get_trades raw_len=100 type=dict` → `signal-writer.tick`（書き込み周期の合図）

### 2.3 周期・タイミング

- 具体的インターバルは **実装依存**（`constants.py` 等）。一般には:
  - `ticker`: 高頻度（~数百 ms〜数秒）
  - `orderbook`: 中頻度（~秒）
  - `trades`: 高頻度（~秒）
- [VERIFY] 実数値は `core/collector/constants.py` の値を正とし、必要ならキャンバスに追補。

### 2.4 レート制御/バックオフ

- [ASSUMPTION] リモート 429 やネットワーク例外時は指数バックオフ（実装要確認）。
- [VERIFY] `ingest/adapters_fallback.py` などにフォールバック経路がある場合は、切替条件を追記。

---

## 3. 入出力（I/O）

### 3.1 入力

- **取引所 API**: bitflyer/binance/bybit/okx（公開エンドポイント中心、鍵は設定/環境変数で）
- **設定**: `config/settings.yaml`（UI から編集可）

### 3.2 出力

- **ログ**: `logs/collector_*.log`, `collector_latest.out.log`, `collector_latest.err.log`
- **状態**: `data/collector/status.json`（Now Health/最新時刻・件数/ワーカー生存情報）
- **データ**: SafeWriter 経由で保存（形式は実装に依存。例: JSONL/Parquet/CSV 等）
  - [VERIFY] `core/storage/writer.py` の `write_row` 実装（パス/拡張子/ローテーション）

---

## 4. 監視と運用

### 4.1 ヘルスチェック

- `ops/collector/health.ps1` … `status.json` とログ時刻差で Now Health を表示
- `ops/collector/ensure_running.ps1` … 多重起動防止・死活監視・再起動
- `ops/collector/logrotate.ps1` … ログ肥大の抑制

### 4.2 運転モード（概要）

- **PROD**: 監査最小／通常運用
- **DEBUG**: 詳細ログで挙動追跡（UI 確認時）
- **DIAG**: 監査詳細を短時間収集 → 原因特定後に速やかに **PROD** へ復帰
- 切替は **Dashboard 設定パネル**。内容は `config/settings.yaml: runtime.mode` に反映

> 詳細コマンド・チェック観点は別紙「運転モードと監査」を参照。

### 4.3 典型運用コマンド

```powershell
# 起動（統一）
.\scripts
un.ps1

# Collector 単独
.tc_trade_system\ops\collector\start_collector.ps1

# ヘルス
.tc_trade_system\ops\collector\health.ps1

# 停止
.\scripts\coll-stop.ps1  # or ops\collector\stop_collector.ps1
```

---

## 5. 障害と復旧

| 症状                   | 代表ログ/現象    | 切り分け                     | 対応                                             |
| ---------------------- | ---------------- | ---------------------------- | ------------------------------------------------ |
| 画面にデータが出ない   | `0 items` が連続 | API レート/ネットワーク/キー | `preflight` 再確認、`DEBUG/DIAG`でログ採取       |
| Collector がすぐ落ちる | 例外スタック     | 設定ファイル破損/依存欠落    | `repair_status.ps1`、依存を再インストール        |
| ログが巨大化           | ファイル > 数 GB | ローテ未設定                 | `logrotate.ps1` を定期実行                       |
| status.json がおかしい | JSON 不整合      | 異常終了・手動編集           | `repair_status.ps1` / `repair_status_weekly.ps1` |

---

## 6. 変更時の注意と引継ぎ

- 取得対象の追加/削除・周期変更は **Repo Map に差分反映**（スレッド一覧を更新）。
- 永続化形式やパスを変更する場合は、**UI/下流（Feature/Signal）への影響**を事前評価。
- 重要決定は `docs/adr/ADR-YYYYMMDD-*.md` に記録。

---

## 7. 付録

### 7.1 簡易シーケンス（ASCII）

```
Start-Collector.ps1
    -> python -m apps.collector
        -> preflight()
        -> spawn threads [exchange.xN]
        -> fetch -> normalize -> publish(bus)
        -> feature_engine.ingest -> compute
        -> signal_builder.ingest -> build
        -> writer.write_row(...)  -> data/*
        -> update status.json     -> data/collector/status.json
```

### 7.2 既知ログ断片（観測）

```
[OK] preflight: bitflyer.ticker.preflight
...
[START] collector with 12 threads: bitflyer.ticker, ..., okx.trades
[DBG] okx.get_trades raw_len=100 type=dict
[OK] signal-writer.tick
[EXIT collector] shutting down...
```

---

## 8. 確定・追補（自動抽出の反映と残タスク）

**SafeWriter 出力形式/パス規則（確定）**

- 形式: UTF-8 CSV（`newline=""`、`csv.QUOTE_MINIMAL`）
- dict/list は `json.dumps(..., ensure_ascii=False, separators=(",", ":"))` で **1 セル JSON**
- ベース: `data/`（`utils.paths_env.get_signals_dir()` 起点）
- 主要パス:
  - `data/raw/{feed}-{ex}-{sym}.csv`
  - `data/signals/signal-{pair}-{YYYYMMDD}.csv`（原子的置換）
  - `data/latest/{feed}-{ex}.csv`、`data/latest/signal-latest.csv`
- ヘルス: `data/debug/health/index.json` に `filename / size_kb / age_sec / status` を記録

- **周期・待機系（コードから確定できたもの）**

  - `core/collector/constants.py`: `POLL_SEC = 2.0`
  - `core/collector/bootstrap.py`: 監視ループ
    - `while not _STOP_EVENT.wait(10.0)`
    - `while not _STOP_EVENT.wait(1.0)`
    - `time.sleep(interval)`（個別 interval を使用）
  - `core/collector/okx_trades_worker.py`: `time.sleep(max(0.5, interval))`（下限 0.5 秒）
  - `core/collector/health.py`: `time.sleep(self.log_every_sec)`（値は実装/設定依存）

- **health.ps1 の参照ポイント（確定）**

  - `READY` / `STOP` フラグの `LastWriteTime`
  - `logs/collector_latest.out.log` / `logs/collector_latest.err.log` の Tail と時刻

- **実インターバル値の表**

  - 既確認: `POLL_SEC=2.0`、`okx_trades_worker: max(0.5, interval)`、`_STOP_EVENT.wait(10.0/1.0)`、`health.log_every_sec`
  - 追加の `*_INTERVAL/*_TIMEOUT/*_RETRY/*_BACKOFF` が他ファイルにあれば横断抽出して追補

- **バックオフ／リトライ詳細**

  - 現状ヒット: `requests.Session.get(..., timeout=_DEF_TO)` の **タイムアウト指定**のみ
  - `429/Retry/Backoff` 該当コードは未検出（別ファイル実装の可能性）
  - 次回：`core/ingest/*.py` / `core/collector/*.py` を横断して `429|retry|backoff|max_retry|time.sleep` を再スキャンし、  
    再試行回数・待機（固定/指数）・最大待機を表化

- **`status.json` スキーマ**
  - 現状：`data/collector/status.json` は **未生成/Null**（Collector 未起動直後など）
  - 生成手順：Collector を一度起動 → 停止後に下記でスキーマ抽出
    ```powershell
    $st = ".\data\collector\status.json"
    if (Test-Path $st) {
      $j = Get-Content $st -Raw -Enc UTF8 | ConvertFrom-Json
      function Show-Json($o,$p=""){
        if ($null -eq $o){ "$p : Null"; return }
        $t = $o.GetType().Name
        if ($t -in 'Hashtable','OrderedDictionary'){ foreach($k in $o.Keys){ Show-Json $o[$k] ($p + ($(if($p){"."}else{""}) + [string]$k)) }; return }
        if ($t -eq 'Object[]'){ for($i=0;$i -lt $o.Count;$i++){ Show-Json $o[$i] ($p + "["+$i+"]") }; return }
        "{0} : {1}" -f $p,$t
      }
      Show-Json $j
    } else { "status.json が見つかりません: $st" }
    ```
  - 出力（`path : Type`）を仕様に表化（必須キー/単位を付与）

###　監視と異常時の挙動（追加機能）

#### API レート制御（GOV / Adaptive Scheduler）

- 目的: 規制（429/403）回避と安定運用。**平時は短周期、規制兆候で自動延伸**。
- 構成:
  - `core/collector/adaptive_scheduler.py`
    - **GOV**: 動的スリープ決定（base/jitter/decay/max_interval）
    - **STATS**: 呼び出し実績（60 秒/5 分）と障害件数（Err/429/403）
    - **9 割キャップ**: 取引所ごとの「情報系 API の上限（MAX/min）」の **90%** を目標に運用。超過しそうなら `sleep ≥ 60 / target_rpm` を強制
    - **throttle フラグ**: 目標超過中は `throttle:true` をスナップショットに出力
  - `core/exchanges/profiles/*.py`
    - 取引所別の既定値を宣言し、一括適用（`apply_profiles()`）
    - 例: bitflyer=100/min → 運用 90/min、binance=300/min → 270/min（暫定）
- 実装ポイント:
  - すべての外部呼び出しは **RateLimitedAdapter** を経由
  - 成否を `note_call("OK"|"ERR"|429|403)` として STATS に記録
  - **rate limit 発生**: `GOV.report_rate_limit(ex)` でバックオフ寄りへ
  - **復帰**: `GOV.report_success(ex)` で回復方向へ

#### コレクター内部テレメトリ出力

- `data/collector/rate_stats.json`（5 秒間隔で更新）
  - 例
    ```json
    {
      "ts": 173...,
      "stats": {
        "bitflyer": {
          "rpm_60s": 12.0,
          "rpm_300s": 10.4,
          "err_60s": 0.0,
          "target_rpm": 90.0,
          "throttle": false
        },
        "binance": { ... }
      }
    }
    ```
  - 用途: ダッシュボード健全性カードの API 行（通常=黒、制御中=赤）に反映
- `data/collector/events.jsonl`（既存）
  - 健全性レベルの遷移（OK/WARN/CRIT）を JSON Lines で追記

#### 健全性カード：API 実測表示

- 情報源: `data/collector/rate_stats.json`
- 表示仕様（1 行）:
  - `API:60s=<直近60秒の回数> / 5分=<直近5分の1分平均>/分 / Err60=<直近60秒のエラー数> [OK|WARN|CRIT]`
- 配色:
  - 通常（throttle = false）: 黒文字
  - 制御中（throttle = true）: **濃赤**（視認強調）
- 目的: “今どれくらい叩いているか／抑制が走っているか”を一目で把握

#### 背景スレッド（エクスポータ）

- `collector.rate_stats`（常時）
  - 5 秒おきに `snapshot_all()` をダンプして `data/collector/rate_stats.json` を更新
- フォールバック `collector.probe`（ワーカースレッド 0 本時）
  - 健全性を最低限監視し、`events.jsonl` と `rate_stats.json` を継続更新

#### レート制御の既定値（profiles）

- ファイル: `core/exchanges/profiles/*.py`
  - 取引所別に `PROFILE["rate"]` と `PROFILE["max_info_rpm"]` を宣言
  - `apply_profiles(adapters, enabled)` で起動時に一括適用
- 既定（暫定・要調整）
  - bitflyer: MAX 100/min → 運用 90/min
  - binance: MAX 300/min → 運用 270/min（※将来 weight 対応に拡張）
  - bybit: MAX 240/min → 運用 216/min
  - okx: MAX 300/min → 運用 270/min
- チューニング:
  - 実測の `rpm_60s` と規制発生状況を見て `base/jitter/decay/max_interval` を調整

#### ダッシュボードのタブ閉鎖で一括停止（開発運用）

- 目的: 多重起動（PS ウィンドウ残存/Collector 孤児）を**物理的に排除**
- 仕組み
  1. `apps/lib/heartbeat.py`：ダッシュボードのルートで `beat("dashboard")`
     - `data/runtime/heartbeats/dashboard-<sid>.hb` を 30s 間隔で更新
  2. `scripts/guardian.ps1`: 直近 `IdleSeconds（推奨90）` に心拍更新が無ければ、
     `Stop-Process -Id <dashPS, collectorPS> -Force` を実行
  3. `scripts/dev.ps1`: ダッシュボードとコレクターを別 PS 窓で起動し、PID を guardian に渡す
- 運用:
  - **`dev.ps1` から起動**する
  - ダッシュボードタブを閉じる → **90 秒以内に** PS2 窓と Collector が自動終了

#### 参照ファイル

- `core/collector/adaptive_scheduler.py`（GOV/STATS/RateLimitedAdapter）
- `core/collector/bootstrap.py`（profiles 適用、events.jsonl、rate_stats exporter）
- `core/exchanges/profiles/`（bitflyer/binance/bybit/okx）
- `apps/boards/dashboard/tabs/health.py`（API 行の表示/配色）
- `apps/lib/heartbeat.py` / `scripts/guardian.ps1` / `scripts/dev.ps1`（任意運用）

