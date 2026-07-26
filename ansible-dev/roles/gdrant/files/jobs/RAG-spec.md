
# 📘 **RAG System Architecture — Indexing & Complex Search Workflow Summary**  


---

## # 1. Overview

このドキュメントは、ASAOさんと一緒に設計した **企業向けマルチモーダルRAGシステム**の全体構成をまとめたものです。

このシステムは以下を実現します：

- PDF 文書の **テキスト・画像・OCR・画像分類** をすべてインデックス化  
- Qdrant による **複合検索（AND / OR / NOT / ネスト）**  
- Qwen による **日本語質問 → 論理式(JSON)抽出**  
- Qwen による **検索結果の Markdown 整形（ファイルリンク付き）**  
- PostgreSQL なしでも検索が完結  
- 文書管理をしたい場合のみ PostgreSQL を使用  

---

## # 2. Indexing Workflow

### インデックス対象
- PDF テキスト（pdftotext）
- スキャンPDF → Gemini Vision OCR（plain text）
- PDF 画像（pdf2image）
- 画像分類（Florence2）
- 画像意味ベクトル（SigLIP2）
- テキスト意味ベクトル（Jina v3）

### Qdrant に保存する payload（検索に必要な情報）
```json
{
  "file_id": 42,
  "filename": "試験仕様書_2024.pdf",
  "file_url": "https://docs.example.com/試験仕様書_2024.pdf",
  "page": 12,
  "type": "image",
  "image_type": "table",
  "caption": "CPU usage table",
  "text": "CPU負荷試験の結果..."
}
```

### PostgreSQL の役割（任意）
- 文書カテゴリ  
- 部署  
- 権限管理  
- 文書の物理パス  
- 文書の更新履歴  

検索には不要。

---

## # 3. Complex Search Workflow

### 検索で使うベクトル
- **text** → Jina v3  
- **ocr_text** → Gemini Vision OCR → Jina v3  
- **image** → SigLIP2  

### 検索で使う payload
- image_type（Florence2）  
- caption  
- text  
- filename  
- file_url  
- page  

---

## # 4. Logical Query Parsing (LLM)

### 日本語質問 → 論理式(JSON)  
Qwen 3.5 B9 が担当。

#### system プロンプト（完全版）
```
あなたは企業向け文書検索システムの「検索条件パーサー」です。
ユーザーの日本語の検索要求を読み取り、AND / OR / NOT を使った論理式に変換し、
検索エンジンが実行できる JSON を生成します。

重要なルール:
- 日本語の自然文から論理構造を抽出する
- AND / OR / NOT を使って論理式を構築する
- ネストされた論理式も JSON で表現する
- 曖昧な表現は意味的に最も自然な論理式に変換する
- JSON 以外は出力しない
- JSON のキーは以下のみ使用する:
    - and
    - or
    - not
    - text_query
    - text_query_or
    - image_query
    - image_query_or
    - ocr_query
    - ocr_query_or
    - include_image_types
    - exclude_image_types
```

#### 出力例
```
{
  "and": [
    { "not": [{ "image_query": "犬" }] },
    {
      "and": [
        { "include_image_types": ["table"] },
        { "ocr_query_or": ["CPU", "メモリ"] }
      ]
    },
    { "text_query": "試験" }
  ]
}
```

---

## # 5. Qdrant Complex Search Engine

### AND / NOT → Qdrant filter  
### OR → 複数検索結果のマージ  
### ネスト → JSON をそのまま実行

---

## # 6. Final Answer Formatting (LLM)

### Qwen に渡す整形レイヤー（完全版）

Markdown で返す：

- 文書名（### 見出し）
- ファイルリンク（Markdown）
- ページ番号
- 合致理由（画像分類・OCR・テキスト）
- 抜粋
- 総合評価

#### 出力例

```
### 試験仕様書_2024.pdf
- ページ: 3, 4
- リンク: [試験仕様書_2024.pdf](https://docs.example.com/試験仕様書_2024.pdf)
- 合致理由:
  - Florence2 により「table」と分類された画像が存在
  - Gemini Vision OCR により表内に「CPU」が含まれることを確認
  - テキストに「試験項目」「CPU負荷試験」が含まれる
- 抜粋:
  - 「CPU負荷試験」
- 総合評価: 条件に最も合致しています
```

---

## # 7. 全体アーキテクチャ

```
日本語質問
    ↓（Qwen：論理式抽出）
論理式 JSON
    ↓（search_workflow）
Qdrant 複合検索
    ↓
検索結果 JSON
    ↓（Qwen：Markdown整形）
最終回答
```

---

## # 8. この設計の特徴

- テキスト・画像・OCR・分類を統合した **マルチモーダル検索**  
- AND / OR / NOT / ネストの **複合論理検索**  
- Qwen による **自然文 → 論理式 → Markdown整形**  
- Qdrant による高速検索  
- PostgreSQL なしでも検索が完結  
- 文書管理をしたい場合のみ PostgreSQL を追加  

---

## # 9. 今後の拡張案

- Query Expansion（試験 → test / テスト / 検査）  
- 表構造抽出（Camelot / Tabula）  
- 図面形状検索（DINOv2 / SAM）  
- 数式検索（MathPix）  

---

# 📦 **以上が完全版のまとめドキュメント（Markdown）です。**

ASAOさんはこのままコピーして `.md` として保存すれば、  
チャット枠が切れてもこの設計をいつでも再開できます。

必要なら **PDF 版の構成案** や **GitHub README 用の簡易版** も作れるよ。