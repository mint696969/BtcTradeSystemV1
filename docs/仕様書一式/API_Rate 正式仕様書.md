# API_Rate 正式仕様書

## 1. 目的と位置づけ

本仕様書は、BtcTradeSystem NEXT における **Collector の API レート制御機構（Phase1）** を正式に定義する。

目的は以下の通り：

* 各取引所が定める API レートリミットを **超過しない**
* 429（Too Many Requests）等の制限を受けても **Collector 全体が停止しない**
* 情報取得量を極力維持しつつ、**自動的に抑制・復帰**する
* 24時間・長期連続運用に耐える
* 後続の GPT / 開発者が **コードを読まずに全体像を理解できる**

本仕様は Phase1（最低限の自動制御）を対象とし、UI 可視化等は Phase2 で扱う。

---

## 2. 全体構成

```
Scheduler
  └─ RateController
        ├─ RatePolicy（取引所ごとの公式上限）
        ├─ 共通ポリシー（rate_control.yaml）
        ├─ util 判定（WARN 予防）
        └─ 429 緊急制御（CRIT）
```

* **Scheduler**

  * 実行回数から util（利用率）を算出
  * util を RateController に渡す

* **RateController**

  * mode（NORMAL / WARN / CRIT）を管理
  * 実効最大RPS（eff_max_rps）を計算
  * wait / hold / backoff を決定

---

## 3. 用語定義

### 3.1 mode

| mode   | 意味                  |
| ------ | ------------------- |
| NORMAL | 通常運用。公式上限で取得        |
| WARN   | 予防的抑制。429 を避けるための減速 |
| CRIT   | 緊急抑制。429 受信後の強制制限   |

---

### 3.2 util（利用率）

**util = 実行リクエスト数 / 許容最大リクエスト数**

* Scheduler が一定時間窓で算出
* util は 0.0〜1.0 の連続値
* 「平均100%超」だけを判断軸にしない

---

## 4. 設定（rate_control.yaml）

### 4.1 util 判定関連

| key                   | 説明                         |
| --------------------- | -------------------------- |
| util_window_warn_sec  | WARN 判定用の時間窓（秒）            |
| util_window_clear_sec | WARN 解除用の時間窓（秒）            |
| warn_util             | util >= この値で WARN へ        |
| warn_clear_util       | util <= この値で WARN 解除       |
| crit_util             | util >= この値で CRIT へ（主に安全弁） |

※ WARN と解除にヒステリシスを持たせ、振動を防止する。

---

### 4.2 抑制率（cap）

| key       | 説明                            |
| --------- | ----------------------------- |
| warn_cap  | WARN 時の上限倍率（公式RPS × warn_cap） |
| crit_cap  | CRIT 時の上限倍率                   |
| floor_rps | 完全停止を避けるための最低RPS              |

実効最大RPS：

```
eff_max_rps = max(official_max_rps * cap, floor_rps)
```

---

### 4.3 429 / backoff 制御

| key                      | 説明                 |
| ------------------------ | ------------------ |
| crit_backoff_initial_sec | 初回 backoff 秒数      |
| crit_backoff_max_sec     | backoff 最大秒数       |
| crit_hold_min_sec        | 最低 hold 秒数         |
| no_429_for_sec           | この秒数 429 が無ければ復帰可能 |

優先順位：

1. Retry-After（あれば最優先）
2. backoff（指数増加）
3. floor_rps による最低取得

---

## 5. 動作仕様

### 5.1 util による WARN 制御（予防）

* util >= warn_util → WARN
* util <= warn_clear_util → NORMAL
* 429 中は util による解除を行わない

目的：

* 429 を **発生させない** ための事前減速

---

### 5.2 429 による CRIT 制御（緊急）

* 429 受信時：即 CRIT
* Retry-After があればそれを hold として使用
* 無い場合は backoff を適用

CRIT 中：

* util が低下しても即復帰しない
* no_429_for_sec 経過後にのみ復帰可能

---

## 6. 永続化・監査

### 6.1 rate_state.json

* 出力先：`<DATA_DIR>/collector/rate_state.json`
* 内容：

  * ts（UNIX秒）
  * exchange ごとの mode / eff_max_rps / wait_ms 等

Collector 起動成功の **最小証拠** として扱う。

---

### 6.2 audit イベント（固定名）

| event                      | 内容                     |
| -------------------------- | ---------------------- |
| collector.rate.mode        | mode 変化                |
| collector.rate.hold        | wait / hold 発生         |
| collector.rate_state.write | rate_state.json 書き込み   |
| collector.http.429         | API 429 受信（provider 側） |

---

## 7. Phase1 合格条件

* WARN(util) → CRIT(429) → 復帰が自動で行われる
* Collector 全体が停止しない
* rate_state.json が継続的に生成される
* 設定変更で挙動を調整可能（コード直埋め無し）

---

## 8. Phase2 以降の拡張予定（参考）

* ダッシュボードでの可視化（mode / util / hold）
* 取引所別・endpoint別の詳細表示
* Health との統合評価

---

## 9. 本仕様の前提

* Collector / Health 正式仕様書と矛盾する場合、
  **本仕様（APIレート制御）を正とする**
* 実装詳細はコードに依存するが、
  **判断軸・状態遷移・永続化の考え方は本書を基準とする**
