from paddleocr import PaddleOCR

class TextOCR:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="japan")

    def extract_text(self, image_path):
        result = self.ocr.ocr(image_path)
        lines = []
        for line in result:
            for box, text in line:
                lines.append({
                    "text": text[0],
                    "bbox": box
                })
        return lines
