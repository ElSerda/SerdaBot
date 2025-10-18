import time, os, json, sys
import requests

API = os.environ.get("LLM_API", "http://127.0.0.1:1234/v1/chat/completions")
MODEL = os.environ.get("LLM_MODEL", "Qwen2.5-1.5B-Instruct-Q4_K_M")

# v1.1 - 187 chars
SYSTEM = ("Bot Twitch FR. UNE phrase (≤30 mots, ≤150 chars). Pas de /me, hashtags. 0-2 émojis. "
          "Ton naturel, direct, jamais méchant. Pas de salutations auto, métadiscours, excuses, auto-présentation.")

def test_model(mode: str, user_text: str):
    """Test direct du modèle avec température dynamique."""
    temp = 0.6 if mode == "ask" else 0.7
    
    if mode == "ask":
        user_msg = f"Explique brièvement: «{user_text if user_text.endswith('?') else user_text+' ?'}». Réponds en 1 phrase."
    else:
        user_msg = f"Réponds sur ton complice. «{user_text}». Réponds en 1 phrase."
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_msg}
        ],
        "temperature": temp,
        "top_p": 0.9,
        "top_k": 40,
        "min_p": 0.05,
        "repeat_penalty": 1.10,
        "max_tokens": 60,
        "stop": ["\nUser:", "\nAssistant:"]
    }
    
    print(f"\n{'='*60}")
    print(f"MODE: {mode.upper()} | TEMP: {temp}")
    print(f"SYSTEM: {SYSTEM[:80]}... ({len(SYSTEM)} chars)")
    print(f"USER: {user_msg[:80]}...")
    print(f"{'='*60}")
    
    t0 = time.time()
    r = requests.post(API, json=payload, timeout=15)
    dt = time.time() - t0
    r.raise_for_status()
    out = r.json()["choices"][0]["message"]["content"].strip()
    print(f"OUT: {out}")
    print(f"⚡ {dt:.2f}s | {len(out)} chars")
    print(f"{'='*60}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Mode démo
        test_model("ask", "ordinateur quantique")
        test_model("chill", "Salut le bot !")
    else:
        mode = sys.argv[1] if sys.argv[1] in ["ask", "chill"] else "ask"
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "test"
        test_model(mode, query)
