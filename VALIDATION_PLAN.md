# 行政手続データ分析 MCP Server 検証実行計画

最終更新: 2026-08-17

## 1. 目的

innovaTopiaの記事で紹介された、デジタル庁の「行政手続データ分析 MCP Server」を個人のWindows PCで再現し、記事と公式実装の説明が実機で一致するかを確認する。

この検証が完了するまで、gyosei-navi 独自のUIや機能は実装しない。

## 2. 対象と前提

- 参照記事: https://innovatopia.jp/ai/ai-news/116042/
- 公式リポジトリ: https://github.com/digital-go-jp/administrative-procedures-mcp（MIT License）
- 公式リポジトリのclone先: C:\\PROJECT\\administrative-procedures-mcp
- 対象データセット: procedures-survey-r6（データ本体はリポジトリ非同梱。apcli fetch がデジタル庁の配布ページ https://www.digital.go.jp/resources/procedures-survey-results から取得しParquet化する）
- 想定データ量: 約75,000件
- 検証環境: Windows。setup.sh が動かない場合はWSLまたはGit Bashを使用する。
- 公式要件（README記載の前提バージョン。Step 0で実環境と突き合わせる）
  - Python 3.10+
  - uv（推奨。手動セットアップも可）
  - FastMCP 3.2+（既定はMCP仕様 2025-11-25。2026-07-28版はFastMCP 4系プレリリースの追加インストールが別途必要。本検証で2026-07-28版も対象に含めるかはQ6参照）
  - Chromeの内蔵AI（Prompt API）を試す場合: Chrome 138+ または Edge Canary/Dev 138.0.3309.2+

## 3. 記録方法

各検証項目について、validation-results.md などの作業記録に残す。

- 実行日時
- 実行環境（OS、Python、uv、Chromeのバージョン）
- 実行コマンド
- 成否
- 主要な出力（件数、エラー、警告）
- 公式README・記事との一致点／相違点
- 画面確認が必要な項目のスクリーンショットまたはURL

秘密情報や個人情報は記録・公開しない。APIキーを使用した場合も値は保存しない。

## 4. 実行手順

### Step 0: 事前確認

- [ ] innovaTopia記事と公式READMEを読む
- [ ] git、python、uv の有無とバージョンを確認する
- [ ] C:\\PROJECT 配下に十分な空き容量があることを確認する
- [ ] 公式リポジトリのライセンス、データ出典、利用条件を確認する

確認コマンド例:

```powershell
git --version
python --version
uv --version
```

公式READMEでは `dataset.yaml` を信頼済みの設定ファイルとして扱うことを前提としており、出所不明のYAMLに対して `apcli fetch` / `apcli add` を実行しないよう注意書きがある。本検証では公式リポジトリ同梱の `dataset.yaml`（procedures-survey-r6）のみを対象とし、内容を差し替えない。

### Step 1: 公式リポジトリのセットアップ

```bash
git clone https://github.com/digital-go-jp/administrative-procedures-mcp.git
cd administrative-procedures-mcp
./setup.sh
```

Windowsで失敗した場合:

1. エラー全文を保存する
2. WSLまたはGit Bashで再実行する
3. それでも失敗する場合は、公式READMEの手動手順へ切り替える

手動手順:

```bash
uv sync --extra excel
apcli fetch procedures-survey-r6
```

確認:

- [ ] 依存関係のセットアップに成功した
- [ ] procedures-survey-r6 の取得に成功した
- [ ] データ取得、Parquet変換、インデックス作成等で致命的エラーがない
- [ ] Windows固有の問題と回避策を記録した

### Step 2: LLMなしでCLIを検証

次の順に実行する。前の確認が失敗した場合は、原因を記録してから停止する。

```bash
apcli list
apcli inspect procedures-survey-r6
apcli query procedures-survey-r6 -q 相続 --limit 5
apcli summarize procedures-survey-r6 -g 所管府省庁 -m count
```

確認:

- [ ] データセットが一覧に表示される
- [ ] inspect でスキーマ、件数、品質情報、出典を確認できる
- [ ] 日本語の「相続」検索が実行できる
- [ ] 検索結果が最大5件に制限される
- [ ] 所管府省庁別の件数集計が実行できる
- [ ] 同じ条件で再実行したとき結果が再現する
- [ ] 集計をLLMではなくCLI／サーバー側コードが実行していることを確認する

### Step 3: dataset.yaml の設計を確認

公式リポジトリ内の dataset.yaml を読み、次を項目ごとに記録する。

- [ ] 各フィールドの意味、型、表示名
- [ ] NULL・欠損値の意味
- [ ] コード値とその説明
- [ ] computed measures の定義と計算方法
- [ ] provenance、notes、quality_summary の扱い
- [ ] 検索・集計結果へ出典と注意事項が付く仕組み

