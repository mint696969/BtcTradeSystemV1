# path: ./tmp/06_DATA_LIFECYCLE_AND_RETENTION_SPEC_2026-04-09.md
# desc: Cross-layer Data Lifecycle and Retention Spec (integrated replacement for archive/retention local spec)

更新日: 2026-04-09
位置づけ: architecture 正本候補 / `docs/architecture/` 追加文書
対象: `btcts_next/src/btcts/` 現行 mainline / data lifecycle / archive / retention / official artifact policy
置換元候補: `docs/systems/collector/Collector補助機能_Archive_Retention正式仕様書.md`

---

## 1. この仕様書の目的
本仕様書は、BTC-TS における **データの生成・保管・複製・保持・削除** の共通ルールを、現行 repo truth に合わせて統合するための文書である。

ここで固定したいのは、Collector 補助機能としての Archive / Retention ローカル仕様だけではない。より上位の、次の判断基準を一本化することが目的である。

- どのデータを system truth とみなすか
- どのデータを reproducible cache とみなすか
- どのデータを disposable intermediate とみなすか
- D hot / E cold をどう役割分担するか
- layer ごとに何を長く残し、何を短く残し、何を残さないか
- maintenance / restart / safe stop / archive GC をどう整合させるか

本仕様書は、旧 `Collector補助機能_Archive_Retention正式仕様書.md` をより高位の cross-layer policy へ吸収し、**L1 / L2 / L3 / L4 / UI をまたぐ data lifecycle 正本** として扱う。

---

## 2. この仕様書が必要な理由
layered design は code ownership だけで完結しない。データもまた layer responsibility を持つ。

もし data lifecycle の高位方針を固定しないと、次のような drift が起きる。

- raw / canonical / derived / UI intermediate が同列に保存される
- hot storage が「一時 cache」ではなく無制限蓄積場所になる
- cold storage も無制限に膨張し、何が truth かわからなくなる
- 再生成可能な中間物が長期正本と誤認される
- safe stop / restart / archive delete の判断が属人的になる

したがって本仕様書は、layered architecture の補助仕様ではなく、**layered architecture を現実運用で成立させる基盤仕様** である。

---

## 3. high-level principle
本仕様書では、data lifecycle を次の 3 層で考える。

### 3.1 Truth
再生成不能、または再生成コスト・監査価値が高く、長期保存の対象となる基礎データ。

### 3.2 Reproducible Cache
再生成可能ではあるが、毎回の再構築コスト・運用利便性・観測価値のために一定期間保存する価値があるデータ。

### 3.3 Disposable Intermediate
実験途中物、UI 中間物、再生成容易な一時成果物。短期利用後は消える前提で扱う。

この 3 層を混ぜないことが、本仕様書の最重要原則である。

---

## 4. storage role
## 4.1 Hot
現行運用では hot は `D:\btc_ts_hot` を想定する。

hot の役割は、

- 低遅延書き込み
- 直近の realtime processing
- 当日〜直近日の working set
- short-term runtime cache

である。

hot は長期正本の置き場ではない。

## 4.2 Cold
現行運用では cold は `E:\btc_ts` を想定する。

cold の役割は、

- 長期保管
- 研究 / replay / AI 学習 / 監査の基礎
- selected cache の短〜中期保持
- official artifact の保管

である。

cold は hot の単純コピー先ではなく、**truth と selected cache の保管層** として扱う。

---

## 5. layer と data class

```text
L1 capture / lane operation / raw persistence
  owner: collector_vnext
  truth: raw stream capture

L2 canonical / structural truth
  owner: ingestion/l2_canonical
  truth: canonicalized market event history

L3 market meaning / continuity / semantics
  owner: processing/l3_market_semantics
  mostly reproducible from L1/L2 + config/version

L4 shared consumer models / adapters
  owner: processing/l4_consumer_models
  mostly reproducible from L2/L3 + config/version

UI / Health / Warroom / Replay / Research
  owner: apps/operator_ui
  view state / diagnostics / cache / explicit artifact export
```

### 基本方針
- L1/L2 は truth owner に近い
- L3/L4 は meaning / consumer shaping owner だが、全出力を長期正本にしない
- UI は原則として long-term truth owner ではない
- official artifact は explicit export / explicit audit のみ長期保存対象にする

---

## 6. canonical data classes

## 6.1 Tier A: Long-term Truth
長期 cold archive を必須とするデータ。

代表:
- `data/collector_raw`
- `data/market_data`
- collector audit / supervisor audit の最低限必要部分
- official replay / official audit / evidence pack / official export
- 再生成不能または再生成コストが高いもの

### 原則
- cold 保存対象
- hot では短〜中期保持
- hot からの delete は verified 条件を満たした後のみ

## 6.2 Tier B: Reproducible Cache
cold に置く価値はあるが、TTL 付き保持または policy 付き保持にするデータ。

代表候補:
- `data/market_state`
- L3/L4 digest / summary / shared read model snapshot
- runtime outward cache
- recalculation は可能だが、毎回再構築すると重いもの

### 原則
- cold 保存は許可する
- ただし indefinite 保存を前提にしない
- medium retention を持たせる
- layer ごとに keep days / officialization 条件を持てる形が望ましい

