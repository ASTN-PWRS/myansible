# services/extract_text.py
import subprocess

def extract_text(pdf_path):
    result = subprocess.check_output(["pdftotext", pdf_path, "-"])
    return result.decode("utf-8")