検証の観点は、「AIの推論精度を上げる」ことではなく、間違いやすい検索・計算を決定論的なサーバー側処理へ移していることが実装上確認できるかとする。

### Step 4: MCPの4ツールを確認

公式実装の次のツールを特定し、各ツールの入力、出力、エラー、出典情報を記録する。

1. list_datasets
2. inspect_dataset
3. query_records
4. summarize_records

```text
利用者の質問
  → LLMが意図を解釈
  → MCPツールを選択
  → サーバー側コードが検索・集計
  → 構造化結果を返す
  → LLMが人間向けに説明
```

各ツールの入出力定義は `apcli describe <ツール名>` で個別に確認できる（例: `apcli describe query_records`）。

確認:

- [ ] 4ツールが利用可能である
- [ ] 各ツールの引数が確認できる（`apcli describe` の出力を記録する）
- [ ] 検索・集計がLLMの手計算になっていない
- [ ] 構造化された結果が返る
- [ ] 出典、品質情報、注意事項が結果に含まれる

（任意・HTTPモードで起動した場合のみ）`/health` の `mcp_protocol_version` で応答中のMCP仕様バージョンを確認できる（既定は2025-11-25）。ただしStep 6のClaude Code接続は `.mcp.json` によるstdio接続のため `/health` は対象外。stdio側で仕様バージョンを確認する方法は未確認（Q7参照）。

### Step 5: apcli preview とAPIキーなし利用を確認

```bash
apcli preview
```

既定URL http://127.0.0.1:8765/ をブラウザで開く。

確認:

- [ ] UIが起動する
- [ ] データセットの表示・検索ができる
- [ ] ChromeのPrompt API／Gemini Nanoの利用可否を確認した
- [ ] APIキーなしで自然言語操作できる範囲を確認した
- [ ] 単純な検索と複雑な検索の結果差を記録した
- [ ] 必要なChromeバージョン、設定、制約を記録した

### Step 6: MCPクライアントから接続

可能な環境では、公式リポジトリの .mcp.json を使ってClaude Code等から接続する。

次の質問を順に試す。

```text
厚生労働省が所管する行政手続を検索して
所管府省庁別に手続件数を集計して
相続に関係しそうな行政手続を検索して
オンライン化に関係する項目を使って集計できる？
```

回答文だけでなく、次を確認する。

- [ ] 呼び出されたMCPツール名
- [ ] 渡された引数
- [ ] 検索・集計の実行主体
- [ ] 出典・注意事項が最終回答に反映されるか
- [ ] 失敗時のエラー内容と原因

接続できない場合は、利用できない理由、試した設定、代替確認（CLIやMCPの直接テスト）を記録して完了条件の判定対象にする。

## 5. 完了判定

次の全項目を満たした時点でPhase 0を完了とする。

- [ ] 公式リポジトリをcloneできた
- [ ] セットアップできた
- [ ] procedures-survey-r6を取得できた
- [ ] apcli list が動いた
- [ ] apcli inspect が動いた
- [ ] apcli query で日本語検索できた
- [ ] apcli summarize で集計できた
- [ ] dataset.yaml の設計を確認した
- [ ] MCPの4ツールを確認した
- [ ] apcli preview を試した
- [ ] APIキーなしで使える範囲を確認した
- [ ] MCP対応AIから呼び出した、または利用できない理由を記録した
- [ ] 記事の説明と実機結果の一致・相違を整理した

## 6. 停止条件と次の判断

次の場合は独自機能の設計へ進まず、調査結果を整理して停止する。

- 公式データを取得できない
- データセットを認識できない
- CLIの検索または集計が再現できない
- 出典・品質情報の扱いを確認できない
- Windows固有の問題が未解決で、代替環境でも検証できない

Phase 0完了後に、次の順でPhase 1を判断する。

1. 実測結果を元にnote記事の構成を作る
2. 一般利用者向けUIの価値を評価する
3. 引っ越し、結婚、出産、相続、退職の検索が公式データだけで成立するか確認する
4. 静的サイト、Parquet + DuckDB-Wasm、Chrome内蔵AI、MCP公開の必要性を比較する
5. 方針が確定してから gyosei-navi の実装計画を作る

## 7. 公開時のルール

- 政府・自治体等の正式公開データ、オープンデータ、公開API、完全なダミーデータのみを使用する
- 個人情報、勤務先の実データ、社内情報、顧客情報、非公開資料を使用しない
- 公開許可が確認できない業務データをサンプルやデモに転用しない
- 記事や検証結果には、公式データの出典、取得日時、制約、未検証事項を明記する

