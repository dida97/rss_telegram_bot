import os
from dataclasses import dataclass
from dotenv import dotenv_values

@dataclass
class Config:
    rss_feed: str
    telegram_bot_token: str
    telegram_chat_id: str
    interest_criteria: str
    openrouter_api_key: str

    @classmethod
    def load(cls) -> "Config":
        env = dotenv_values()
        
        rss_feed = env.get("RSS_FEED")
        telegram_bot_token = env.get("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = env.get("TELEGRAM_CHAT_ID")
        interest_criteria = env.get("INTEREST_CRITERIA")
        openrouter_api_key = env.get("OPENROUTER_API_KEY")

        if not all([rss_feed, telegram_bot_token, telegram_chat_id, interest_criteria, openrouter_api_key]):
            missing = [
                k for k, v in {
                    "RSS_FEED": rss_feed,
                    "TELEGRAM_BOT_TOKEN": telegram_bot_token,
                    "TELEGRAM_CHAT_ID": telegram_chat_id,
                    "INTEREST_CRITERIA": interest_criteria,
                    "OPENROUTER_API_KEY": openrouter_api_key
                }.items() if not v
            ]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            rss_feed=rss_feed,
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            interest_criteria=interest_criteria,
            openrouter_api_key=openrouter_api_key
        )
