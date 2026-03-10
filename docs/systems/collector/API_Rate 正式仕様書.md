desc: BtcTradeSystem NEXT における API レート制御の正式仕様。Health/UI の重大度語彙と、監査観測モードを分離し、Collector の制御・観測・長期運用診断に接続する。
API_Rate 正式仕様書
1. 目的と位置づけ

本仕様書は、BtcTradeSystem NEXT における Collector の API レート制御機構 を正式に定義する。

本仕様の目的は以下の通りである。

各取引所・各 API 提供元が定めるレート上限を 超過しない

429（Too Many Requests）や類似の抑制条件を受けても Collector 全体を停止させない

情報取得量を可能な限り維持しつつ、自動で抑制・復帰する

24時間・長期連続運用を前提として、放置運用でも診断可能な観測性を持つ

UI / Health / Soak Report / 将来の Collector 専用機構成に接続できる 正準な概念と記録方式 を持つ

本仕様書は、過去の Phase1 向け最小制御仕様を置き換える正式仕様である。
ただし、過去仕様の設計意図のうち有効なものは継承する。

2. 本仕様で明確に分離する概念

本仕様では、以下の概念を 混同しない。

2.1 重大度・状態評価の語彙

以下は主に Health / UI / 実運用判断で使用する語彙である。

NORMAL

WARN

CRIT

これらは 人間に状況を伝えるための重大度・状態評価 であり、
レート制御専用の mode 名ではない。

例：

NORMAL
通常状態。現時点で重大な問題は認められない。

WARN
現時点では重大ではないが、放置すると重大化する可能性がある。

CRIT
重大イベント、または実運用・実取引上ただちに注意が必要な状態。

これらは UI バッジ、Health 評価、運用判断に接続する語彙である。

2.2 観測密度・監査モード

以下は監査・観測の密度を表す運用モードである。

NORMAL

DEBUG

BOOST

これは BTC_TS_MODE により切り替わる 監査・観測密度のモード であり、
重大度や Health 判定とは別軸である。

NORMAL
長期運用向け。必要十分な記録のみ残す。

DEBUG
開発寄り長期運用向け。推薦修正レベルの問題を拾いやすくする。

BOOST
短期高密度解析向け。重い詳細観測を有効にする。

2.3 レート制御内部状態

API レート制御の内部状態として、実装上は必要に応じて以下のような状態遷移を持ってよい。

通常取得状態

予防的抑制状態

緊急抑制状態

hold / cooldown / backoff 中

復帰待ち状態

ただし、これらの内部状態名は Health / UI の重大度語彙と一致させる必要はない。
UI に表示する際は、内部状態から重大度・運用メッセージへ変換する。

3. 設計原則
3.1 Collector 全体を止めない

レート制御は 取得量を調整するための機構 であり、
Collector を全面停止させるための機構ではない。

429 や利用率逼迫が発生した場合も、可能な限り

一時待機

一部減速

一部抑制

floor_rps による最低限継続取得

により、Collector 全体の継続性を優先する。

3.2 過抑制より無制御超過を避ける

一時的に取得量が減ることよりも、無制御に API 上限を超過する方が危険である。
そのため、安全側に倒す制御を許容する。

3.3 可観測であること

レート制御は「効いていること」が重要であると同時に、
なぜ効いたのか / なぜ解除されたのか を後から追跡可能でなければならない。

そのため、最低限以下は必ず記録対象とする。

制御が入った時

制御が解除された時

制御が入った理由

制御が解除された理由

これは BTC_TS_MODE=NORMAL でも必須である。

3.4 Command / State / Event の分離

レート制御を含む Collector 制御は、以下の3層で扱う。

Command
人・UI・運用者の意図

State
実際に現在どうなっているか

Event
時系列で何が起きたか

レート制御は Event に最も強く現れ、State に要約され、必要に応じて Command に影響される。

4. 全体構成
Collector / Scheduler / Provider
  └─ RateController
       ├─ RatePolicy（提供元ごとの上限・方針）
       ├─ Common Policy（共通閾値・backoff・hold）
       ├─ Util / 429 / Retry-After 等の判断
       ├─ Event 出力
       └─ rate_state.json / status.json への反映

周辺との接続は以下の通り。

Scheduler

実行間隔、取得頻度、利用率情報を提供

Provider

HTTP 応答、429、Retry-After 等を提供

RateController

抑制・待機・復帰を判断

status.json

Collector 全体の実状態を要約

rate_state.json

レート制御状態の正準スナップショット

audit / event log

