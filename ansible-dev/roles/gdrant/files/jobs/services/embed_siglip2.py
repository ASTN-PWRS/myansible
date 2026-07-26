# services/embed_siglip2.py
import subprocess, json

SIGLIP2_CLI = "/usr/local/bin/siglip2-cli"

def embed_image(image_path):
    result = subprocess.check_output([SIGLIP2_CLI, "embed", image_path])
    return json.loads(result)["vector"]
