from docx import Document
from PIL import Image
from io import BytesIO
import os

def extract_images_from_docx(docx_path, out_dir):
  doc = Document(docx_path)
  os.makedirs(out_dir, exist_ok=True)

  images = []
  for i, rel in enumerate(doc.part.rels.values()):
    if "image" in rel.target_ref:
      img_data = rel.target_part.blob
      img = Image.open(BytesIO(img_data))
      out_path = os.path.join(out_dir, f"image_{i}.png")
      img.save(out_path)
      images.append(out_path)

  return images
