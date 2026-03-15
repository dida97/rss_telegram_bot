import os
from dataclasses import dataclass
from dotenv import dotenv_values

@dataclass
class Config:
    telegram_bot_token: str
    telegram_chat_id: str
    openrouter_api_key: str

    @classmethod
    def load(cls) -> "Config":
        env = dotenv_values()
        
        telegram_bot_token = env.get("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = env.get("TELEGRAM_CHAT_ID")
        openrouter_api_key = env.get("OPENROUTER_API_KEY")

        if not all([telegram_bot_token, telegram_chat_id, openrouter_api_key]):
            env_vars: dict[str, str | None] = {
                "TELEGRAM_BOT_TOKEN": telegram_bot_token,
                "TELEGRAM_CHAT_ID": telegram_chat_id,
                "OPENROUTER_API_KEY": openrouter_api_key
            }
            missing: list[str] = [k for k, v in env_vars.items() if not v]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            telegram_bot_token=telegram_bot_token,
            telegram_chat_id=telegram_chat_id,
            openrouter_api_key=openrouter_api_key
        )
