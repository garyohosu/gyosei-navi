# gyosei-navi 開発メモ

最終更新: 2026-08-17

## このリポジトリを作った直接のきっかけ

まず最初にやることは、新しい行政サービスを作ることではない。

**innovaTopia の記事で紹介されている、デジタル庁の「行政手続データ分析 MCP Server」を個人のPCで実際に動かし、記事の内容を再現・検証する。**

これが本リポジトリの最初の目的。

### 起点となった記事

- innovaTopia
  - https://innovatopia.jp/ai/ai-news/116042/

### 検証対象の公式リポジトリ

- デジタル庁 `administrative-procedures-mcp`
  - https://github.com/digital-go-jp/administrative-procedures-mcp
  - clone: `https://github.com/digital-go-jp/administrative-procedures-mcp.git`

公式READMEでは、デジタル庁が公表する「行政手続等の棚卸調査結果」約75,000件を検索・集計できるMCPサーバーとして公開されている。

主な特徴は次のとおり。

- `dataset.yaml` でデータの意味・コード・注意事項を定義する
- 生データの計算をLLMに任せず、検索・集計をサーバー側で実行する
- 出典、品質情報、注意事項をツール応答に含める
- MCP対応クライアントから自然言語で利用できる
- LLMなしでも `apcli` から検索・集計できる
- `apcli preview` でローカルUIを確認できる

---

# Phase 0: 記事の内容をそのまま動作確認する

**ここが最優先。gyosei-navi 独自機能の開発は、この確認が終わってから。**

## 0-1. 公式リポジトリを取得

```bash
git clone https://github.com/digital-go-jp/administrative-procedures-mcp.git
cd administrative-procedures-mcp
./setup.sh
```

Windows環境で `setup.sh` がそのまま実行できない場合は、WSL / Git Bash / 公式READMEの手動手順を確認する。

公式READMEの手動例:

```bash
uv sync --extra excel
apcli fetch procedures-survey-r6
```

確認項目:

- Pythonバージョン
- `uv` の有無
- セットアップ成功/失敗
- 行政手続データの取得成功/失敗
- Parquet変換成功/失敗
- 実行時のエラーやWindows固有の問題

## 0-2. LLMなしでCLIを確認

まずAIを介さず、データそのものが正しく扱えることを確認する。

```bash
apcli list
apcli inspect procedures-survey-r6
apcli query procedures-survey-r6 -q 相続 --limit 5
apcli summarize procedures-survey-r6 -g 所管府省庁 -m count
```

ここで確認すること:

- データセットが認識されるか
- 約75,000件のデータを扱えるか
- 日本語検索が動くか
- 所管府省庁などで集計できるか
- `inspect` でデータ構造・品質情報を確認できるか
- 集計結果が再現可能か

## 0-3. `dataset.yaml` を読む

記事の重要ポイントなので、単に動かすだけで終わらせない。

確認すること:

- 各フィールドの意味をどう定義しているか
- NULL / 欠損の意味がどう記述されているか
- コード値をどう説明しているか
- computed measures がどう定義されているか
- provenance / notes / quality_summary がどう扱われるか

**「AIを賢くして間違いを減らす」のではなく、「AIが間違いやすい計算を決定論的なコード側へ移す」設計を実コードで確認する。**

## 0-4. MCPの4ツールを確認

公式実装の中心となるツール:

1. `list_datasets`
2. `inspect_dataset`
3. `query_records`
4. `summarize_records`

確認したい流れ:

```text
利用者の質問
   ↓
LLMが意図を解釈
   ↓
MCPツールを選択
   ↓
検索・集計は通常のコードで実行
   ↓
構造化された結果
   ↓
LLMが人間向けに説明
```

## 0-5. APIキーなしの動作確認

公式READMEでは `apcli` はLLM不要で動く。

さらに、次を確認する。

```bash
apcli preview
```

既定:

```text
http://127.0.0.1:8765/
```

ChromeのPrompt API / Gemini Nanoが利用可能な環境では、外部AI APIキーなしで自然言語操作を試す。

確認項目:

- UI自体は起動するか
- Chrome内蔵AIが利用可能か
- APIキーなしで自然言語検索できるか
- 単純な検索と複雑な検索で結果に差があるか
- 対応Chromeバージョンや設定条件は何か

