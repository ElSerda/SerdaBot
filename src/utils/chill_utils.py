from twitchio import Message
import httpx


def build_chill_prompt(message: Message, botname: str) -> str:
    """Extracts a casual prompt from a message that mentions the bot."""
    content = message.content.strip()
    lowered = content.lower()
    # Remove bot name from message content
    if botname in lowered:
        lowered = lowered.replace(botname, "").strip()
    return lowered or "React casually to this."


def truncate_response(response: str, limit: int = 500) -> str:
    """Truncates a response cleanly without cutting in the middle of a sentence."""
    if len(response) <= limit:
        return response
    best_dot = response[:limit].rfind(".")
    best_comma = response[:limit].rfind(",")
    if best_dot > 100:
        return response[: best_dot + 1].strip()
    elif best_comma > 100:
        return response[: best_comma + 1].strip()
    return response[:limit].strip() + "…"


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
        print(f"[CHILL_UTILS] ❌ Error querying model: {e}")
    return ""
