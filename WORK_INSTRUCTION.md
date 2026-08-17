# 作業指示書: 行政MCP Phase 0 実機検証

最終更新: 2026-08-17

## 目的

innovaTopiaの記事で紹介された、デジタル庁の「行政手続データ分析 MCP Server」を個人のWindows PCで実際に動かし、記事の説明と公式実装が実機で一致するかを確認する。

この検証が完了するまで、gyosei-navi独自のUI・機能実装には着手しない。

## 参照資料

- innovaTopia記事
  - https://innovatopia.jp/ai/ai-news/116042/
- デジタル庁公式リポジトリ
  - https://github.com/digital-go-jp/administrative-procedures-mcp
- 本リポジトリ内
  - `VALIDATION_PLAN.md`
  - `QandA.md`
  - `FIX_PLAN.md`
  - `memo.md`

## 今回確定した判断

### Q1: 実行前レビューを行う

Step 0で `setup.sh`、`.mcp.json`、そこから起動されるコマンド、主要処理、データ取得先を実行前に確認する。

### Q7: `apcli` は `uv run apcli` に統一する

Windowsでvenvのactivate状態に依存しないよう、検証手順では原則として以下の形式を使う。

```powershell
uv run apcli list
uv run apcli inspect procedures-survey-r6
uv run apcli query procedures-survey-r6 -q 相続 --limit 5
uv run apcli summarize procedures-survey-r6 -g 所管府省庁 -m count
uv run apcli preview
```

### Q8: innovaTopia記事側の主張を先に列挙する

実機検証前に、記事本文から「検証可能な主張」を抽出し、公式README由来の情報と混同しない形で記録する。

最低限、以下を照合対象にする。

1. 約75,000件の行政手続データを扱える
2. MCP経由で自然言語による検索・集計ができる
3. `dataset.yaml` にデータの意味・コード・注意事項を定義している
4. 検索・集計はLLMではなくサーバー側で実行する
5. 出典・品質情報・注意事項を返せる
6. `apcli` でLLMなしに検索・集計できる
7. `apcli preview` でローカルUIを確認できる
8. Chrome内蔵AIを使い、APIキーなしで自然言語操作できる範囲がある
9. 個人環境でセットアップできる
10. Windows環境で追加手順や回避策が必要か

各項目は「記事の主張 / 公式READMEの記載 / 実機結果 / 判定 / 備考」で記録する。

## 作業順序

### 1. 事前確認

`VALIDATION_PLAN.md` のStep 0に従い、追加で `setup.sh`、`.mcp.json`、実行コマンド、データ取得先を確認する。Python / uv / git / Chromeのバージョンを記録する。

### 2. 記事側の検証項目を固定する

innovaTopia記事本文を読み、検証可能な主張を一覧化する。公式READMEの内容を記事の主張として補完しない。

### 3. 公式リポジトリをセットアップする

```powershell
git clone https://github.com/digital-go-jp/administrative-procedures-mcp.git
cd administrative-procedures-mcp
uv sync --extra excel
uv run apcli fetch procedures-survey-r6
```

`setup.sh` を使用する場合は事前レビュー後に使用する。Windowsで問題が出た場合はエラーを記録し、Git BashまたはWSLで再確認する。

### 4. LLMなしでCLIを確認する

```powershell
uv run apcli list
uv run apcli inspect procedures-survey-r6
uv run apcli query procedures-survey-r6 -q 相続 --limit 5
uv run apcli summarize procedures-survey-r6 -g 所管府省庁 -m count
```

同一条件を再実行し、結果が再現することも確認する。

### 5. `dataset.yaml` を確認する

フィールド定義、NULL / 欠損、コード値、computed measures、provenance、notes、quality_summary を確認する。

### 6. MCPの4ツールを確認する

- `list_datasets`
- `inspect_dataset`
- `query_records`
- `summarize_records`

```powershell
uv run apcli describe list_datasets
uv run apcli describe inspect_dataset
uv run apcli describe query_records
uv run apcli describe summarize_records
```

各ツールの入力、出力、エラー、出典情報を記録する。

### 7. APIキーなしの範囲を確認する

```powershell
uv run apcli preview
```

UI起動、データセット探索、Chrome Prompt API / Gemini Nano、APIキーなしの自然言語操作、単純・複雑問い合わせの差を確認する。

### 8. Claude Code等からMCP接続を確認する

`.mcp.json` を事前確認したうえで、可能ならClaude Codeから接続する。

質問例:

```text
厚生労働省が所管する行政手続を検索して
所管府省庁別に手続件数を集計して
相続に関係しそうな行政手続を検索して
オンライン化に関係する項目を使って集計できる？
```

回答文だけでなく、呼び出されたMCPツール、引数、検索・集計の実行主体、出典・注意事項、失敗時の原因を確認する。

## 記録

検証結果は `validation-results.md` に記録する。

最低限、実行日時、環境バージョン、実行コマンド、成否、主要出力、エラー、記事との一致・相違、公式READMEとの一致・相違、回避策を残す。

秘密情報、APIキー、個人情報、勤務先の実データ・社内情報は記録しない。

## 停止条件

以下の場合は独自実装へ進まず、原因と結果を整理して停止する。

- 公式データを取得できない
- データセットを認識できない
- CLI検索または集計を再現できない
- 出典・品質情報を確認できない
- Windows / Git Bash / WSLの範囲で検証を継続できない

## 完了条件

`VALIDATION_PLAN.md` のPhase 0完了条件をすべて満たし、さらに以下を満たす。

- innovaTopia記事の検証可能な主張が一覧化されている
- 各主張について「記事 / 公式README / 実機結果」が区別されている
- 一致 / 一部一致 / 相違 / 未検証の判定が付いている
- Windows固有のハマりどころが記録されている
- APIキーなしで使える範囲が実測で確認されている

（2026-08-17追記）**Phase 0 は未完了である。** 一度は完了としたが、実行証跡の監査（`EVIDENCE_AUDIT.md`）で記録の裏付けが取れず、完了判定を撤回した。

再検証時は、上記の完了条件に加えて次を必須とする。

- 各項目について、実行コマンドとその出力の**原文**を `validation-results.md` に貼る。要約・推測で埋めない
- MCPは「起動 → クライアント接続 → `tools/list` 相当でツール取得 → ツールを1回以上呼び出してレスポンス取得」まで到達し、それぞれのログを残す
- 各ステップで `git --version` / `uv --version` / `python --version` の実出力を併記する
- **検証環境を削除する前にログを保存する**

完了後、実測結果をもとに最初のnote記事を作成する。

## 禁止事項

- Phase 0完了前にgyosei-navi独自UIを作り始めない
- 記事の主張を公式READMEの記載で勝手に補完しない
- 実行結果を推測で埋めない
- 出所不明の `dataset.yaml` に `apcli fetch` / `apcli add` を実行しない
- 個人情報、勤務先の実データ、社内情報、顧客情報、非公開資料を公開用検証に使わない
