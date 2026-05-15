import fitz
import io
import cv2
import numpy as np
from PIL import Image

def change_opacity(img Image.Image, opacity float) - Image.Image
    img = img.convert(RGBA)
    r, g, b, a = img.split()
    a = a.point(lambda v int(v  opacity))
    return Image.merge(RGBA, (r, g, b, a))


def pdf_to_images(pdf_path, dpi=300, thumb_short=640, wm_path=None, opacity=0.4)
    doc = fitz.open(pdf_path)
    images = []

    # 透かし画像を事前ロード（毎回読み込むと遅い）
    wm_img = None
    if wm_path
        wm_img = Image.open(wm_path).convert(RGBA)

    for i, page in enumerate(doc)
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes(png)

        # PIL で読み込み
        pil_img = Image.open(io.BytesIO(img_bytes)).convert(RGB)

        # -----------------------------
        # ① サムネイル生成（短辺 640px）
        # -----------------------------
        w, h = pil_img.size
        short = min(w, h)
        scale = thumb_short  short
        new_size = (int(w  scale), int(h  scale))

        thumb = pil_img.resize(new_size, Image.LANCZOS).convert(RGBA)

        # -----------------------------
        # ② 透かし合成
        # -----------------------------
        if wm_img
            # 透かしをサムネイルに合わせて縮小
            tw, th = wm_img.size
            ratio = (thumb_short  0.25)  max(tw, th)  # 透かしは短辺の25%くらい
            wm_resized = wm_img.resize(
                (int(tw  ratio), int(th  ratio)),
                Image.LANCZOS
            )

            # CSS の opacity 的な透過
            wm_resized = change_opacity(wm_resized, opacity)

            # 右下に配置
            x = thumb.width - wm_resized.width - 20
            y = thumb.height - wm_resized.height - 20

            thumb.alpha_composite(wm_resized, dest=(x, y))

        # -----------------------------
        # ③ WebP で保存
        # -----------------------------
        thumb.save(fthumb_{i+1}.webp, format=WEBP, quality=90)

        # -----------------------------
        # ④ OCR 用 numpy(BGR) を返す
        # -----------------------------
        np_img = np.array(pil_img)
        np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        images.append(np_img)

    return images
