import time, os, json, sys
import requests

API = os.environ.get("LLM_API", "http://127.0.0.1:1234/v1/chat/completions")
MODEL = os.environ.get("LLM_MODEL", "Qwen2.5-1.5B-Instruct-Q4_K_M")

# Import du prompt ZH de production
from prompts.prompt_loader import SYSTEM_ZH

def test_model(mode: str, user_text: str):
    """Test direct du modèle avec prompt ZH de production."""
    temp = 0.6 if mode == "ask" else 0.7
    
    # Utilise le même système que build_messages() pour cohérence
    if mode == "ask":
        # Reformulation en question comme dans to_question_fr()
        if not user_text.endswith("?"):
            if len(user_text.split()) <= 3:
                user_msg = f"C'est quoi {user_text} ?"
            else:
                user_msg = user_text + " ?"
        else:
            user_msg = user_text
    else:
        # Mode chill: texte brut
        user_msg = user_text
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_ZH},
            {"role": "user", "content": user_msg}
        ],
        "temperature": temp,
        "top_p": 0.9,
        "top_k": 40,
        "min_p": 0.05,
        "repeat_penalty": 1.10,
        "max_tokens": 250,  # Aligné avec production
        "stop": ["\nUser:", "\nAssistant:"]
    }
    
    print(f"\n{'='*60}")
    print(f"MODE: {mode.upper()} | TEMP: {temp} | MAX_TOKENS: 250")
    print(f"SYSTEM: SYSTEM_ZH (prompt chinois production)")
    print(f"USER: {user_msg}")
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
