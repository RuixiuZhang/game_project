import os
from dotenv import load_dotenv

load_dotenv()

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = os.getenv("DIFY_API_URL")

if not DIFY_API_KEY or not DIFY_API_URL:
    raise RuntimeError("❌ DIFY_API_KEY 或 DIFY_API_URL 未正确加载")
