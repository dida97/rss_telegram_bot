import logging
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class AnalysisResult(BaseModel):
    relevant: bool

class FeedAnalyzer:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model: str = "stepfun/step-3.5-flash:free"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def is_relevant(self, title: str, summary: str, criteria: str) -> bool:
        prompt = f"""
        Analyze the following RSS feed item. 
        Criteria: {criteria}
        Title: {title}
        Summary: {summary}
        Determine if it is relevant to the criteria specified by the user. 
        Respond **ONLY** with a valid **JSON** object matching **THIS EXACT SCHEMA**: {{"relevant" : bool}}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                logger.error("Received empty response from LLM.")
                return False

            result = AnalysisResult.model_validate_json(raw_content)
            return result.relevant

        except ValidationError as e:
            logger.error(f"Failed to parse JSON from LLM: {e}")
            return False
        except Exception as e:
            logger.error(f"Error communicating with LLM logic: {e}")
            return False