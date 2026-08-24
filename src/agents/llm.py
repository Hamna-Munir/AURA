# src/agents/llm.py
import json
import time
from groq import Groq, RateLimitError

from src.utils import config
from src.utils.logger import get_logger

log = get_logger("agents.llm")

# Groq ne purane llama models retire kar diye; ye current recommended hai.
MODEL = "openai/gpt-oss-20b"

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not config.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY missing hai. .env mein Groq key daalo.")
        _client = Groq(api_key=config.LLM_API_KEY)
    return _client


def ask_json(system_prompt: str, user_prompt: str, max_retries: int = 3) -> dict:
    """
    LLM ko call karo aur GUARANTEED JSON (dict) wapas lo.
    - JSON parse fail ho to safely clean kar ke retry.
    - Rate limit (429) aaye to ruk kar dobara koshish.
    """
    client = get_client()

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,   # kam temperature = zyada consistent faisle
                response_format={"type": "json_object"},  # JSON mode
            )
            raw = resp.choices[0].message.content

            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                # Safety net: kabhi model ```json ... ``` mein wrap kar deta hai
                cleaned = (
                    raw.strip()
                    .removeprefix("```json")
                    .removeprefix("```")
                    .removesuffix("```")
                    .strip()
                )
                log.warning("JSON parse retry ho raha hai")
                return json.loads(cleaned)

        except RateLimitError:
            wait = 3 * (attempt + 1)   # 3s, 6s, 9s
            log.warning("Rate limit hit. %ss wait kar ke retry (%d/%d)...",
                        wait, attempt + 1, max_retries)
            time.sleep(wait)

    raise RuntimeError("Rate limit ke baad bhi fail. Thodi der baad try karo.")