# services/llm_qwen.py

# Qwen Markdown 整形レイヤー
from qwen import QwenClient  # 仮のクライアント名。あなたの環境に合わせて変更。

client = QwenClient(api_key="YOUR_API_KEY")


def summarize_with_qwen(results_json, original_query):
    prompt = f"""
あなたは企業向け文書検索システムの回答整形AIです。
以下は検索エンジン(Qdrant)から返された検索結果のJSONです。
これを読み取り、ユーザーの検索要求に合致した理由を説明し、
Markdown形式でわかりやすく整理して出力してください。

検索要求:
{original_query}

出力ルール:
- 文書ごとにセクションを作る
- 文書名は Markdown の見出し (###) にする
- ファイルリンクは Markdown のリンク形式で出す
  例: [試験仕様書_2024.pdf](https://docs.example.com/試験仕様書_2024.pdf)
- ページ番号を列挙する
- 合致した理由を箇条書きで説明する
- OCRテキストや本文の抜粋を適度に含める
- 画像分類(image_type)やcaptionがある場合は説明に含める
- 最後に「総合評価」を一言でまとめる

検索結果(JSON):
{results_json}

Markdown形式で出力してください。
"""

    response = client.generate(prompt)
    return response.text
