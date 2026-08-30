#!/usr/bin/env python3
"""First call to the Nous Research Inference API via the OpenAI SDK.

pip install openai
export NOUS_API_KEY=sk-...   # from portal.nousresearch.com -> Settings -> API Keys
"""
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://inference-api.nousresearch.com/v1",
    api_key=os.environ["NOUS_API_KEY"],
)

r = client.chat.completions.create(
    model="nousresearch/hermes-4-70b",  # NOTE: not "Hermes-4-70B" (that 404s)
    messages=[{"role": "user", "content": "Что такое 3+3?"}],
    max_tokens=200,
)
print(r.choices[0].message.content)

# If reasoning was requested and output isn't in content, check:
#   print(getattr(r.choices[0].message, "reasoning_content", None))
