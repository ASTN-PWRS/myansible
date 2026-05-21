import os
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

def create_diagonal_watermark(
    width,
    height,
    text,
    font_path,
    color=(0, 0, 0),
    alpha=80,
    diag_ratio=0.9,
):
    import math, os, numpy as np, cv2
    from PIL import Image, ImageDraw, ImageFont

    diag = math.sqrt(width**2 + height**2)
    target_width = diag * diag_ratio

    approx_font_size = int(target_width / max(len(text.replace("\n", "")), 1))
    font_size = max(10, approx_font_size)
    font = ImageFont.truetype(font_path, font_size)

    dummy = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy)
    while True:
        bbox = draw.textbbox((0, 0), text.replace("\n", ""), font=font)
        text_w = bbox[2] - bbox[0]
        if text_w >= target_width:
            break
        font_size += 2
        font = ImageFont.truetype(font_path, font_size)

    # --- 改行対応: 各行の高さを積み上げる ---
    lines = text.split("\n")
    line_spacing = int(font_size * 0.3)
    line_heights = []
    max_w = 0
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        max_w = max(max_w, w)
        total_h += h + line_spacing

    pad = 100
    base_w = max_w + pad * 2
    base_h = total_h + pad * 2

    text_img = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(text_img)

    # --- 各行を中央揃えで描画 ---
    y = (base_h - total_h) / 2
    for line, h in zip(lines, line_heights):
        bbox = draw2.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (base_w - w) / 2
        draw2.text((x, y), line, font=font, fill=(color[0], color[1], color[2], alpha))
        y += h + line_spacing

    # --- OpenCVで高品質回転 ---
    cv_img = cv2.cvtColor(np.array(text_img), cv2.COLOR_RGBA2BGRA)
    h, w = cv_img.shape[:2]
    cx, cy = w / 2, h / 2
    angle = math.degrees(math.atan2(height, width))
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    ones = np.ones((4, 1), dtype=np.float32)
    corners_hom = np.hstack([corners, ones])
    rotated_corners = corners_hom @ M.T
    min_x, max_x = np.min(rotated_corners[:, 0]), np.max(rotated_corners[:, 0])
    min_y, max_y = np.min(rotated_corners[:, 1]), np.max(rotated_corners[:, 1])
    new_w, new_h = int(max_x - min_x), int(max_y - min_y)
    M[0, 2] -= min_x
    M[1, 2] -= min_y

    rotated = cv2.warpAffine(
        cv_img,
        M,
        (new_w, new_h),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )

    rotated_pil = Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGRA2RGBA))

    # --- 中央トリミング ---
    rw, rh = rotated_pil.size
    cx, cy = rw // 2, rh // 2
    left = cx - width // 2
    top = cy - height // 2
    cropped = rotated_pil.crop((left, top, left + width, top + height))

    return cropped


wm = create_diagonal_watermark(
    width=800,
    height=600,
    text="CONFIDENTIAL\n Dont copy",
    font_path="RobotoSlab-VariableFont_wght.ttf",
    color=(255, 0, 0),
    alpha=120,
)

wm.save("watermark.png")
