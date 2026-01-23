# collector_rate_control_spec.md

## 目的（Phase 1）

Collector を 24 時間連続運用しつつ、取引所ごとの API レート制限を自動制御して **429 を極力踏まず**、かつ **収集が完全停止しない** ことを保証する。

* 対象：Collector の API 呼び出し（取引所ごと）
* 非対象：通知/自動復旧/推論（Phase 2 以降）

## 用語

* **official_max_rps**：取引所の公式上限（requests/sec）。exchanges.yaml に取引所単位で定義。
* **util（利用率）**：一定窓で観測した「実使用レート / 許容上限レート」。0.0〜1.0。
* **cap（上限制限倍率）**：実効上限 `eff_max_rps = official_max_rps * cap`。
* **floor_rps**：完全停止を避けるための最低レート下限（Retry-After 指示がある場合は例外的に従う）。
* **WARN / CRIT**：制御段階（計画減速 / 緊急制限）。

## 設計方針（事故りにくさ優先）

### 三層制御

1. **常時：上限遵守（RateLimiter）**

   * 取引所単位で `eff_max_rps` を超えないように実行許可（token bucket / next_allowed_at など）。
2. **WARN：予防的減速**

   * 短窓 util が高い状態が続く場合、`warn_cap` を適用して `eff_max_rps` を下げる。
3. **CRIT：429 などの緊急制限**

   * 429 を一次根拠として `crit_cap` を適用し、Retry-After を最優先で hold。

### 「止めない」

* 原則として `eff_max_rps >= floor_rps` を維持し、収集が完全停止しないようにする。
* ただし **Retry-After が明示された場合は最優先で従う**（安全のため）。

## util（利用率）の定義（推奨）

### 観測窓

* **短窓：10秒**（WARN 判定用）
* **復帰判定：30秒**（ヒステリシス用）

### 分子（推奨）

* **実際に送ったリクエスト数**（= provider 呼び出し回数）

  * 成功/失敗に関わらず「送った」事実をカウント
  * 429 は別途 CRIT 判定に直結するため util の分子に依存しない

### 分母

* `eff_max_rps`（現在の実効上限）× 観測秒数

### util の算出

* `util_10s = req_count_10s / (eff_max_rps * 10)`
* scheduler が exchange 単位に rolling window / EWMA のどちらかで保持。

  * Phase 1 推奨：rolling window（実装が単純で説明しやすい）

## 状態遷移（推奨・ヒステリシスあり）

### WARN

* 进入（WARN へ）：`util_10s >= warn_util` が `warn_enter_confirm_sec` 以上継続
* 解除（NORMAL へ）：`util_30s <= warn_clear_util` が `warn_clear_confirm_sec` 以上継続

### CRIT

* 进入：

  * 429 を受信（一次根拠）
  * もしくは `util_10s >= crit_util` を継続（※Phase 1 では 429 優先でよい）
* 解除：

  * `crit_hold_min_sec` 経過後、かつ `no_429_for_sec` を満たす
  * 解除後は一気に NORMAL に戻さず **WARN → NORMAL** の段階復帰を推奨

## 係数（推奨デフォルト）

### 判定閾値（util）

* `warn_util = 0.90`
* `warn_clear_util = 0.85`
* `crit_util = 0.98`（Phase 1 では 429 優先で実質未使用でもよい）

### cap（倍率）

* `warn_cap = 0.80`
* `crit_cap = 0.50`

### hold / backoff

* `retry_after_priority = true`
* `crit_backoff_initial_sec = 2`
* `crit_backoff_max_sec = 30`
* `crit_hold_min_sec = 10`
* `no_429_for_sec = 60`

### floor

* `floor_rps = 0.10`（= 10秒に1回）

## 設定（置き場所の方針）

### 共通ポリシー設定ファイル（固定）

* **配置**：`<CONFIG_DIR>/rate_control.yaml`（本番例：`E:\btc_ts\config\ui\rate_control.yaml`）
* **目的**：WARN/CRIT の判定閾値・cap・hold/backoff・floor など、取引所共通の制御パラメータを集中管理する。
* **方針**：Health 用 `monitoring.yaml` とは分離し、レート制御は本ファイルを唯一の正とする。

## 設定（置き場所の方針）

### 取引所ごと（exchanges.yaml）

* `exchanges.<id>.rate.official_max_rps`

  * 互換：現状が `max_rps` の場合は当面両対応し、最終的に official_max_rps に正規化

### 共通ポリシー（新規：rate_control.yaml など）

* 上記「判定閾値（util）」「cap（倍率）」「hold/backoff」「floor」
* Phase 1 は直埋めでも可だが、Phase 2 の可視化・運用調整を考えると設定化が望ましい。

## 実装接続点（Scheduler → RateController）

### util カウントのタイミング（固定）

* **送信した時点で +1（推奨・固定）**

  * 成功/失敗に依存せず「送った」事実を分子にする。
  * 実装上は provider 呼び出し直前（HTTP リクエスト送信直前）で exchange カウンタを増やす。

### Scheduler 側の責務

* exchange 単位で「直近10秒の送信回数」「直近30秒の送信回数」を保持する（Phase 1 は rolling window）。
* 定期的に util を算出し、`RateController.set_mode_by_util(exchange, util)` を呼ぶ。
* 429 は provider 結果から `RateController.on_429(exchange, retry_after_sec)` を呼ぶ（一次根拠）。

## 監査・状態（運用の根拠）

### audit イベント名（固定）

* `collector.rate.mode`：mode 遷移（NORMAL→WARN→CRIT、復帰）
* `collector.rate.hold`：hold 実施（Retry-After/バックオフによる待機の事実）
* `collector.http.429`：HTTP 429 発生（CRIT 相当の一次根拠）
* `collector.rate_state.write`：rate_state.json 書き出し（DEBUG）

※ 監査は「事実のみ」を記録し、推論・解釈は行わない（Phase 2 以降で可視化）。

## 監査・状態（運用の根拠）

* `rate_state.json` に以下を残す

  * mode / eff_max_rps / util_10s / util_30s / last_429_ts / hold_until など
* audit に以下を残す（事実のみ）

  * mode 遷移（NORMAL→WARN→CRIT、復帰）
  * 429 発生、Retry-After 値、hold 秒数

## Phase 1 合格条件

* 24h 回しても 429 連打にならず、Collector が停止しない（no_data 以外で落ちない）
* rate_state.json が更新され続け、現在の mode と eff_max_rps が追跡できる
* 429 が発生した場合、CRIT に遷移し、Retry-After があれば優先 hold される
* 収集が完全停止しない（Retry-After 指示時を除く）
