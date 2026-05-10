import cv2
import numpy as np

class MixedImageToMarkdown:
    def __init__(self):
        self.table = TableTransformer()
        self.text = TextOCR()

    def convert(self, image_path):
        img = cv2.imread(image_path)
        h, w = img.shape[:2]

        # 1. テーブル検出（Table Transformer は表領域を返さないため、画像全体を表と仮定）
        # → 画像内に表がない場合は例外になるので try で処理
        table_md = None
        try:
            table_md = self.table.extract_table_markdown(image_path)
        except:
            table_md = None

        # 2. テキスト OCR
        text_items = self.text.extract_text(image_path)

        # 3. bbox の y 座標でソート
        text_items = sorted(text_items, key=lambda x: x["bbox"][0][1])

        md_parts = []

        # 4. テーブルがある場合は先に挿入
        if table_md:
            md_parts.append(table_md)

        # 5. テキストを追加
        for t in text_items:
            md_parts.append(t["text"])

        return "\n\n".join(md_parts)
