import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np
import cv2

def pdf_to_images(pdf_path, dpi=300):
    doc = fitz.open(pdf_path)
    images = []

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")

        # PIL で読み込み
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # numpy に変換（RGB）
        np_img = np.array(pil_img)

        # BGR に変換（PaddleOCR が期待する形式）
        np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        images.append(np_img)

    return images