## 6.3 Tier C: Disposable Intermediate
長期保存しない前提のデータ。

代表:
- UI intermediate cache
- widget convenience file
- ad-hoc experiment intermediate
- temporary export scratch
- derived trial output
- reproducible で監査価値の低い途中成果物

### 原則
- cold 長期保存対象にしない
- hot でも短命でよい
- 必要なら explicit export で official artifact に昇格させる

---

## 7. 現行 repo truth に基づく current mapping

## 7.1 現行 Archive Worker の copy 対象
`collector_vnext/archive/config.py` の current default relative prefixes は次である。

- `data/market_data`
- `data/collector_raw`
- `state/collector_vnext`
- `logs/collector_vnext`

### 解釈
- L1/L2 raw / canonical は既に cold archive 対象に入っている
- collector state / logs も cold copy 対象に入っている
- 一方で `data/market_state` やその他 L3/L4 派生出力は current default prefixes には入っていない

## 7.2 現行 GC の delete 対象
current mainline の GC は `relative_prefixes` のうち `data/` 配下のみを delete 候補にする。
したがって current behavior は実質次である。

- delete 対象: `data/market_data`, `data/collector_raw`
- delete 対象外: `state/collector_vnext`, `logs/collector_vnext`

### 解釈
current mainline は、**L1/L2 truth 系の hot 圧縮** を先に扱っており、state/logs は copy するが delete しない保守的設計になっている。

## 7.3 market_state の位置づけ
`market_engine/market_state/writer.py` は `data/market_state` へ JSONL を append する。
current default archive policy ではこれを cold copy 対象に含めていない。

### current interpretation
- `market_state` は Tier B 候補である
- ただし current mainline では long-term cold policy がまだ formalized されていない
- 本仕様書では、`market_state` を **selected reproducible cache** として扱い、将来 retention policy を与える方向を推奨する

---

## 8. archive / retention current implementation

## 8.1 archive worker responsibility
current mainline の archive worker は次を責務とする。

- Hot -> Cold copy
- verified GC
- archive state 出力
- archive audit 出力
- stop request への応答

watchdog とは責務分離されている。

## 8.2 current launcher defaults
`tools/run_collector_vnext_archive_worker.ps1` における current default は次である。

- `BTCTS_ARCHIVE_COLD_ROOT = E:\btc_ts`
- `BTCTS_ARCHIVE_SCAN_INTERVAL_SEC = 30`
- `BTCTS_ARCHIVE_STABLE_AGE_SEC = 600`
- `BTCTS_ARCHIVE_COPY_MIN_AGE_DAYS = 1`
- `BTCTS_ARCHIVE_GC_MIN_AGE_DAYS = 2`
- `BTCTS_ARCHIVE_MAX_FILES_PER_CYCLE = 64`
- `BTCTS_ARCHIVE_MAX_BYTES_PER_CYCLE = 268435456`
- `BTCTS_ARCHIVE_GC_ENABLED = true`
- `BTCTS_ARCHIVE_GC_DRY_RUN = true`
- `BTCTS_ARCHIVE_MAX_DELETE_FILES_PER_CYCLE = 32`

### 重要
current launcher default は **gc_enabled=true だが gc_dry_run=true** である。したがって current default stack 起動では、GC plan は走るが実 delete は行わない。

## 8.3 current copy rule
current mainline の copy plan は、少なくとも次を満たす。

- current day の `date=` directory は対象外
- stable age 未満の file は対象外
- copy min age 未満の date dir は対象外
- file 単位で copy する
- 1 cycle 内で file count / total bytes を制限する

### 注意
current mainline は CPU idle / machine load / network bandwidth を直接監視して copy 量を抑制しているわけではない。
低優先度は **scan interval・stable age・batch size 制限** で実現している。

## 8.4 current verified GC rule
current mainline の delete 候補は、少なくとも次を満たす file のみである。

1. `data/` 配下である
2. `gc_min_age_days` 以上前の `date=` directory に属する
3. hot file が stable である
4. cold file が同相対 path に存在する
5. `cold_size >= hot_size`

### 解釈
current verified GC は hash verify ではない。現状の verify は **existence + size-based** である。

---

## 9. official artifact policy
本仕様書では、derived の全保存ではなく **official artifact 保存** を推奨する。

## 9.1 official artifact とは何か
次を満たすものを official artifact と呼ぶ。

- explicit tool / explicit export によって生成される
- purpose が明示される
- replay / audit / review / evidence / report として再参照価値がある
- random intermediate ではない

## 9.2 保存方針
- official artifact は cold に保存してよい
- ただし artifact class ごとに TTL / keep policy を分けてよい
- all intermediate を official artifact 扱いにしてはならない

## 9.3 current direction
current repo には replay / research / evidence / onboarding / smoke / audit など、explicit export / explicit verification の入口がある。
この方向を強め、**価値のある derived は official artifact 化して残し、途中物は残しすぎない** 方針を取る。

---

## 10. retention policy by class

## 10.1 L1 / L2 truth
### 例
- `collector_raw`
- `market_data`