engage / release / reason を含む履歴を残す

Soak Report

長期運用後の自動診断に利用する

5. 用語定義
5.1 official_max_rps

対象 API / 提供元が許容する公式または運用上の最大 RPS。

5.2 util（利用率）

利用率を表す連続値。
概念上は以下のように扱う。

util = 実行量 / 許容量

値域は原則 0.0〜1.0 以上

算出方法の詳細は実装に委ねる

平均値だけでなく、短期偏りや burst 的な逼迫も考慮してよい

5.3 hold

一定時間、新規実行を遅延または抑制する状態。

5.4 backoff

429 や過負荷時に、待機時間を増やしていく抑制方式。
指数増加、固定増加、またはそれに準ずる方法を許容する。

5.5 Retry-After

提供元が返す待機推奨時間。
存在する場合は最優先で尊重する。

5.6 floor_rps

Collector を完全停止させないための最低取得量。
ただし、安全上許容されない提供元については別途停止判断をしてよい。

6. 設定項目

レート制御の共通設定は、将来的にも 設定ファイルで変更可能 であることを原則とする。
コードへの直埋めは避ける。

代表的な項目は以下を想定する。

6.1 利用率関連

util_window_warn_sec

util_window_clear_sec

warn_util

warn_clear_util

crit_util

6.2 抑制率・下限

warn_cap

crit_cap

floor_rps

6.3 429 / hold / backoff

crit_backoff_initial_sec

crit_backoff_max_sec

crit_hold_min_sec

no_429_for_sec

6.4 提供元個別設定

provider / exchange / endpoint 単位の個別上限

取得重要度

例外ポリシー

一時停止対象

7. 動作仕様
7.1 予防的抑制

利用率や短期逼迫が一定条件を超えた場合、
429 を受ける前に予防的減速を許容する。

目的は 429 を発生させないこと である。

予防的抑制では、必要に応じて以下を行う。

実効 RPS の引き下げ

実行間隔の延長

待機時間の付与

取得対象の優先度調整

7.2 緊急抑制

429 やそれに準ずる強い制限イベントを受けた場合、
即座に緊急抑制へ入る。

緊急抑制では、以下の順で判断する。

Retry-After があれば最優先で採用

無ければ backoff を適用

必要に応じて floor_rps まで低下させる

一定時間、即時復帰させない

7.3 復帰

緊急抑制または予防的抑制からの復帰は、即時ではなく条件付きとする。

復帰判断の例：

一定時間 429 が発生していない

利用率が閾値より十分下がっている

cooldown / hold が終了している

連続失敗が収束している

復帰は段階的に行ってよい。
たとえば、緊急抑制から即通常運用へ戻すのではなく、
一段低い抑制状態を経由してよい。

8. 永続化・正準出力
8.1 rate_state.json

出力先：

<DATA_DIR>/collector/rate_state.json

役割：

レート制御の現在状態を表す正準スナップショット

Collector 起動成功の最小証拠の一つ

UI / Health / Soak Report の参照元

最低限含めるべき情報：

ts

提供元ごとの現在状態

実効 RPS

待機情報

直近 429 情報

必要に応じて reason 要約

8.2 status.json

出力先：

<DATA_DIR>/collector/status.json

役割：

Collector 全体の実状態を表す正準出力

レート制御の要約状態も含めてよい

UI / Health の主要参照元

最低限含めるべき情報：

Collector 稼働状態

起動時刻

heartbeat

last_error

restart_count

rate_control summary

8.3 Event / Audit

Event は時系列履歴として出力する。
既存の audit.jsonl へ出すか、Collector 専用イベントログへ出すかは実装選択とする。
ただし、重要イベント名と基本スキーマは安定させる。

9. 必須イベント
9.1 全モードで必須（NORMALでも必須）

以下は BTC_TS_MODE=NORMAL でも必ず観測できなければならない。

rate_control.engaged

rate_control.released

最低限含めるべき項目：

ts

event

exchange または provider

prev_mode

new_mode

reason

9.2 推奨イベント

rate_control.backoff_changed

rate_control.hold_started

rate_control.hold_finished

collector.http.429

collector.rate_state.write

10. BTC_TS_MODE 連動の観測密度

本仕様では、観測密度を BTC_TS_MODE に連動させる。

10.1 NORMAL

目的：

長期運用向け

低ノイズ

必要十分な分析可能性を維持

記録対象：

engage / release

reason

重大な state 変化

429

hold / backoff の主要変化

soak report に必要な最低限の情報