## 0-6. MCPクライアント接続を確認

可能なら Claude Code 等から公式MCPへ接続する。

公式リポジトリには `.mcp.json` が含まれており、Claude Codeではクローンしたディレクトリから起動する構成が用意されている。

確認したい質問例:

```text
厚生労働省が所管する行政手続を検索して
```

```text
所管府省庁別に手続件数を集計して
```

```text
相続に関係しそうな行政手続を検索して
```

```text
オンライン化に関係する項目を使って集計できる？
```

重要なのは回答文だけではなく、

- どのMCPツールを呼んだか
- どんな引数を渡したか
- 集計をLLM自身が行っていないか
- 出典・注意事項が回答に反映されるか

を見ること。

---

# Phase 0 の完了条件

以下を満たしたら「記事の動作確認完了」とする。

- [ ] 公式リポジトリをローカルにcloneできた
- [ ] セットアップできた
- [ ] `procedures-survey-r6` を取得できた
- [ ] `apcli list` が動いた
- [ ] `apcli inspect` が動いた
- [ ] `apcli query` で日本語検索できた
- [ ] `apcli summarize` で集計できた
- [ ] `dataset.yaml` の設計を確認した
- [ ] MCPの4ツールを確認した
- [ ] `apcli preview` を試した
- [ ] APIキーなしでどこまで使えるか確認した
- [ ] MCP対応AIから実際に呼び出してみた、または利用できない理由を記録した
- [ ] innovaTopia記事の説明と実機結果の一致・相違を整理した

この結果を最初のnote記事の材料にする。

---

# 最初のnote記事

仮タイトル:

**「デジタル庁が公開した行政MCPを自宅PCで本当に動かしてみた」**

記事では以下を実測ベースで書く。

1. innovaTopiaの記事を読んだきっかけ
2. 公式GitHubは本当に個人で動かせるのか
3. セットアップ手順
4. APIキーは必要か
5. 約75,000件の行政データを実際に検索
6. 集計をAIではなくMCPサーバー側で行う仕組み
7. `dataset.yaml` の意味
8. MCPの4ツール
9. Chrome内蔵AIでどこまで動くか
10. 記事どおりだった点 / 違った点 / ハマった点
11. 一般の人向けに応用すると何が作れそうか

**先に結論を決めず、実際の動作結果を書く。**

---

# Phase 1: 動作確認後に gyosei-navi の方向を考える

公式MCPの検証が終わってから、一般利用者向けの応用を考える。

現時点の候補は「人生イベントから関連しそうな行政手続を探すナビ」。

候補イベント:

1. 引っ越し
2. 結婚
3. 出産
4. 相続
5. 退職

ただし、これは **Phase 0 の結果を見てから設計する**。

公式データだけで十分な検索ができなければ、無理にこの方向へ進めない。

---

# 公開時の重要ルール

このリポジトリは一般公開を前提とする。

使用してよいもの:

- 政府・自治体等が正式に公開しているデータ
- オープンデータ
- 公開API
- 完全なダミーデータ

使用しないもの:

- 個人情報
- 勤務先の実データ
- 社内情報
- 顧客情報
- 非公開資料
- 公開許可が確認できない業務データ

仕事の実データをサンプルやデモに転用しない。

---

# 将来の検討事項

Phase 0完了後に検討する。

- 一般利用者向けUIを作る価値があるか
- GitHub Pagesのような静的サイトへ移植できるか
- Parquet + DuckDB-Wasm でブラウザ完結できるか
- Chrome内蔵AIを利用したAPIキー不要版が現実的か
- MCPサーバーを公開する必要が本当にあるか
- 人生イベント検索が元データだけで成立するか
- 公式情報へのリンクをどこまで付与できるか

## 現在地

```text
[いまここ]
innovaTopiaの記事を読む
        ↓
公式 行政手続MCPをローカルで再現
        ↓
記事の内容を実機検証
        ↓
note 第1回
        ↓
一般向けの用途を評価
        ↓
gyosei-navi の実装方針を決める
```

**まだ「行政手続ナビを作る」段階ではない。まず公式MCPを動かす。**
