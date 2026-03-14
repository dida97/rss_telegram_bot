import feedparser
from openai import OpenAI
from pydantic import BaseModel
from dotenv import dotenv_values

from utils.database_utils import is_url_seen, add_seen_url
from utils.telegram_utils import send_telegram_message

NO_TITLE_STRING = "No Title"
NO_SUMMARY_STRING = "No Summary"

# Configuration
env = dotenv_values()

RSS_FEED = env.get("RSS_FEED")
TELEGRAM_BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env.get("TELEGRAM_CHAT_ID")
INTEREST_CRITERIA = env.get("INTEREST_CRITERIA")
OPENROUTER_API_KEY = env.get("OPENROUTER_API_KEY")

assert OPENROUTER_API_KEY, "Provide an Openrouter API Key."


class AnalysisResult(BaseModel):
    relevant: bool


def main():
    feed = feedparser.parse(RSS_FEED)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    if not feed.entries:
        return

    for entry in feed.entries:
        link = entry.get("link")
        if not link or is_url_seen(RSS_FEED, link):
            continue

        title = entry.get("title", NO_TITLE_STRING)
        summary = entry.get("summary", NO_SUMMARY_STRING)

        prompt = f"""
        Analyze the following RSS feed item. 
        Criteria: {INTEREST_CRITERIA}
        Title: {title}
        Summary: {summary}
        Determine if it is relevant to the criteria specified by the user. 
        Respond **ONLY** with a valid **JSON** object matching **THIS EXACT SCHEMA**: {{"relevant" : bool}}
        """

        try:
            response = client.chat.completions.create(
                model="stepfun/step-3.5-flash:free",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content
            result = AnalysisResult.model_validate_json(raw_content)

            if result.relevant:
                message = f"<b>{title}</b>\n\n<a href='{link}'>Read more</a>"
                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
                add_seen_url(RSS_FEED, link)

        except Exception as e:
            print(f"Error processing {link}: {e}")
            print(f"Adding Back this entry to the queue")
            feed.entries.append(entry)


if __name__ == "__main__":
    main()