10.2 DEBUG

目的：

開発寄り長期運用

UI 開発と並行する soak の主力モード

追加記録対象：

threshold 近傍の変化

util 比

backoff 変化

cooldown 情報

推奨修正レベルの候補抽出に必要な情報

10.3 BOOST

目的：

短期高密度解析

局所トラブルの掘り下げ

追加記録対象：

acquire 遅延

endpoint / provider 詳細

scheduler 判断詳細

raw timing

Retry-After の生値や詳細解析

10.4 重要ルール

イベント名と基本スキーマはモードで変えない。
変えるのは観測密度だけ とする。

11. Soak Report との関係

1週間等の unattended 運用後には、
レート制御も含めた Soak Report を生成できることが望ましい。

Soak Report では少なくとも以下を抽出対象とする。

engage 回数

release 回数

429 件数

backoff 増加回数

長時間 hold の有無

provider / exchange 単位の偏り

recommended-fix-level の候補

UI開発継続可否への示唆

12. 合格条件

以下を満たすことを API_Rate 制御の合格条件とする。

429 や逼迫時でも Collector 全体が停止しない

抑制・復帰が自動で行われる

rate_state.json が継続的に更新される

engage / release / reason が観測できる

BTC_TS_MODE に応じて観測密度が変化する

長期 unattended 運用後に、Soak Report で診断可能である

13. 将来拡張

将来、以下を拡張対象として許容する。

provider / endpoint 単位の詳細可視化

UI からの表示・制御連携

Collector 専用機への切り出し

NAS 越しの状態共有

取引重要度を考慮した優先制御

実取引系イベントとの連動

Health / WARN / CRIT 表示とのより強い接続

14. 本仕様の優先順位

NORMAL / WARN / CRIT は重大度・状態評価の語彙として扱う

NORMAL / DEBUG / BOOST は観測密度モードとして扱う

両者を混同しない

実装詳細はコードに依存しうるが、
概念分離・永続化・イベント観測・運用診断の考え方は本書を正とする

---

付録A. control.json スキーマ案

control.json は、Collector に対する 意図（Command） を表す。
実際に反映済みかどうかは status.json を参照する。

想定配置
<DATA_DIR>/collector/control.json
想定スキーマ
{
  "request_id": "20260306T120000Z_001",
  "desired_state": "running",
  "desired_mode": "NORMAL",
  "requested_at": "2026-03-06T12:00:00Z",
  "requested_by": "operator",
  "reason": "start collector for soak and UI parallel development",
  "note": ""
}
フィールド定義
field	type	required	説明
request_id	string	必須	命令を一意に識別するID
desired_state	string	必須	望ましい状態。running / stopped を基本とする
desired_mode	string	任意	望ましい観測モード。NORMAL / DEBUG / BOOST
requested_at	string (ISO8601 UTC)	必須	命令時刻
requested_by	string	任意	操作者。例: operator / ui / system
reason	string	任意	命令理由
note	string	任意	補足メモ
補足

control.json は 命令 を表す

実際に反映されたかどうかは status.json を見る

同じ内容の再投入も許容してよい

request_id により重複判定や適用済み判定を行ってよい

付録B. status.json スキーマ案

status.json は、Collector の 実状態（State） を表す。
UI / Health / Runbook / Soak Report の主要参照先とする。

想定配置
<DATA_DIR>/collector/status.json
想定スキーマ
{
  "ts_unix": 1772798462.0,
  "ts_iso": "2026-03-06T12:01:02Z",
  "actual_state": "RUNNING",
  "actual_mode": "NORMAL",
  "message": "collector running",
  "last_error": "",
  "pid": 12345,
  "started_at": "2026-03-06T12:00:05Z",
  "last_heartbeat": "2026-03-06T12:01:02Z",
  "restart_count": 0,
  "control": {
    "last_request_id": "20260306T120000Z_001",
    "last_applied_at": "2026-03-06T12:00:06Z"
  },
  "watchdog": {
    "state": "RUNNING",
    "pid": 23456,
    "last_seen": "2026-03-06T12:01:01Z"
  },
  "derived": {
    "state": "RUNNING",
    "last_seen": "2026-03-06T12:01:00Z"
  },
  "rate_control": {
    "summary_state": "WARN",
    "engaged": true,
    "last_reason": "http_429",
    "last_changed_at": "2026-03-06T11:58:30Z"
  },
  "items": []
}
フィールド定義
field	type	required	説明
ts_unix	number	必須	状態生成時刻（UNIX秒）
ts_iso	string	必須	状態生成時刻（ISO8601 UTC）
actual_state	string	必須	実状態。RUNNING / STOPPED / ERROR 等
actual_mode	string	任意	現在の観測モード。NORMAL / DEBUG / BOOST
message	string	任意	人間向け短文
last_error	string	任意	直近エラー要約
pid	integer	任意	Collector 本体 PID
started_at	string	任意	起動時刻
last_heartbeat	string	任意	生存確認時刻
restart_count	integer	任意	再起動回数
control	object	任意	直近 control 適用情報
watchdog	object	任意	watchdog 実状態要約
derived	object	任意	derived / quality 実状態要約
rate_control	object	任意	レート制御要約
items	array	任意	将来の endpoint/provider 単位の状態一覧
付録C. rate_state.json スキーマ案

