import requests
from langdetect import detect


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "und"


def translate_text(text: str, source_lang: str, target_lang: str = "fr") -> str:
    try:
        response = requests.post(
            "http://127.0.0.1:5000/translate",
            json={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text",
            },
            timeout=5,
        )
        if response.status_code == 200:
            return response.json().get("translatedText", "")
        return "[Translation failed]"
    except Exception as e:
        return f"[Translation error: {e}]"
