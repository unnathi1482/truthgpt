import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def _needs_random_fact_mode(prompt: str) -> bool:
    """
    Return True if the user seems to ask for a single/random fact.
    """
    p = prompt.lower()
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


def generate_answer(prompt: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Generate a chat-style answer from Groq.
    """
    client = get_groq_client()

    # Decide temperature: stable by default, higher only for "random fact" style prompts.
    if _needs_random_fact_mode(prompt):
        temp = 0.7
    else:
        temp = 0.0

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