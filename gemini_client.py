import re
import time
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings


@lru_cache(maxsize=1)
def get_gemini_client():
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def _get_retry_seconds(error_text: str, default: int = 10) -> int:
    """
    Try to read Google's suggested retry delay from the error message.
    """

    match = re.search(
        r"retry in ([0-9]+(?:\.[0-9]+)?)s",
        error_text,
        re.IGNORECASE,
    )

    if match:
        try:
            return max(5, int(float(match.group(1))) + 2)
        except ValueError:
            pass

    return default


def generate_text(
    prompt: str,
    model: str,
    temperature: float = 0.4,
    max_output_tokens: int = 2500,
) -> str:

    client = get_gemini_client()

    config = types.GenerateContentConfig(
        max_output_tokens=max_output_tokens
    )

    max_attempts = 5

    for attempt in range(max_attempts):

        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

            generated_text = getattr(response, "text", None)

            if not generated_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return generated_text.strip()

        except Exception as error:

            error_text = str(error)

            # -------------------------------------------------
            # 503 - Gemini temporarily overloaded
            # -------------------------------------------------
            is_503 = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            )

            # -------------------------------------------------
            # 429 - Rate limit / quota
            # -------------------------------------------------
            is_429 = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "Quota exceeded" in error_text
            )

            # -------------------------------------------------
            # Retry temporary Gemini errors
            # -------------------------------------------------
            if is_503 or is_429:

                if attempt == max_attempts - 1:

                    if is_429:
                        raise RuntimeError(
                            "Gemini request limit was reached. "
                            "Please wait a little while and try again."
                        ) from error

                    raise RuntimeError(
                        "Gemini is temporarily experiencing high demand. "
                        "Please wait a few minutes and try again."
                    ) from error

                if is_429:
                    wait_seconds = _get_retry_seconds(
                        error_text,
                        default=15,
                    )
                else:
                    # Increasing backoff for 503
                    wait_seconds = 5 * (2 ** attempt)

                print(
                    f"Gemini temporarily unavailable "
                    f"({ '429' if is_429 else '503' }). "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

                continue

            # -------------------------------------------------
            # Other errors should not be retried
            # -------------------------------------------------
            raise

    raise RuntimeError("Gemini request failed.")