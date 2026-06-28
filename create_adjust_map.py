import json
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="japan", use_angle_cls=True)

mapping = {}

for pdf in ["pdf_MSMincho.pdf", "pdf_MSGothic.pdf", "pdf_Meiryo.pdf"]:
    result = ocr.ocr(pdf, cls=True)

    for line in result:
        rec = line[1][0]  # 認識文字列
        # PDFは1文字ずつなので rec は1文字のはず
        # 正解は PDF生成時の順番で対応させる
        # ここは実装次第で調整

        # 誤認識だけ記録
        if rec != expected_char:
            mapping.setdefault(expected_char, set()).add(rec)

json.dump(mapping, open("mapping_pdf.json", "w"), ensure_ascii=False, indent=2)
