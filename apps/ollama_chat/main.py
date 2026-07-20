

# ---- 実行例 ----

messages = [
    {
        "role": "system",
        "content": """
<|system|>
あなたは有能な AI assistant です。
必要なら function call を返します。
返すときは JSON のみで返してください。
"""
    },
    {
        "role": "user",
        "content": "文書一覧を見せて"
    }
]

# 1. LLM に問い合わせ
response = safe_chat(messages, tools)

# LLM 通信エラー
if "error" in response:
    print(response["error"])
    exit()

# function call が無い場合（LLM が文章回答した）
if not response.message.tool_calls:
    print("LLM returned text:", response.message.content)
    exit()

# 2. function call を取り出す
call = response.message.tool_calls[0]
fn = call.function.name
args = call.function.arguments or {}

# 3. Python の function を実行（例外処理付き）
if fn not in tool_map:
    result = json.dumps({"error": f"Unknown function: {fn}"})
else:
    try:
        result = tool_map[fn](**args)
    except Exception as e:
        result = json.dumps({"error": str(e)})

# 4. LLM に結果を返して最終回答を生成
messages.append({
    "role": "assistant",
    "tool_calls": response.message.tool_calls
})

messages.append({
    "role": "tool",
    "tool_name": fn,
    "content": result
})

final = safe_chat(messages, tools)

if "error" in final:
    print(final["error"])
else:
    print(final.message.content)
