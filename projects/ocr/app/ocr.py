# app/ocr.py
import cv2
import numpy as np
from paddleocr import PaddleOCR

ocr_engine = PaddleOCR(lang="japan", use_angle_cls=True)

def preprocess_image(pil_image):
    img = np.array(pil_image)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, img_bin = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    return cv2.cvtColor(img_bin, cv2.COLOR_GRAY2BGR)

def run_ocr(img_bgr):
    result = ocr_engine.ocr(img_bgr, cls=True)
    lines = []
    for line in result:
        for box, (txt, conf) in line:
            lines.append(txt)
    return "\n".join(lines)