rate_state.json は、レート制御の 現在スナップショット を表す。
Collector 起動の最小証拠の一つであり、UI / Health / Soak Report が読む。

想定配置
<DATA_DIR>/collector/rate_state.json
想定スキーマ
{
  "ts": 1772798462.0,
  "items": {
    "bitflyer": {
      "ts": 1772798461.8,
      "exchange": "bitflyer",
      "mode": "WARN",
      "eff_max_rps": 2.5,
      "wait_ms": 120,
      "last_429_ts": 1772798310.0,
      "last_retry_after_sec": 2.0,
      "reason": "http_429"
    },
    "binance": {
      "ts": 1772798461.7,
      "exchange": "binance",
      "mode": "NORMAL",
      "eff_max_rps": 5.0,
      "wait_ms": 0,
      "last_429_ts": 0.0,
      "last_retry_after_sec": 0.0,
      "reason": ""
    }
  }
}
フィールド定義
field	type	required	説明
ts	number	必須	スナップショット時刻
items	object	必須	provider/exchange ごとの状態
items.*.ts	number	必須	個別状態時刻
items.*.exchange	string	必須	提供元識別子
items.*.mode	string	必須	レート制御内部状態
items.*.eff_max_rps	number	必須	実効最大RPS
items.*.wait_ms	integer	必須	現在の待機時間
items.*.last_429_ts	number	任意	直近429時刻
items.*.last_retry_after_sec	number	任意	直近 Retry-After 秒
items.*.reason	string	任意	現在状態の代表理由
補足

mode はレート制御内部状態を表す

これは Health/UI の重大度語彙 NORMAL / WARN / CRIT と同一意味である必要はない

UI 表示時は、必要に応じて内部状態を別のバッジ表現へ変換してよい

付録D. Event スキーマ案

Event は 履歴（Event） であり、時系列で起きたことを残す。
audit.jsonl または Collector 専用 event log に出力してよい。

共通基本形
{
  "ts": "2026-03-06T12:05:00Z",
  "event": "rate_control.engaged",
  "feature": "collector",
  "level": "INFO",
  "exchange": "bitflyer",
  "prev_mode": "NORMAL",
  "new_mode": "WARN",
  "reason": "warn_util_threshold",
  "payload": {
    "util_ratio": 0.93
  }
}
最低限共通で持つべき項目
field	type	required	説明
ts	string	必須	発生時刻（ISO8601 UTC）
event	string	必須	イベント名
feature	string	任意	機能分類
level	string	必須	DEBUG / INFO / WARN / ERROR
reason	string	任意	発生理由
payload	object	任意	追加情報
付録E. レート制御イベントの初期標準名案

最低限、以下のイベント名を標準候補とする。

event	説明
rate_control.engaged	制御が入った
rate_control.released	制御が解除された
rate_control.backoff_changed	backoff 値が変化した
rate_control.hold_started	hold 開始
rate_control.hold_finished	hold 終了
collector.http.429	429 受信
collector.rate_state.write	rate_state.json 更新
NORMAL でも必須のイベント

rate_control.engaged

rate_control.released

NORMAL でも必須の項目

ts

event

exchange または provider

prev_mode

new_mode

reason

付録F. mode別の観測密度方針（簡易表）
観測モード	記録方針
NORMAL	長期運用向け。engage / release / reason と主要状態遷移を記録
DEBUG	開発寄り長期運用向け。threshold近傍、backoff、復帰候補などを追加記録
BOOST	短期高密度解析向け。acquire待機、scheduler判断、endpoint詳細などを追加記録
重要ルール

重要イベント名と基本スキーマは共通

変えるのは 記録密度 のみ

重大度語彙 NORMAL / WARN / CRIT と混同しない