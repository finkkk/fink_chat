from openai import OpenAI
from config import SYSTEM_USERNAME, AI_API_KEY, AI_MODEL, AI_API_URL, AI_MAX_TOKENS

# AI调用方法(无上下文)
client = OpenAI(api_key=AI_API_KEY, base_url=AI_API_URL)


# ====== 指令处理函数 ======


# 无上下文 单个用户提问AI指令
def cmd_ask(username, args):
    if not args:
        return {
            "username": SYSTEM_USERNAME,
            "message": "⚠️ 格式：/ask 你想问的内容",
            "style": "error"
        }

    prompt = " ".join(args)
    messages = [
        {"role": "system", "content": "你是一个乐于助人而且幽默的 AI 助手"},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            max_tokens=AI_MAX_TOKENS
        )
        return {
            "username": SYSTEM_USERNAME,
             "message": f"🤖{response.choices[0].message.content}",  # 添加AI徽章
            "role": "system"
        }
    except Exception as e:
        return {
            "username": SYSTEM_USERNAME,
            "message": f"❌ AI 调用失败：{str(e)}",
            "style": "error",
            "role": "system"
        }
    

# ====== 指令注册字典 ======


AI_COMMANDS = {
    "/ask": {
        "desc": f"调用 AI 提问（模型: {AI_MODEL}，不读上下文，最多 {AI_MAX_TOKENS} tokens）",
        "func": cmd_ask,
        "broadcast": True,
        "save": True,
        "permission": ["user", "admin", "super_admin"],
    },
}