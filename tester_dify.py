from dotenv import load_dotenv
load_dotenv()

import os
import requests
import json

API_KEY = "app-vvTJvg3XZ7FOdZxIYAsa7eAN"#os.getenv("DIFY_API_KEY")
URL = "https://api.dify.ai/v1/chat-messages"#os.getenv("DIFY_API_URL")

print("KEY:", API_KEY[:6] + "..." if API_KEY else None)
print("URL:", URL)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "query": "你好",
    "inputs": {},
    "response_mode": "blocking",
    "user": "test_user"
}

print(">>> sending request")

resp = requests.post(URL, headers=headers, json=payload, timeout=30)

print("STATUS:", resp.status_code)
print("RAW TEXT:")
print(resp.text)

try:
    print("JSON:", json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("JSON PARSE FAILED:", e)