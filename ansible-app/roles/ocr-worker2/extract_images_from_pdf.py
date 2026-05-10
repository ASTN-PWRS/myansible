import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, out_dir):
  os.makedirs(out_dir, exist_ok=True)
  doc = fitz.open(pdf_path)

  images = []
  for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    out_path = os.path.join(out_dir, f"page_{i}.png")
    pix.save(out_path)
    images.append(out_path)

  return images