### policy
- cold archive 必須
- hot は直近 working set のみ保持
- delete は verified GC 後のみ

## 10.2 L3 / L4 reproducible cache
### 例
- `market_state`
- semantic summary cache
- shared read model snapshot

### policy
- cold 保存は optional / selected
- indefinite 保存を既定にしない
- keep days を明示する
- policy が決まるまで current default archive に無理に混ぜない

## 10.3 UI / intermediate
### 例
- widget convenience cache
- diagnostics scratch
- ad-hoc intermediate

### policy
- cold 正本化しない
- short retention で十分
- 再必要時に再生成する

## 10.4 logs / state
### policy
- copy は有用
- delete はより保守的に扱う
- current mainline でも delete 対象外でよい
- long-term archive に残す量は後で別 policy を切ってよい

---

## 11. safe stop / maintenance policy

## 11.1 なぜ必要か
maintenance / code apply / OS restart の前に、collector 書き込み・archive copy・archive delete を壊れた途中状態にしにくい停止導線が必要である。

## 11.2 current repo にある骨格
current mainline には次の骨格がある。

- UI から watchdog への restart request
- watchdog から daemon への stop request
- daemon の `STOPPING -> STOPPED` state
- archive worker の stop request
- archive worker の `STOPPING -> STOPPED` state

したがって safe stop は新規ゼロ実装ではなく、**既存 stop skeleton を stack-aware に束ねる仕事** として設計できる。

## 11.3 推奨 safe stop v1
推奨 phase は次である。

1. stop requested
2. daemon graceful stopping
3. daemon stopped confirmed
4. archive drain requested
5. archive current cycle completed
6. archive stopped confirmed
7. safe stop completed

## 11.4 shutdown 時の優先順位
shutdown / maintenance では次を推奨する。

- copy 完了を優先
- delete 完了を必須条件にしない
- delete は通常運用 cycle に残してよい

### 理由
- shutdown 安全性の本体は write 停止と copy 整合である
- delete は容量都合として重要だが、停止安全性の第一優先ではない
- stop 時に delete を必須化すると停止時間とリスクが読みにくくなる

---

## 12. file integrity current truth

## 12.1 JSON state
current state write は direct write であり、tmp + atomic replace ではない。
したがって forced kill / power loss では partial JSON が残る可能性がある。

### current mitigation
- UI / loader 側は safe read を持ち、壊れた state を空扱いで吸収しやすい
- 次回正常更新で上書き回復するケースが多い

## 12.2 JSONL append
current raw / canonical / market_state は append-only JSONL である。
forced kill 時に起きやすい壊れ方は、**末尾の最終行が途中で切れること** である。

## 12.3 archive copy
current copy は `shutil.copy2()` であり、tmp + rename 方式ではない。
forced kill 時には cold 側に途中 file が残る可能性がある。
ただし current planner は `dst_size < src_size` の時に再コピー候補へ戻す。

## 12.4 archive delete
current delete は file 単位の `unlink()` である。通常の orderly stop では current cycle 完了後に止まるため、半削り file よりも「一部 file だけ削除済み」という partial progress になりやすい。

## 12.5 future hardening
今後強化したい順序は次を推奨する。

1. safe stop v1
2. shutdown 時 GC skip / copy 優先
3. state JSON の tmp + atomic replace 化
4. archive copy の tmp + rename 化
5. hash / manifest based stronger verify

---

## 13. current open

## 13.1 market_state retention
`data/market_state` を Tier B としてどう cold へ持つかは未 formalized である。

## 13.2 per-class retention
raw / canonical / market_state / logs / state / official artifact で retention を分ける policy はまだ未実装である。

## 13.3 bandwidth / machine load awareness
current archive worker は batch limit で低優先度化しているが、CPU / I/O / network load-aware scheduling は未実装である。

## 13.4 stronger verify
current verified GC は existence + size verify であり、hash / manifest verify は未実装である。

## 13.5 delete budget
current GC には delete file count 上限はあるが、delete bytes 上限はない。

---

## 14. migration rule
本仕様書を mainline 採用する場合、旧 `Collector補助機能_Archive_Retention正式仕様書.md` は current truth の一部を含むが scope が Collector local に閉じているため、mainline 正本からは退かせるのが望ましい。

### 推奨
- `docs/architecture/06_DATA_LIFECYCLE_AND_RETENTION_SPEC_2026-04-09.md` を mainline へ配置
- 旧 `Collector補助機能_Archive_Retention正式仕様書.md` は archive / history 扱いへ寄せる

### 理由
- 現在の論点は archive worker ローカルを超えているため
- L1/L2/L3/L4/UI をまたぐ data policy は architecture 正本に置く方が自然なため
- stale / overlapping docs を mainline に重ねると、人間と GPT の両方が current truth を誤読しやすいため

---

## 15. 一文まとめ
BTC-TS の data lifecycle は、**L1/L2 truth を長く守り、L3/L4 を selected cache と official artifact に整理し、UI intermediate を長期正本化しない** ことを基本とする。Hot は realtime working set、Cold は truth と selected cache の保管層であり、archive / retention / safe stop はこの原則を壊さないように設計する。
