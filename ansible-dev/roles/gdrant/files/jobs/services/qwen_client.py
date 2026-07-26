# services/qwen_client.py

import requests

QWEN_API_URL = "http://localhost:8000/v1/chat/completions"  # 例：Ollama互換API

def call_qwen(prompt: str, stream: bool = True):
    """
    Qwen にプロンプトを投げて回答を取得する。
    stream=True の場合はストリーミングで返す。
    """

    payload = {
        "model": "qwen2.5-7b-instruct",
        "stream": stream,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(QWEN_API_URL, json=payload, stream=stream)

    # ストリーミング
    if stream:
        collected = ""
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = line.decode("utf-8")
                if data.startswith("data: "):
                    obj = json.loads(data.replace("data: ", ""))
                    delta = obj.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        collected += content
                        yield content  # ★ ここがストリーミング
            except Exception:
                continue
        return

    # 非ストリーミング
    obj = response.json()
    return obj["choices"][0]["message"]["content"]
