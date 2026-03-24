# path: ./docs/仕様書一式/監査（Audit）＋派生サマリ 正式仕様書.md
# desc: Phase2：Collector/Watchdog/Health の監査ログ（台帳）と派生サマリ（GPT判定用）を定義し、運用モード（NORMAL/DEBUG/BOOST）を明確化する。

---

## 0. 背景 / 目的

Phase1 で「bitFlyer（現物）を対象に、Collector が 24h 安定稼働し、watchdog が自動復旧できる」状態を証明した。  
Phase2 では、それを **長期常時運用（24h×365）** に耐える形で、

- 記録物の信頼性（あとから“何が起きたか”追える）
- GPTが品質判断できる可観測性（速く・正確に判断できる）
- 運用/開発のログ粒度を整理（NORMAL/DEBUG/BOOST）

を整備する。

> 改ざん耐性を“過剰に堅牢”にはしないが、  
> 「何かの拍子に壊れて成果物が信用できない」状態は避ける。  
> そのため **監査（台帳）＋派生サマリ** を必須化する。

---

## 1. 用語

- **監査ログ（Audit / 台帳）**：append-only の JSONL。起きたイベントを時系列で残す唯一の一次情報。
- **派生サマリ（Derived Summary）**：監査ログ・状態ファイル・ファイル増分等から作る集計結果。GPTが短時間で判断できる形。
- **運用モード（Mode）**：ログ粒度と追加観測（重い情報）を切り替える概念。`NORMAL / DEBUG / BOOST`。
- **証跡パック（Evidence Pack）**：調査/問い合わせに必要な断片を zip で固めたもの。

---

## 2. Phase2 ゴール（定義）

### 2.1 ゴール
1) **NORMAL（常時運用）モードが存在**し、常時運用で必要十分な監査ログと派生サマリが残る。  
2) **DEBUG / BOOST が明確に差別化**され、目的と出力が異なる。  
3) GPT が “正常/異常/劣化” を**派生サマリ中心に判断**できる（台帳だけでも追えるが、通常判断はサマリ優先）。  
4) 監査・サマリが **ログ肥大で運用を壊さない**（ローテーション/保持/上限/退避の設計がある）。

### 2.2 非ゴール
- 暗号署名やWORMなどの強い改ざん防止（将来の必要が出たら別フェーズ）。
- UI 完成（サマリの閲覧UIは任意。まずはファイルで成立させる）。

---

## 3. モード仕様（NORMAL / DEBUG / BOOST）

### 3.1 モード一覧
| Mode | 想定 | 監査（台帳） | 派生サマリ | 重い観測（raw断片/レイテンシ詳細等） |
|---|---|---|---|---|
| **NORMAL** | 常時運用（24/365） | 重要イベントのみ（低容量） | **必須**（日次/時間） | 原則OFF |
| **DEBUG** | 原因追跡 | NORMAL + 原因追跡に必要なイベント | 必須（粒度UP可） | 一部ON（軽量） |
| **BOOST** | 短期深掘り（数分〜数時間） | DEBUG + 高頻度/詳細 | 必須（最も詳細） | ON（重い） |

### 3.2 モードの指定
- 環境変数：`BTC_TS_MODE`
  - 許容値：`NORMAL | DEBUG | BOOST`
  - 未指定時：`NORMAL`
- 監査ログの各行は `mode` を必ず持つ（実行時のモードを固定で書く）。

> 旧：DEBUG/BOOST が実質同義になっていた問題を解消する。

---

## 4. 監査ログ（audit.jsonl）仕様

### 4.1 ファイル
- パス：`${BTC_TS_LOGS_DIR}/audit.jsonl`
- 形式：JSON Lines（1行1JSON / UTF-8 / 追記のみ）
- ローテーション：Phase2 で設計・実装対象（後述）

### 4.2 1行の共通スキーマ（必須キー）
- `ts` : ISO8601 UTC（例：`2026-02-28T20:49:45.924Z`）
- `mode` : `NORMAL|DEBUG|BOOST`
- `event` : イベント名（ドット区切り推奨）
- `feature` : `collector|watchdog|health|test|...`
- `level` : `DEBUG|INFO|WARN|ERROR`
- `payload` : dict（イベント固有）
- `meta` : dict（pid/host/trace_id等）

推奨キー：
- `trace_id`（相関ID。処理単位/起動単位）
- `site` / `actor`（将来の運用拡張用。いまは空でも良い）

### 4.3 イベント最小セット（NORMAL必須）
**Collector**
- `collector.start` / `collector.stop`
- `collector.status.write`（間引き：例 30〜60秒おき）
- `collector.rate_state.write`（間引き：例 60秒おき）
- `collector.http.request`（原則OFF、DEBUG以上でON）
- `collector.http.429`（必須：発生時）
- `collector.retry`（WARN以上のみ）
- `collector.exception`（ERROR）

