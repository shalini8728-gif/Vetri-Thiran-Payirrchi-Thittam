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
            "GEMINI_API_KEY is missing. Please add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def _get_retry_seconds(error_text: str, default: int = 5) -> int:
    match = re.search(
        r"retry in ([0-9]+(?:\.[0-9]+)?)s",
        error_text,
        re.IGNORECASE,
    )

    if match:
        try:
            return max(3, int(float(match.group(1))) + 1)
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
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    # Only retry temporary 503 errors.
    # Do NOT repeatedly retry quota/429 errors.
    max_attempts = 3

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

            is_503 = (
                "503" in error_text
                or "UNAVAILABLE" in error_text.upper()
            )

            is_429 = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text.upper()
                or "QUOTA" in error_text.upper()
            )

            # API quota problem
            if is_429:

                raise RuntimeError(
                    "Gemini API quota has been reached. "
                    "Please wait for the quota to reset or use a Gemini API project "
                    "with available quota."
                ) from error

            # Temporary Gemini server problem
            if is_503:

                if attempt == max_attempts - 1:

                    raise RuntimeError(
                        "Gemini is temporarily unavailable. "
                        "Please wait a few minutes and try again."
                    ) from error

                wait_seconds = _get_retry_seconds(
                    error_text,
                    default=5,
                )

                print(
                    f"Gemini temporarily unavailable (503). "
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)
                continue

            # Any other error
            raise RuntimeError(
                f"Gemini request failed: {error_text}"
            ) from error

    raise RuntimeError("Gemini request failed.")