import json
import sys

MODEL_PATH = "/opt/models/bge-m3/current"

def main():
    if sys.stdin.isatty():
        print("stdin required", file=sys.stderr)
        sys.exit(101)

    text = sys.stdin.read().strip()

    if not text:
        print("empty input", file=sys.stderr)
        sys.exit(102)

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_PATH)

    vec = model.encode(
        text,
        normalize_embeddings=True,
    ).tolist()

    print(json.dumps(vec))

if __name__ == "__main__":
    main()