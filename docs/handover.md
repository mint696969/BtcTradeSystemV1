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

---

##### 以下直近の作業報告

---

btcts_next 移植作業 引き継ぎ指示書（2025-12-21 / JST）
0. 今回の結論（直近の確認結果）

コマンド出力より build_scheduler() は動作し Scheduler インスタンス生成まで正常。

type Scheduler

ただし、sch.endpoints/_endpoints/items/_items/_tasks/tasks などの **リスト属性は見つからない（None）**ため、Scheduler 実装は「辞書／内部構造／プロパティ名」が別名の可能性が高い。

つまり現段階は「Scheduler が作れた」が「何本 endpoints が登録されているかを確実に観測する仕組みは未整備」。

1. 現時点の完了範囲（btcts_next 側：現物がある）

キャンバス上の最新状態（= 次チャットで参照すべき“真”）は以下。

btcts_next（新構成）

btcts_next/src/btcts/collector/main.py

build_scheduler() 実装済み

exchanges/endpoints/monitoring/collector を btcts.settings.load_yaml() で読み

RatePolicy を構成して sch.set_policy() → endpoints を sch.add(Endpoint(...))

bitFlyer の orderbook / trades runner を最低限実装（保存は jsonl）

重大な既知バグあり：return sch の後に audit.emit("collector.scheduler.built"... ) が残っており 到達不能コード（ログが出ない）

btcts_next/src/btcts/collector/rate.py

RatePolicy / RateState / RateController 実装済み（429/Retry-After 対応あり）

btcts_next/src/btcts/core/env.py / paths.py / io.py / audit.py / __init__.py

ENV 正準名（BTC_TS_*）確定、パス解決・原子的I/O・監査 emit あり

btcts_next/src/btcts/settings/svc.py / __init__.py

schema + current(diff only) の設計で読み書き実装済み（差分ゼロなら current 削除）

btcts_next（UI）

btcts_next/src/btcts/ui/app.py

Collector/Health の2タブ構成

btcts_next/src/btcts/ui/pages/collector.py

start/stop/status を btcts.collector.control に遅延 import して操作

status.json のパスと ENV 不整合を “原因が分かる形” で表示

V1 側（参照・接続点として変更済み）

btc_trade_system/features/dash/ui_health.py

btcts_next を遅延 import して Collector 制御を Health タブ右側に表示する実装あり

btc_trade_system/features/health/health_svc.py

rate セクション由来の WARN/CRIT アイテム生成、履歴 timeline 読み込み等が追加済み

btc_trade_system/features/audit_dev/writer.py

監査出力の基盤（既存）＋（任意の）軽量レート制御の骨格が入っている

btc_trade_system/features/settings/settings_svc.py

def→current 合成、差分保存、差分ゼロなら何もしない 等の仕様が入っている

2. 未完了（＝次工程で必ずやること）
A) Scheduler の観測性が不足

今の検証は「Scheduler が作れた」止まり。
次は 「登録された endpoints 数・キー・優先度・interval」を確実に見える化する必要がある。

B) btcts_next collector/main.py に 到達不能コード

build_scheduler() の最後に return sch があり、その後の audit.emit(...) が死んでいる。
→ endpoints 登録数などのログが取れない。

C) btcts.collector.control の実装状態が不明

UI は from btcts.collector.control import start, status, stop を前提にしている。
未実装/未移植なら、UI は import で落ちる（今後の不具合源）。

