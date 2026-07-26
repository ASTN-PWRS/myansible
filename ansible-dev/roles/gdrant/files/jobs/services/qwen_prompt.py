# services/qwen_prompt.py

def build_qwen_prompt(docs, query):
    """
    Qwen に渡す整形プロンプト（最適化版）
    - 文書単位で統合
    - Markdown画像 / PDF画像を自然に説明
    - 見出しを使って構造化
    """

    lines = []
    lines.append("あなたは企業向け検索システムのアシスタントです。")
    lines.append("以下は検索結果です。質問に最も関連する内容を統合して説明してください。")
    lines.append(f"\n質問: {query}\n")

    for doc in docs:
        lines.append("------------------------------------------------------------")
        lines.append(f"■ 文書名: {doc['filename']}")
        lines.append(f"URL: {doc['file_url']}")

        # 見出し（Markdown）
        if doc.get("headings"):
            lines.append("\n● 見出し（Markdown）:")
            for h in doc["headings"]:
                lines.append(f"- {h}")

        # テキスト抜粋
        if doc.get("texts"):
            lines.append("\n● テキスト抜粋:")
            for t in doc["texts"][:3]:
                lines.append(f"- {t[:200]}...")

        # 画像（PDF + Markdown）
        if doc.get("captions") or doc.get("image_types"):
            lines.append("\n● 画像情報:")
            for caption, img_type in zip(doc.get("captions", []), doc.get("image_types", [])):
                lines.append(f"- 種類: {img_type}, 説明: {caption}")

        # ページ情報
        if doc.get("pages"):
            pages = sorted(set([p for p in doc["pages"] if p is not None]))
            if pages:
                lines.append("\n● 該当ページ:")
                lines.append(f"- {pages}")

        # スコア
        if doc.get("scores"):
            lines.append(f"\n● スコア: {max(doc['scores']):.4f}")

    lines.append("\n---\n")
    lines.append(
        "上記を踏まえて、質問に対する最適な回答を作成してください。\n"
        "Markdown画像が含まれる場合は、画像の説明（caption）と種類（image_type）を自然に文章に統合してください。\n"
        "PDF画像とMarkdown画像は区別せず、内容に基づいて説明してください。\n"
        "必要に応じて見出しを使って文書の構造を説明しても構いません。\n"
        "回答は簡潔で、要点をまとめてください。"
    )

    return "\n".join(lines)
