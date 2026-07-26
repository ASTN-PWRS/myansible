# services/extract_images.py
from pdf2image import convert_from_path
import os

def extract_images(pdf_path):
    out_dir = f"/tmp/extracted_{os.path.basename(pdf_path)}"
    os.makedirs(out_dir, exist_ok=True)

    pages = convert_from_path(pdf_path, dpi=200)
    results = []

    for idx, page in enumerate(pages):
        out_path = f"{out_dir}/page_{idx}.png"
        page.save(out_path, "PNG")
        results.append((idx, out_path))

    return results
