import os
import json
import requests
import feedparser
from openai import OpenAI
from pydantic import BaseModel
from dotenv import dotenv_values


env = dotenv_values()
OPENROUTER_API_KEY = env.get("OPENROUTER_API_KEY", None)

assert OPENROUTER_API_KEY, "Provide an Openrouter API Key."

client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

completion = client.chat.completions.create(
  # extra_headers={
  #   "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
  #   "X-OpenRouter-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  # },
  model="stepfun/step-3.5-flash:free",
  messages=[
    {
      "role": "user",
      "content": "Hi there!"
    }
  ]
)
print(completion.choices[0].message.content)