D) 設定 schema ファイル（btcts_next/config/schema/*_def.yaml）の整備が未確認

settings/svc.py は schema を正としているので、schema が無いと全体が成立しない。
少なくとも exchanges_def / endpoints_def / monitoring_def / collector_def / health_def / dash_def / tabs_def が必要。

3. 次チャットでやる作業ロードマップ（手順固定）
Phase 1: まず「Scheduler の中身が見える」状態にする（最優先）

目的：build_scheduler が“何を登録したか”を確実に出力できるようにする。

btcts_next/src/btcts/collector/main.py

return sch を関数末尾に移動し、audit.emit("collector.scheduler.built"... ) を return 前に実行する。

その payload に以下を入れる：

endpoints_added

endpoints の一覧（上位20件でも良い）：[(ex, endpoint, prio, target_interval)]

endpoints_cfg のフォーマット判定（items vs map）

さらに Scheduler オブジェクトの内部構造に依存しない形で、登録時にローカル配列へ積む（これが安全）。

その後、PowerShell で再チェック

& $py -c "from btcts.collector.main import build_scheduler; sch=build_scheduler(); print('ok')"

logs に audit が出ること or 例外なく動くこと確認。

Phase 2: btcts.collector.control を確定させる（UIが落ちる根本原因潰し）

目的：UI（btcts_next 側 / V1 側 ui_health 側）が同じ start/stop/status を呼べること。

btcts_next/src/btcts/collector/control.py（無ければ作る）で提供する I/F を固定：

start() -> CollectorStatus

stop() -> CollectorStatus

status() -> CollectorStatus

実装方針は2択（どちらかに統一）：

A案（推奨・軽い）：status.json の状態＋pidfile などで「RUNNING/STOPPED」を判断（プロセス制御は後回し）

B案（運用想定）：subprocess で collector を別プロセス起動し pid を管理

※ 現時点は UI を成立させるために A案で十分。B案は後で。

Phase 3: settings schema の最低限整備（btcts_next を“単独で動く”状態へ）

目的：settings/svc の設計に沿って、最低限の schema を置く。

btcts_next/config/schema/ に以下を配置（存在確認→無ければ作成）

exchanges_def.yaml

endpoints_def.yaml

monitoring_def.yaml

collector_def.yaml

health_def.yaml

dash_def.yaml

tabs_def.yaml

中身は「defaults を持つ」ことだけ守れば良い（最初は最小でOK）

svc は {defaults: {...}} or {default: {...}} を読める

Phase 4: 実動確認（collector → status.json → health が更新される）

目的：最短の運用ループが成立すること。

collector を起動（control.start でも、直接 main でも良い）

BTC_TS_DATA_DIR\collector\status.json が更新される

V1 側 Health タブのカードが更新される（read_health が読める）

429 を食らったら rate セクション（hard/soft）が health に反映される

4. 既知の危険ポイント（ここ踏むと迷子・破壊する）

Scheduler の内部属性名（endpoints/items/tasks 等）に 依存して観測しようとしない
→ 実装差で即死するので、登録時にローカル配列で追跡してログへ出すのが正解。

btcts_next と btc_trade_system を混ぜて import 地獄にしない
→ V1 側から next を呼ぶのは ui_health.py のように 遅延 import で限定する。

パスは BTC_TS_DATA_DIR / BTC_TS_CONFIG_DIR / BTC_TS_LOGS_DIR を“正”として統一
→ どちらの世界でもこの ENV で揃える。フォールバックは最後の手段。

5. 次チャット開始時に貼ると早い「状況確認コマンド」
5.1 build_scheduler の観測（最低限）
& $py -c "from btcts.collector.main import build_scheduler; sch=build_scheduler(); print('built', type(sch).__name__)"

5.2 status.json の更新確認
Get-Content "$env:BTC_TS_DATA_DIR\collector\status.json" -ErrorAction SilentlyContinue

5.3 logs の監査確認（btcts_next）
Get-Content "$env:BTC_TS_LOGS_DIR\audit.jsonl" -Tail 50 -ErrorAction SilentlyContinue

6. 次に着手すべき「具体タスク（短期ToDo）」

btcts_next/src/btcts/collector/main.py の到達不能コード修正（return の位置、ログ出し）

Scheduler 登録一覧を build_scheduler 内でローカル追跡し、audit に出す

btcts_next/src/btcts/collector/control.py の有無確認 → 無ければ作成（A案でOK）

btcts_next/config/schema の存在確認 → 無ければ最小で作成

UI（btcts_next）で Collector タブが落ちないことを確認