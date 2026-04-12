from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR
import cv2
import numpy as np

# PaddleOCR（日本語）
ocr_engine = PaddleOCR(use_angle_cls=True, lang="japan")


def pdf_to_images(pdf_bytes: bytes):
    """
    PDF をページ単位の PIL.Image リストに変換
    """
    return convert_from_bytes(pdf_bytes)


def image_to_text(image):
    """
    1ページ分の画像から OCR テキストを抽出
    """
    # PIL → OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    result = ocr_engine.ocr(img, cls=True)

    if not result or not result[0]:
        return ""

    # 抽出されたテキストを結合
    lines = [line[1][0] for line in result[0]]
    return "\n".join(lines)


def pdf_ocr(pdf_bytes: bytes):
    """
    PDF 全ページを OCR して
    [ {page:1, text:"..."}, {page:2, text:"..."} ] の形式で返す
    """
    pages = pdf_to_images(pdf_bytes)
    results = []

    for i, page in enumerate(pages, start=1):
        text = image_to_text(page)
        results.append({
            "page": i,
            "text": text
        })

    return results
