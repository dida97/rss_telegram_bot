import os
import json
import requests
import feedparser
from openai import OpenAI
from pydantic import BaseModel
import logging
from dotenv import dotenv_values

# Configuration
env = dotenv_values()

RSS_URL = env.get("RSS_URL", None)
TELEGRAM_BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN", None)
TELEGRAM_CHAT_ID = env.get("TELEGRAM_CHAT_ID", None)
SEEN_URLS_FILE = env.get("SEEN_URLS_FILE", None)
INTEREST_CRITERIA = env.get("INTEREST_CRITERIA", None)
OPENROUTER_API_KEY = env.get("OPENROUTER_API_KEY", None)

assert OPENROUTER_API_KEY, "Provide an Openrouter API Key."


class AnalysisResult(BaseModel):
    relevant: bool
    commentary: str


def load_seen_urls():
    if os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_urls(seen_urls):
    with open(SEEN_URLS_FILE, "w") as f:
        json.dump(list(seen_urls), f)


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    response.raise_for_status()


def main():
    seen_urls = load_seen_urls()
    feed = feedparser.parse(RSS_URL)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    if not feed.entries:
        return

    for entry in feed.entries:
        link = entry.get("link")
        if not link or link in seen_urls:
            continue

        title = entry.get("title", "No Title")
        summary = entry.get("summary", "No Summary")

        prompt = f"""
        Analyze the following RSS feed item. 
        Criteria: {INTEREST_CRITERIA}
        Title: {title}
        Summary: {summary}
        
        Determine if it is relevant to the criteria. If it is, provide a single-sentence minimal commentary.
        Respond ONLY with a valid JSON object matching this exact schema:
        {{"relevant": boolean, "commentary": "string"}}
        """

        try:

            response = client.chat.completions.create(
                model="stepfun/step-3.5-flash:free",
                extra_body = {        
                    "models": ["nvidia/nemotron-3-super-120b-a12b:free", "qwen/qwen3-next-80b-a3b-instruct:free"],
                },
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content
            # Valida e converte la stringa JSON nel modello Pydantic
            result = AnalysisResult.model_validate_json(raw_content)

            if result.relevant:
                message = "\n\n" + f"<b>{title}</b>\n\n{result.commentary}\n\n<a href='{link}'>Read more</a>"
                send_telegram_message(message)
            
            
        except Exception as e:
            print(f"Error processing {link}: {e}")
    
        seen_urls.add(link)
    

    save_seen_urls(seen_urls)



if __name__ == "__main__":
    main()
