import os
import json
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")  # e.g. https://api.groq.ai/v1


async def generate(
    prompt: str,
    model: str = "groq-1",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    return_json: bool = False,
):
    """Simple async wrapper for a Groq-compatible HTTP inference endpoint.

    This function is intentionally generic: set `GROQ_API_URL` to your provider
    endpoint (for example, a proxy or official Groq endpoint) and set
    `GROQ_API_KEY` in the environment.

    The payload shape is generic and may need adjusting to match your endpoint.
    """
    if not GROQ_API_KEY or not GROQ_API_URL:
        raise ValueError(
            "GROQ_API_KEY and GROQ_API_URL must be set in the environment"
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # If caller expects raw JSON-like response, return it
    if return_json:
        return data

    # Try common fields for text output
    if isinstance(data, dict):
        if "text" in data:
            return data["text"]
        # some providers return `outputs` array
        outputs = data.get("outputs")
        if isinstance(outputs, list) and outputs:
            first = outputs[0]
            if isinstance(first, dict) and "text" in first:
                return first["text"]

    # Fallback: return JSON string
    return json.dumps(data)