**Watchdog**
- `watchdog.start` / `watchdog.exit`
- `watchdog.lock.acquired` / `watchdog.lock.busy`
- `watchdog.kill` / `watchdog.restart`
- `watchdog.stop.*`（disk/too_many_fails/no_data 等）

**Health**
- `health.eval`（間引き：例 60秒おき）
- `health.warn` / `health.crit`（閾値超過時）

### 4.4 429 の扱い（仕様）
- 429 は「取引所からのレート制限」を示す代表値だが、将来的に別要因（CDN/中継/代理等）で起こり得る。
- よって **“429が1回でも出たら即NG”** ではなく、派生サマリでは下記を区別できること：
  - `source=exchange`（取引所応答としての429）
  - `source=network|proxy|unknown`（HTTP層の失敗としての429）
- Collector は可能なら `payload` に `exchange`, `topic`, `endpoint`, `status_code`, `retry_after_sec`, `source` を入れる。

---

## 5. 派生サマリ（Derived Summary）仕様

### 5.1 目的
- GPT が監査台帳を全走査せずとも、**短時間で状態判断**できるようにする。
- “長期運用の正常性” を **定量指標**で把握できるようにする。

### 5.2 出力先（推奨）
- `${BTC_TS_LOGS_DIR}/derived/`
  - `hourly_YYYYMMDD_HH.json`（時間サマリ）
  - `daily_YYYYMMDD.json`（日次サマリ）
  - `latest_hourly.json` / `latest_daily.json`（最新へのシンボリック代替。Windowsならコピー更新）

### 5.3 サマリの最小スキーマ（例）
#### hourly_*.json（1時間）
- `ts_start`, `ts_end`（UTC）
- `mode`（この期間の主モード。通常は起動時のモード固定）
- `collector`:
  - `proc_restart_count`
  - `topics`: `{ "<exchange>/<topic>": { ok_count, err_count, max_age_sec, max_retries, last_ok_ts } }`
  - `http`: `{ total, status_2xx, status_4xx, status_5xx, status_429, retry_after_max_sec }`
- `watchdog`:
  - `restart_count`
  - `stop_events`: `{ reason: count }`
  - `hang_detected_count`
- `files`:
  - `data_bytes_delta`: `{ "<exchange>/<topic>": bytes }`
  - `audit_bytes_delta`
- `health`:
  - `warn_count`, `crit_count`
- `notes`（任意）

#### daily_*.json（1日）
- hourly を日次集計したもの（合計・最大・上位Nなど）

### 5.4 生成方式（実装指針）
- 監査ログを逐次処理する **カーソル方式**（例：`derived/cursor.json` に offset/mtime/sha を記録）
- 1時間ごとに **追記分だけ集計**（全量再集計を避ける）
- “Collectorの状態” は `status.json` / `rate_state.json` のスナップも併用してよい

---

## 6. ログ/サマリのローテーション（運用必須）

### 6.1 方針
- 長期運用でディスクを枯らさない。  
- 監査ログは「捨てる」のではなく、**圧縮して退避**が基本（必要に応じて保持期間を設計）。

### 6.2 最小仕様（提案）
- `audit.jsonl`
  - 日次で `audit_YYYYMMDD.jsonl` に切り替え（またはサイズ閾値：例 256MB）
  - 退避時に gzip（任意）
  - 保持：例 30日（要件に合わせ調整）
- `supervisor_collector.jsonl` / `.log`
  - 日次orサイズで退避
- `derived/`
  - 日次は保持長め（例 180日）
  - hourly は短め（例 14日）＋ daily に集約済みなら削除可

---

## 7. 証跡パック（Evidence Pack）

### 7.1 目的
- 障害解析・サポート問い合わせ・監査確認を最短化する。
- 「これだけあれば第三者（別GPT含む）が状況再現/判断できる」を満たす。

### 7.2 最小構成（例）
- `derived/latest_daily.json`
- `derived/latest_hourly.json`
- `audit.jsonl`（直近N行 or 直近1時間分）
- `supervisor_collector.jsonl`（直近N行）
- `status.json` / `rate_state.json`
- `config_snapshot/`（collector.yaml / watchdog.yaml / endpoints_def.yaml 等のSHAとコピー）
- `README.txt`（会話ID/時刻/環境メモ）

---

## 8. 将来拡張（金融商品の多様化への布石）

Collector は現状 bitFlyer BTC だが、最終的に FX / 株 / その他の金融商品の情報も推論対象にする。  
このため監査・派生サマリは、**商品種別やシンボル拡張に耐えるキー設計**を採る。

