# services/classify_florence2.py
import subprocess, json

FLORENCE_CLI = "/usr/local/bin/florence2-cli"

def classify_image(image_path):
    result = subprocess.check_output([FLORENCE_CLI, "classify", image_path])
    return json.loads(result)
