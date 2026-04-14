import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _needs_random_fact_mode(prompt: str) -> bool:
    """
    Return True if the user seems to ask for a single/random fact.
    """
    p = (prompt or "").lower()
    if "random fact" in p:
        return True
    if "one fact" in p or "1 fact" in p:
        return True
    if "fun fact" in p:
        return True
    return False


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file (do not commit .env)."
        )
    return Groq(api_key=api_key)


def _is_retryable_groq_error(e: Exception) -> bool:
    """
    Groq SDK exception classes can vary by version.
    We detect retryable ones by class name and (optionally) status code.
    """
    name = type(e).__name__

    if name in ("APIConnectionError", "APITimeoutError"):
        return True

    if name == "APIStatusError":
        status_code = getattr(e, "status_code", None)
        # Retry common transient status codes
        if status_code in (429, 500, 502, 503, 504):
            return True

    return False


def generate_answer(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
    max_retries: int = 3,
) -> str:
    """
    Generate a chat-style answer from Groq.
    Retries transient failures (network/timeouts/429/5xx).
    """
    client = get_groq_client()

    # stable by default; varied only for "random fact" type prompts
    temp = 0.7 if _needs_random_fact_mode(prompt) else 0.0

    last_err: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are TruthGPT. Answer using 4–6 bullet points.\n"
                            "Rules:\n"
                            "- Each bullet must be ONE verifiable factual claim (no opinions).\n"
                            "- Avoid subjective words like: iconic, famous, notable, significant, beautiful.\n"
                            "- Prefer specific names, dates, numbers, and locations.\n"
                            "- If a detail is uncertain, say 'Uncertain:' and do not guess.\n"
                            "- Do not include extra commentary outside the bullets."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temp,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()

        except Exception as e:
            last_err = e
            if attempt < max_retries and _is_retryable_groq_error(e):
                # exponential backoff: 1s, 2s, 4s...
                sleep_s = 2 ** (attempt - 1)
                time.sleep(sleep_s)
                continue
            raise

    # Shouldn't reach here, but just in case:
    raise last_err if last_err else RuntimeError("Groq request failed.")