推奨キー例：
- `market_type`（spot/fx/stocks/…）
- `symbol`（BTC_JPY 等）
- `instrument_id`（取引所の正式ID）
- `exchange`（bitflyer 等）
- `topic`（orderbook/trades/ticker/…）

---

## 9. 受け入れ条件（Phase2 Done）

- [ ] `BTC_TS_MODE` が `NORMAL/DEBUG/BOOST` で差が出る（出力イベント量・内容が明確に異なる）
- [ ] NORMAL で 24/365 運用してもログが過剰に肥大しない（ローテ設計があり、実装が入る）
- [ ] `derived/latest_daily.json` が生成され、主要な判断指標（429/再起動/最大age/データ増分）が入る
- [ ] Evidence Pack がワンコマンドで作れる
- [ ] GPT が「派生サマリ中心」で品質判断できる（判断テンプレ/チェックリストが揃う）

---

## 10. 次回タスク（Phase2の実装順）

1) **モード分離**：DEBUG/BOOST の差別化、NORMAL のデフォルト化  
2) **派生サマリ生成**：hourly → daily、カーソル方式  
3) **ローテーション**：audit/supervisor/derived の保持設計 + 実装  
4) **Evidence Pack**：調査用zip（Phase1 runner の発想を常時運用へ拡張）  
5) **テスト**：モード別イベント差分、サマリ生成の整合、ローテ後も運用継続

---

## 11. 実装状況（2026-03-05）

