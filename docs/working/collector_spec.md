**# BtcTradeSystem NEXT — Collector 仕様書（ドラフト）**

\

**## 0. 目的とスコープ**

\

本書は、BtcTradeSystem NEXT の Collector（収集器）について、****本番 24H 連続稼働****を前提に「事故らない」ことを最優先として、仕様（責務・I/F・状態・設定・安全装置）を確定する。

\

スコープは以下。

\

* Collector の起動/停止/状態（UI・Health が参照する正準I/F）

* 取引所設定（非秘密/秘密の分離）と必須未充足の扱い

* レート制御（soft/hard/429）と状態の公開

* status.json 等の状態ファイル

* 監査（audit）とログ出力

\

非スコープ（本書では詳細を確定しない）

\

* 戦略・売買ロジック

* 学習/推論（dataset）

* UI 全体のタブ設計

\

---

\

**## 1. 正準（境界・パス・環境変数）**

\

**### 1.1 正準コード**

\

* `./btcts_next/src/btcts` が唯一の正。

\

**### 1.2 運用正準パス（ENV 優先）**

\

`btcts.core.paths` に従う。

\

* 非秘密設定（current）: `BTC_TS_CONFIG_DIR` → `paths.config_dir()`

* データ: `BTC_TS_DATA_DIR` → `paths.data_dir()`

* ログ: `BTC_TS_LOGS_DIR` → `paths.logs_dir()`

* 秘密情報: `BTC_TS_SECRETS_DIR` → `paths.secrets_dir()`

\

フォールバック（ENV 未指定時）は `btcts_next` 内。

\

**### 1.3 ensure の扱い**

\

* 収集・保存系は `ensure=True`（既定）で良い。

* 表示/監査用途は `ensure=False` を原則（副作用でディレクトリを増やさない）。

\

---

\

**## 2. Collector 構成要素と責務**

\

**### 2.1 UI（Collector ページ）**

\

* パス: `./btcts_next/src/btcts/ui/pages/collector.py`

* 責務:

\

  * Start/Stop/Refresh の操作導線

  * 現在状態（PIDベースの status()）の表示

  * `status.json`（raw）の表示と、ENV/パス不整合の原因提示

  * ****安全装置****：必須未充足なら Start は disabled（グレーアウト）

\

**### 2.2 Control（起動/停止/状態 I/F）**

\

* パス: `./btcts_next/src/btcts/collector/control.py`

* 責務:

\

  * 二重起動防止（ロック＋pidfile）

  * Start/Stop の直列化（連打・同時押し耐性）

  * stale pid 清掃

  * 起動失敗の可視化（collector.log）

  * ハンドシェイク（`rate_state.json` 生成確認）

  * 停止の確実性（Windows: taskkill/TerminateProcess）

\

**### 2.3 Rate（レート制御）**

\

* パス: `./btcts_next/src/btcts/collector/rate.py`

* 責務:

\

  * 取引所別の rate policy を保持

  * acquire による実行許可（wait 返却）

  * 429 / Retry-After の緊急抑制

  * health/UI 向け state snapshot 提供

\

**### 2.4 Settings（schema + current 差分）**

\

* パス: `./btcts_next/src/btcts/settings/svc.py`

* 責務:

\

  * schema（配布物）+ current（運用差分）で実効値を返す

  * save は defaults との差分のみ保存

  * 差分ゼロなら current を削除（defaultへ戻す）

\

---

\

**## 3. 取引所設定（非秘密/秘密の分離）**

\

**### 3.1 非秘密（config/ui）**

\

* 正準: `paths.config_dir()` 配下（例：`E:\btc_ts\config\ui`）

* 管轄: `settings/svc.py`（schema + diff）

* 例（論理名）:

\

  * `exchanges`（取引所一覧・URL・機能フラグ・閾値等）

\

**### 3.2 秘密（secrets）**

\

* 正準: `paths.secrets_dir()` 配下（例：`E:\btc_ts\secrets`）

* Git 管理外

* UI で入力は扱うが、****値の再表示はしない****。

\

  * 表示は「設定済み（**********）」/「未設定（empty）」のみ。

\

**### 3.3 推奨構造（浅い構造）**

\

* 非秘密: `config/ui/exchanges.yaml`（集約）

* 秘密: `secrets/exchanges.yaml`（集約）

\

（将来増えたら `secrets/exchanges/<exchange>.yaml` へ分割も可能だが、当面は浅くする）

\

---

\

**## 4. 必須未充足の扱い（Start グレーアウト）**

