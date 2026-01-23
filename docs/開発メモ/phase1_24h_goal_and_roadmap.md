24H正式稼働ロードマップ（フェーズ1）
0. 前提固定（最初に合意して以後ブレさせない）

UIの Start/Stop は 同一ホスト上の Collector を制御する（遠隔は別機能）

V1は参考資料。NEXTに V1構造・命名を復活させない

正準の出力は DATA/LOGS/CONFIG のENVに従う（repo下へ出さない）

1. 取引所登録（最小セットで開始）

目的：24H稼働対象を最小化して事故確率を下げる。

最初の正式稼働対象（推奨）

bitFlyer

topic：trades / orderbook のみ

endpoints / scheduler 設定（登録方式を確定）

収集ファイルの出力パスが DATA 配下に統一されることを確認

完了条件

取引所登録後、短時間（5〜10分）運転で jsonl が増加し続ける

2. APIレート制御（24H稼働の中核）

目的：制限事故を構造的に防ぐ。

Soft-limit（WARN）/ Hard-limit（CRIT）の挙動を確定

429 / Retry-After を受けたら Hard-limit を即発動

safety_factor を運用側で調整できる導線を確保

rate_state を DATA 配下に出し、内部状態を観測可能にする

完了条件

429が発生しても request が抑制され、連打しない

rate_state が更新され、cooldown/penalty 等が読み取れる

3. 監査（Audit）整備（復旧可能性を作る）

目的：夜間に何が起きたか翌朝追える状態にする。

start / stop / start_failed / stop_failed

config load（要約）

429 / Retry-After（必須）

例外（原因追跡できる粒度）

完了条件

audit.jsonl に重要イベントが必ず出る

24H後に「何が起きたか」を audit だけで説明できる

4. Health（読むだけの監視・判断）

目的：止めるべき状態を判断できるようにする（ただし制御しない）。

status / rate_state を参照して WARN/CRIT を判定

判定理由（reasons）を UI に表示できる形にする

代表的な異常

収集停止（更新が止まる）

429頻発 / cooldown延長中

status.lock 等の残骸による起動不能

完了条件

Health画面で「今危険かどうか」が一目で分かる

CRITの理由が必ず表示される

5. ダッシュボード（運用安全装置として整備）

目的：Start/Stop を安全にする（便利機能ではなく安全装置）。

Start 成功判定＝「プロセス起動」ではなく statusがRUNNINGで回っている

Stop 成功判定＝statusがSTOPPEDに遷移し、lock残骸が残らない

連打・rerun耐性（ボタン無効化、状態同期）

状態表示（RUNNING/WARN/CRIT、直近429、cooldown等）

完了条件

Start/Stop を連続操作しても落ちない・二重起動しない

状態表示が status/rate_state/audit と矛盾しない

6. 24時間正式稼働テスト（フェーズ終端）

目的：机上の安全ではなく、実稼働で安全性を証明する。

24H稼働の間、定点観測（例：1時間ごとに status / audit の要点だけ確認）

収集データの増加（jsonl mtime/size）

429が出た場合の抑制と回復の確認

異常が出た場合の復旧手順の確立（Stop→状態確認→Start）

完了条件（フェーズ合格）

24時間連続稼働できた

API制限で停止・BAN・長時間遮断を起こしていない

監査ログと状態ファイルで、24Hの挙動を説明できる

UIから安全に止められる（後片付けも含む）

フェーズ完了後（次フェーズの入口）

取引所／topic を増やす（段階的）

collector専用機運用へ移行（ただしローカル制御は維持）

“完成仕様”として確定した項目を docs/仕様書一式/ に昇格