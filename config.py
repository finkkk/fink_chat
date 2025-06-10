# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 配置


# ===== APP 配置 =====
APP_VERSION = "v1.0.5"
APP_UPDATED = "2025-06-09"


# ===== AI 配置 =====
AI_API_KEY = os.getenv("AI_API_KEY")  # DeepSeek 的 API 密钥
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
AI_API_URL = os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions")
# 限制类参数
AI_CONTEXT_COUNT = int(os.getenv("AI_CONTEXT_COUNT", 5))     # 上下文条数
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 1000))        # 最大 token 限额


# ===== 身份管理配置 =====
GUEST_USERNAME = "游客"
SYSTEM_USERNAME = "波特"
ADMIN_USERNAMES = ["zaoyuuw","飞飞"]
SUPER_ADMIN_USERNAMES = ["finkkk"]