\

**### 4.1 基本方針（確定）**

\

* ****必須項目が埋まっていない取引所は disabled 扱い****。

* UI の Start ボタンは disabled（押せない）。

\

**### 4.2 必須項目の考え方**

\

必須は「取引所共通」＋「機能ごと」に分離する。

\

* 取引所共通（例）

\

  * exchange id/name

  * base URL（または endpoint 参照が有効）

  * rate policy の基準（exchanges.<id>.rate.max_rps > 0）

* 機能ごと

\

  * public 収集（trades/orderbook 等）はキー不要

  * private 機能（口座/注文等）はキー必須

\

**### 4.3 判定の責務**

\

* 判定結果は「ready: bool」と「reasons: list[str]」を返せること。

* UI はこの判定結果に従い、Start を disabled にする。

\

（実装で確定：Settings層（btcts/settings/svc.py）が ready/reasons/details を提供し、UI がそれに従う）

\

---

\

## 5. レート制御仕様（ratio 前提）

### 5.1 UI 表示/入力

- 運用者は「MAX=100 の割合（%）」で扱う。
- 内部は 0.0〜1.0 の ratio で保持。

### 5.2 soft/hard の定義（仕様として固定）

- soft/hard は **「上限倍率（cap）」**を表す（MAX=100% の割合）。
  - NORMAL: `eff_max_rps = official_max_rps * 1.0`
  - WARN:   `eff_max_rps = official_max_rps * soft_ratio`
  - CRIT:   `eff_max_rps = official_max_rps * hard_ratio`
- 直感：数値が小さいほど“より強く抑制”する。

**制約（安全装置）**
- ratio は 0.0〜1.0（1.0 が 100%）。
- `soft_ratio <= 1.0`、`hard_ratio <= 1.0`。
- WARN は CRIT より“緩い”抑制であるべきなので、原則 **`soft_ratio >= hard_ratio`**。
  - 逆転している場合は、読み込み時に補正（入れ替え）または disabled（必須未充足）扱いのいずれかを実装で確定する。

### 5.3 モード

- NORMAL / WARN / CRIT

### 5.4 429 / Retry-After

- 429 を受けた場合、強制的に CRIT へ遷移。
- Retry-After があればその秒数を優先して hold。
- 429 発生時は監査に記録し、last_ok を更新しない（異常を「見える」状態に保つ）。

### 5.5 util_ratio（外部観測）の扱い

- util_ratio は外部観測から渡され、mode を更新する材料として使う。
- **soft/hard は util 閾値ではない**（上限倍率）。
- util_ratio の定義（観測方法・集計窓）は実装側（Scheduler）で確定する。
  - 仕様としては「util_ratio が高いほど抑制が強くなる」単調性のみ保証すればよい。

### 5.6 state の公開

- health/UI へ `snapshot()` で状態を公開。

## 6. 状態ファイル

### 6.1 status.json（CollectorStatus）

- 置き場所（正準）: `<DATA_DIR>/collector/status.json`
  - 実装: `paths.data_dir()/collector/status.json`

- 更新主体: Collector（main ループ）
- 書き込みは排他（`io.file_lock`）で行う（timeout=10s / stale=5s）。

- 形式（最低限の保証）:
  - `ts_unix` : float（UNIX秒）
  - `ts_iso`  : str（UTC ISO / Z）
  - `mode`    : str（例: RUNNING / STOPPED / ERROR）
  - `items`   : list（常に list。欠損/None を許容しない）
  - その他: message / last_error 等は将来増減し得るが、UIは安全に扱う

- 例外ケース:
  - Collector未起動/ファイル欠損でも UI/Health は落とさず扱う（空扱い＋理由表示）。

### 6.2 rate_state.json（RateController snapshot）

- 置き場所（正準）: `<DATA_DIR>/collector/rate_state.json`
  - 実装: `paths.data_dir()/collector/rate_state.json`
  - 後方互換のため、ファイル名は固定維持する。

- 更新主体: Collector（rate controller）
- 形式:
  - `ts`    : float（UNIX秒）
  - `items` : dict（rate controller の snapshot を格納する。list ではない）
- 監査:
  - `collector.rate_state.write`（DEBUG）

### 6.3 pidfile / collector.log

- pidfile: `<LOGS_DIR>/collector.pid`
  - 実装: `paths.logs_dir()/collector.pid`
- log: `<LOGS_DIR>/collector.log`
  - 実装: `paths.logs_dir()/collector.log`
