import json, time, queue
from openai import OpenAI
from api import api

client = OpenAI(api_key=api())
llm_queue = queue.Queue(maxsize=5)

SYSTEM = """
You are the world director of a survival game.
YOUR OUTPUT SHOULD BE BRIEF
Output JSON only.
Schema: {"narrative":"string","actions":[]}
"""

def llm_worker(ctx_fn):
    while True:
        time.sleep(2.0)
        try:
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":SYSTEM},
                    {"role":"user","content":json.dumps(ctx_fn())}
                ],
                max_tokens=140
            )
            data = json.loads(r.choices[0].message.content)
        except:
            data = {"narrative":"Your thoughts echo strangely.","actions":[]}

        if not llm_queue.full():
            llm_queue.put(data)