### 11.1 現在の運用ルート（正本）
- 実運用の正本は `E:\btc_ts\` 配下（logs/data/config/secrets）。
- リポジトリ配下（例：`btcts_next/logs`）はフォールバック/テンプレ用途。
- runner は既存の `BTC_TS_*` 環境変数を尊重し、未設定時のみ repo フォールバックを採用する。

### 11.2 出力構造（実装）
- `${BTC_TS_LOGS_DIR}/derived/`
  - `hourly_YYYYMMDD_HH.json`
  - `daily_YYYYMMDD.json`
  - `latest_hourly.json` / `latest_daily.json`
  - `state.json`
- `${BTC_TS_LOGS_DIR}/quality/`（GPT判定を高速化する最小サマリ）
  - `coverage_YYYYMMDD_HH.json`（hourlyから生成）
  - `gaps_YYYYMMDD_HH.jsonl`（hourly topics の max_age_sec から生成）
  - `anomaly_YYYYMMDD.json`（dailyから生成）

### 11.3 Evidence Pack（実装）
- Evidence Pack は `derived/*` に加えて `quality/*`（最新）を同梱する。

### 11.4 ローテーション（実装）
- runner ログ（derived_runner.*）に加えて、以下もサイズ閾値で `_archive/` へ退避する：
  - `audit.jsonl`
  - `supervisor_collector.jsonl`
  - `supervisor_collector.log`
- 方式：サイズ閾値超過 → `${BTC_TS_LOGS_DIR}/_archive/<timestamp>/` へ Move（保持本数で掃除）

> 注：本仕様の「日次切替/gzip」は提案であり、現実装は「サイズ閾値＋保持本数」の簡易方式。運用要件に応じて日次+圧縮へ拡張可能。

### 11.5 受け入れ条件（Phase2 Done）チェック（現状）
- [x] NORMAL で 24/365 運用してもログが過剰に肥大しない（ローテ設計が入り、運用ルートも正本へ統一）
- [x] `derived/latest_daily.json` が生成され、主要指標が入る
- [x] Evidence Pack がワンコマンドで作れる
- [x] GPT が「派生サマリ中心」で品質判断できる（derived + quality の入口が揃った）
- [ ] `BTC_TS_MODE` が `NORMAL/DEBUG/BOOST` で差が出る（差分の受け入れ条件は次フェーズで明確化）

## 11.6 追記（2026-03-19 / Collector hot運用・smoke常駐の運用意味）

### hot tier の正本
Collector vNext の hot 運用では、以下を正本とする。

- data: `D:\btc_ts_hot\data`
- logs: `D:\btc_ts_hot\logs`
- state: `D:\btc_ts_hot\state`

`tools/run_collector_vnext.ps1` および `tools/run_collector_vnext_daemon.ps1` では、`BTCTS_*` と `BTC_TS_*` を橋渡しし、Collector本体・core audit・Operator UI が同じ hot root を参照することを前提とする。

### smoke常駐の運転モデル
現行の daemon 導線は「常時 1 プロセスで 1 本の websocket を維持し続ける」モデルではなく、**15秒間隔の smoke cycle を繰り返すモデル** である。

各 cycle では以下を実行する。

1. bootstrap / rest board / rest trades
2. websocket trade smoke
3. websocket board smoke
4. status / health / checkpoint / audit の更新

このため、board websocket では cycle ごとに接続が張り直され、監査ログ上は次の流れが繰り返し出力されやすい。

- `origin.stream_started`
- `origin.stream_gap_detected`
- `origin.stream_resync_started`
- `origin.stream_resync_completed`

現時点ではこれは異常ではなく、**現行 smoke 常駐モデルを反映した正常挙動** として扱う。

### `last_sequence_id` の定義
`last_sequence_id` は Collector 全体のグローバル通番ではない。

`run_smoke()` は cycle ごとに `SequenceManager.start(1)` で開始するため、`last_sequence_id` は **smoke 1 サイクル内で採番された最終 sequence** を示す。

したがって cycle 間で値が上下して見えても異常とは限らない。UI 上では誤解防止のため `Cycle Last Sequence ID` と表記する。

---

## 12. 追記（2026-03-06）
Phase3A 統合実行（Main PC 代替 collector 運用）

本仕様に加えて、Phase3A では Main PC 上で collector 系処理を統合実行するための統合 runner を定義する。

実行スクリプト：tools/phase3_run_main.ps1

主目的：

scripts/watchdog_collector.ps1 による collector watchdog 実行

tools/phase2_run_derived.ps1 による derived / quality 実行

日次 evidence_pack 生成

disk guard

NAS sync

位置づけ：

収集専用機未導入期間における Main PC の代替 collector 運用

最終的な collector 専用機移行を前提とした暫定かつ実運用可能な統合形態

Phase3A 統合 runner の役割

tools/phase3_run_main.ps1 は以下を統合して扱う。

collector watchdog 起動・監視
scripts/watchdog_collector.ps1 を起動し、collector の継続実行を担保する。

derived / quality 起動・監視
tools/phase2_run_derived.ps1 を起動し、以下を継続生成する。

hourly

daily

coverage

gaps

anomaly

evidence pack 生成
UTC 日付単位で btcts.derived.evidence_pack を実行し、証跡パックを生成する。

disk guard
logs / data のサイズおよび空き容量を定期点検し、phase3_runner.jsonl に記録する。

NAS sync
BTC_TS_NAS_ROOT が設定されている場合、logs / data を NAS 側へ同期する。

Phase3A 実行ログ

統合 runner のログ出力先は以下とする。

BTC_TS_LOGS_DIR\phase3\phase3_runner.jsonl

BTC_TS_LOGS_DIR\phase3\watchdog_stdout.log

BTC_TS_LOGS_DIR\phase3\watchdog_stderr.log

BTC_TS_LOGS_DIR\phase3\derived_stdout.log

BTC_TS_LOGS_DIR\phase3\derived_stderr.log

phase3_runner.jsonl には少なくとも以下のイベントが出力される。

phase3.start

watchdog.spawn / watchdog.attach_existing

derived.spawn

disk.guard

nas.sync.start

nas.sync.done

evidence_pack.start

evidence_pack.ok / evidence_pack.fail

evidence_pack.done

phase3.stop.once または phase3.stop.duration

phase3.exit

NAS sync の扱い

NAS sync は任意機能とし、BTC_TS_NAS_ROOT が設定されている場合のみ動作する。

同期対象：

BTC_TS_LOGS_DIR

BTC_TS_DATA_DIR

実装：

robocopy を用いた非破壊同期

判定：

robocopy の戻り値 0〜7 を成功扱いとする

備考：

実行中ログ、lock、pid などは必要に応じて除外し、sharing violation を抑制する

旧 NAS / SMB1 環境は暫定テスト用途として許容するが、最終本番構成は新しい NAS への移行を前提とする

stale lock recovery（derived runner）

tools/phase2_run_derived.ps1 は stale lock recovery を備える。

lock ファイルが存在していても、

対象 PID が存在しない場合

lock 記録の開始時刻と実プロセス開始時刻が一致しない場合

lock JSON が破損している場合

-Force 指定時
は stale lock とみなし、自動復旧可能とする。

これにより、強制終了・停電・異常停止後でも derived runner の再開性を担保する。

Phase3A 完了時点の到達状態

Phase3A 完了時点では、Main PC において以下の統合フローが成立していることを意味する。

collector watchdog 実行

derived / quality 実行

evidence pack 生成

disk guard 記録

NAS sync 実行

所定時間運転後の正常終了

正常系の代表的なイベント系列は以下とする。

phase3.start

watchdog.spawn

derived.spawn

disk.guard

nas.sync.done (ok=true)

evidence_pack.done (ok=true)

phase3.stop.duration

phase3.exit