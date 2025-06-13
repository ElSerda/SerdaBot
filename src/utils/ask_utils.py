import httpx


def build_ask_prompt(user: str, question: str, max_length: int = 500) -> str:
    """Builds a clean prompt for an !ask command, limited to a character budget."""
    base_prompt = f"User {user} asks: {question.strip()}"
    return base_prompt[:max_length].strip()


def get_max_length(prefix: str, suffix: str, limit: int = 500) -> int:
    """Calculates available character space for content between prefix and suffix."""
    return max(0, limit - len(prefix) - len(suffix))


async def call_model(
    prompt: str, config: dict, user: str = None, timeout: int = 30
) -> str:
    """Queries the local model server and returns the response."""
    api_url = config.get("api_url", "http://127.0.0.1:8000/chat")
    payload = {"prompt": prompt}
    if user:
        payload["user"] = user

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json().get("response", "")
    except Exception as e:
        print(f"[ASK_UTILS] ❌ Error querying model: {e}")
    return ""
