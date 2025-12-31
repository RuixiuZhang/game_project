import requests
import json
from config import DIFY_API_KEY, DIFY_API_URL

conversation_id = None


def talk_to_npc(text, inputs):
    global conversation_id

    payload = {
        "query": text,
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "player"
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(DIFY_API_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()

    data = r.json()
    conversation_id = data.get("conversation_id")

    answer = data["answer"]

    try:
        return json.loads(answer)
    except Exception:
        return {
            "reply": answer,
            "expression": "lazy",
            "trigger_event": None
        }