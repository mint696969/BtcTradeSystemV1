# path: ./docs/architecture/L3_L4_EVOLUTION_AND_COMPATIBILITY_POLICY_2026-04-05.md
# desc: Compatibility and evolution policy for L3 meaning and L4 shared bundles.
# L3 / L4 Evolution and Compatibility Policy

更新日: 2026-04-05
位置づけ: L3 meaning と L4 bundle を今後変更するときの互換ポリシー
対象: `processing/l3_market_semantics/` と `processing/l4_consumer_models/`

---

## 1. この仕様書の目的
本仕様書は、将来 L3 の意味づけや L4 の束ね方が変わる可能性を前提に、変更コストを局所化するための互換ルールを定める。

この仕様書が必要な理由は次の通り。

1. L3 の meaning はまだ成長段階であり、将来変わる可能性が高い
2. 特に orderbook diff / rebuild / continuity / interpretation 周辺は正解が固定しにくい
3. L4 以降まで破壊的変更を波及させると維持コストが高すぎる
4. AI / analytics / replay / operator feedback を通じて meaning が改善される余地がある

---

## 2. 基本認識

### 2.1 L1 / L2
- 取得・canonical・structural truth は比較的安定
- 変更頻度は低い前提でよい

### 2.2 L3
- 市場意味の正本だが、まだ改良余地がある
- 特に diff 解釈、continuity、trust、interpretation は進化しうる
- したがって freeze 前提ではなく controlled evolution 前提で扱う

### 2.3 L4
- shared bundle は shared contract として育てる
- 意味を変える場ではない
- ただし bundle の束ね方や field は進化しうる

---

## 3. 変更の重さ

## 3.1 L3 meaning change
最も重い。

### 例
- trust_state の定義変更
- continuity broken / resynced 判定変更
- wall / sweep / absorption の意味条件変更
- interpretation_bucket の meaning 変更

### 性質
- 下流全 consumer に波及しうる
- 破壊的変更を避けるべき

---

## 3.2 L4 bundle change
中くらい。

### 例
- market_summary に field 追加
- liquidity bundle 分割
- alert candidate 補助タグ追加

### 性質
- shared bundle 利用者に波及しうる
- additive なら比較的安全

---

## 3.3 adapter / widget change
軽い。

### 例
- UI key 変更
- widget series 変更
- card 表示構成変更

### 性質
- その consumer の中で閉じやすい
- 最前線の吸収層にすべき

---

## 4. 互換の原則

## 4.1 additive first
基本方針は常に add を優先する。

### 推奨
- field を追加する
- 新しい tag を追加する
- 新しい bundle version を追加する

### 非推奨
- 既存 field を即 rename する
- 既存 field を即 remove する
- 既存 meaning を黙って差し替える

---

## 4.2 deprecate before remove
既存 contract をやめたい場合は、いきなり削除しない。

### 手順
1. 旧 field / old meaning を deprecated 扱いにする
2. 新 field / new bundle を並走させる
3. adapter 層で吸収する
4. 移行が終わってから remove を検討する

---

## 4.3 version the contract
L3 / L4 の変更に備えて、contract version を持てる設計を推奨する。

### 推奨 field 例
- `schema_version`
- `bundle_version`
- `producer_version`
- `meaning_version`

---

## 5. L3 の進化ポリシー

## 5.1 L3 は controlled evolution
L3 は不変ではない。
ただし「正本層」なので、勝手に揺らしてはいけない。

### ルール
- meaning を変える時は理由を明示する
- replay / observation / AI / operator feedback の根拠を持つ
- rename より add / alias を優先する
- old state の互換読み取りを一定期間残す

---

## 5.2 diff / rebuild / continuity は要観測領域
特に次は意味変更が起こりやすい。

- orderbook diff の扱い
- rebuild 精度
- continuity boundary
- trust degradation
- interpretation_bucket の条件

### 扱い
この領域は「将来変わりうるもの」として、最初から互換余地を持たせる。

---

## 5.3 AI / analytics の位置づけ
AI や analytics は L3 を直接勝手に書き換える owner ではない。

### 役割
- 観測
- 仮説生成
- 誤差発見
- candidate proposal

### 決定
L3 meaning の正式変更は、最終的には spec と review で固定する。

つまり、

```text
AI は提案できるが、L3 meaning の正本 owner ではない。
```

---

## 6. L4 の進化ポリシー

## 6.1 L4 shared は contract として育てる
L4 shared bundle は、下流が依存する共有 contract である。

### ルール
- additive first
- existing field を急に消さない
- widget 専用 convenience で shared を汚さない
- breaking 変更は v2 併存で吸収する

---

## 6.2 推奨変更パターン

### 良い例
- `trust_state` を残したまま `trust_detail` を追加
- `notable_events` に tag を追加
- `market_summary_v2` を追加して adapter で切り替える

### 悪い例
- `trust_state` を消して `trust_label` に置換
- widget の都合で bundle を rename する
- field 名だけ変えて rationale を残さない

---

## 7. 変更吸収の前線

## 7.1 adapter は破壊吸収層
consumer adapter は、L3/L4 の変更を consumer ごとに吸収する前線である。

### 役割
- old field / new field を吸収
- alias を吸収
- placeholder を補う
- widget input へ変換する

### 非役割
- meaning を再定義する
- shared truth を書き換える

---

## 7.2 widget / presenter は最終吸収層
表示の breaking はここで閉じる。

### 役割
- graph series shape 変更
- card row shape 変更
- icon / color / layout 変更

### 期待
L3/L4 の本体変更をここまで波及させないのが理想。

---

## 8. 実務判断ルール

### ルール1
事実が変わったのか、意味が変わったのか、束ね方が変わったのかを先に言語化する。

### ルール2
L3 meaning を変えるなら、仕様・根拠・移行をセットで考える。

### ルール3
L4 shared を変えるなら、まず additive で済まないかを考える。

### ルール4
breaking を吸収する第一候補は adapter 層。

### ルール5
AI や分析結果は「変更提案の根拠」にはなるが、そのまま正本変更にはしない。

---

## 9. 変更フローの推奨

### Case A: L3 meaning を見直したい
1. 現象を観測
2. replay / analytics / operator で根拠を集める
3. spec で meaning 変更案を書く
4. old/new 併存設計を作る
5. adapter で吸収する
6. 十分な観測後に旧 contract を落とす

### Case B: L4 bundle を変えたい
1. shared 価値を確認
2. additive で済むなら追加する
3. breaking なら v2 併存
4. adapter 側を先に対応する
5. consumer を順次移行する

---

## 10. 一言でまとめると

```text
L3 は変わりうるが、重く慎重に進化させる。
L4 は additive first で育てる。
breaking は adapter 層で吸収し、widget まで波及させない。
AI は提案者にはなれるが、正本 owner ではない。
```
