import httpx


def detect_lang(text: str, api_url: str = "http://127.0.0.1:5000") -> str:
    """Detect the language of a given text using LibreTranslate."""
    try:
        response = httpx.post(f"{api_url}/detect", data={"q": text}, timeout=10)
        if response.status_code == 200:
            results = response.json()
            if results and isinstance(results, list):
                return results[0].get("language", "und")
    except Exception as e:
        print(f"[TRANSLATE] ❌ Language detection error: {e}")
    return "und"


def translate(
    text: str,
    to_lang: str = "fr",
    from_lang: str = "auto",
    api_url: str = "http://127.0.0.1:5000",
) -> str:
    """Translate text using LibreTranslate API."""
    try:
        payload = {"q": text, "source": from_lang, "target": to_lang, "format": "text"}
        response = httpx.post(f"{api_url}/translate", data=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("translatedText", "")
    except Exception as e:
        print(f"[TRANSLATE] ❌ Translation error: {e}")
    return ""