- 備考:
  - start/stop はロック＋pidfileで直列化し、二重起動を防止する。

### 6.4 ハンドシェイク（起動成功の最低条件）

- start 成功の最小証拠として `rate_state.json` の生成を確認する。
- 生成されない場合は start.fail とし、プロセスを停止させる（孤児化防止）。

## 6A. 収集データの記録（永続化）

### 6A.1 保存形式

- 収集データは JSONL（1行1レコード）で追記保存する。
- 追記は `io.file_lock` により排他し、同一ファイルの破損を避ける。
初期実装は “raw payload を欠損なく追記保存” を最優先とし、正規化・学習用スキーマ整形は後段の責務とする（将来拡張）。

### 6A.2 出力パス規約（日次ローテーション）

- 正準出力パス:
  - `<DATA_DIR>/collector/<exchange>/<topic>/<YYYYMMDD>.jsonl`
- 日付はUTC基準とする（運用と再現性を優先）。

### 6A.3 落ちた場合の扱い（再開性）

- 追記型のため、Collectorが停止しても、それまでに書かれた行は原則読み取り可能。
- 再起動後は同一規約のファイルへ追記が再開される。
- ただし fsync_each=False の場合、OSキャッシュ内の末尾データが失われる可能性は残る（堅牢性/性能のトレードオフ）。

**### 6A.4 学習・解析向けの出力スキーマ（bitFlyer / 将来拡張案）**

#### orderbook（compact_board）

- レコード必須:
  - `ts`（epoch秒）
  - `exchange`, `topic`
  - `product_code`
  - `best_bid`, `best_ask`, `mid`, `spread`
  - `bids[]`, `asks[]`（要素: `price`, `size`）

#### trades（compact_executions）

- 返却: `{ts, exchange, topic, product_code, items[]}`
- items要素:
  - `id`（約定ID。重複/欠損検知に使用）
  - `exec_date`（文字列）
  - `price`（float）
  - `size`（float）
  - `side`（BUY/SELL）

## 7. 監査（audit）

### 7.1 出力先と形式（正準）

- 出力先: `<LOGS_DIR>/audit.jsonl`（`paths.logs_dir()/audit.jsonl`）
- 形式: JSONL（1行1JSON、UTF-8）
- 追記は排他（`io.file_lock`）＋ fsync_each=True（監査は耐障害性を優先）
- 監査ログは UTF-8 で書き出す。hint 等のメッセージは **ASCII中心**を推奨する（Windows 環境での文字化け回避）。

audit は BTC_TS_MODE により出力有無が切り替わる。
OFF：出力しない
DEBUG / BOOST：出力する
テスト／検証時は BTC_TS_MODE=DEBUG（推奨）を指定する。

### 7.2 Collector 監査イベント名（確定）

Collector 範囲（main/control/status）のみを列挙する。rate.py は emit しない。

- `collector.main.start`
- `collector.scheduler.built`
- `collector.signal`
- `collector.main.error`
- `collector.main.exit`

- `collector.http.unexpected_payload`
- `collector.http.429`
- `collector.http.fail`

- `collector.endpoint.ok`
- `collector.endpoint.skip`

- `collector.status.write`
- `collector.rate_state.write`

- `collector.start`
- `collector.start.fail`
- `collector.stop`
- `collector.stop.fail`
- `collector.lock.timeout`
- `collector.endpoints.empty`
- `collector.no_data`

### 7.3 payload 補足

collector.endpoint.skip は payload に reason / hint / normalized を含め、設定ミスまたは未対応topicの切り分けを可能にする。

### 7.4 no_data 判定（確定）

起動後、一定時間（startup_grace_sec）を経過しても collector.endpoint.ok が1度も発生しない場合、Collector は collector.no_data（CRIT）を emit し、status.json を ERROR に更新して停止する。
判定周期は no_data_check_every_sec で調整する。

**## 8. 運用（24H）最小要件**

\

* Start は必須未充足なら押せない。

* 二重起動しない。

* 起動失敗が UI とログで追える。

* 429 で暴走しない（抑制・記録）。

* status.json と pid/status が矛盾しない（少なくとも混乱源を掃除する）。

\

- no_data 判定は **7.4** に従う（startup_grace_sec / no_data_check_every_sec で調整）。

---

\

## 9. 未確定（次に確定する事項）

- secrets の保存I/F（UI からの保存方法・マスク表示の規約）

（Collector範囲外は本書では扱わない：HealthはHealth仕様書、Rate制御はRate制御仕様書で管理）
