import os, time, requests, random

API   = os.environ.get("LLM_API", "http://127.0.0.1:1234/v1/chat/completions")
MODEL = os.environ.get("LLM_MODEL", "Qwen2.5-1.5B-Instruct-Q4_K_M")

# === MODE ANALYSE ===
DISABLE_QUOTES = True  # Set False pour tester roast/quotes

# importe tes helpers actuels
from prompts.prompt_loader import build_messages, make_openai_payload
from cogs.roast_manager import load_roast_config, load_quotes_config, DEFAULT_PATH, QUOTES_PATH

def call_model(built, max_tokens=60):
    """Appelle le modèle avec le nouveau système build_messages."""
    payload = make_openai_payload(MODEL, built, max_tokens=max_tokens)
    
    t0 = time.time()
    r = requests.post(API, json=payload, timeout=15)
    dt = time.time() - t0
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"].strip()
    return txt, dt




def run_case_with_lang(mode, message, user, lang="zh", max_tokens=60):
    """Test un cas avec une langue de prompt spécifique."""
    
    # === ROAST DIRECT (comme dans chill_command.py) ===
    if not DISABLE_QUOTES:
        roast_config = load_roast_config(DEFAULT_PATH)
        roast_users = {u.lower() for u in roast_config.get("users", [])}
        roast_quotes = roast_config.get("quotes", [])
        
        if mode == "chill" and user.lower() in roast_users and roast_quotes:
            quote = random.choice(roast_quotes)
            print(f"OUT   : {quote}  (len={len(quote)}, 0.00s ⚡ ROAST DIRECT)")
            return
        
        # === QUOTE FUN (20% pour users normaux) ===
        quotes_config = load_quotes_config(QUOTES_PATH)
        fun_quotes = quotes_config.get("quotes", [])
        
        if mode == "chill" and fun_quotes and random.random() < 0.2:
            quote = random.choice(fun_quotes)
            print(f"OUT   : {quote}  (len={len(quote)}, 0.00s ⚡ QUOTE FUN)")
            return
    
    # === MODÈLE (ask ou chill normal) ===
    built = build_messages(mode, message, lang=lang)
    txt, dt = call_model(built, max_tokens=max_tokens)
    print(f"OUT   : {txt}  (len={len(txt)}, {dt:.2f}s)")
    
    # Affiche les tokens si différent de default
    if max_tokens != 60:
        print(f"        (max_tokens={max_tokens})")


if __name__ == "__main__":
    print("=" * 80)
    mode_txt = "MODE ANALYSE - Quotes/Roast désactivés" if DISABLE_QUOTES else "MODE COMPLET - v1.1.2"
    print(f"🧪 MEGA SMOKE TEST - PROMPT ZH PRODUCTION (max_tokens=250)")
    print(f"📝 {mode_txt}")
    print(f"🎯 Test exhaustif : Ask tech/gaming/culture + Chill varié")
    print("=" * 80)
    
    # 🚀 MEGA TEST - 30+ cas variés avec max_tokens=250 partout
    tests = [
        # ===== ASK MODE - TECH =====
        ("ask",   "python",                              "viewer",    250, "Ask Tech: Python (1 mot)"),
        ("ask",   "IA",                                  "viewer",    250, "Ask Tech: IA (2 lettres)"),
        ("ask",   "ordinateur quantique",                "viewer",    250, "Ask Tech: Quantique"),
        ("ask",   "blockchain",                          "viewer",    250, "Ask Tech: Blockchain"),
        ("ask",   "c'est quoi un serveur web",           "viewer",    250, "Ask Tech: Serveur web"),
        ("ask",   "Docker c'est quoi",                   "viewer",    250, "Ask Tech: Docker"),
        ("ask",   "peux-tu expliquer la POO",            "viewer",    250, "Ask Tech: POO détaillé"),
        ("ask",   "comment fonctionne internet",         "viewer",    250, "Ask Tech: Internet global"),
        ("ask",   "différence entre git et github",      "viewer",    250, "Ask Tech: Git vs GitHub"),
        ("ask",   "c'est quoi les microservices",        "viewer",    250, "Ask Tech: Microservices"),
        
        # ===== ASK MODE - GAMING =====
        ("ask",   "Elden Ring",                          "viewer",    250, "Ask Gaming: Elden Ring"),
        ("ask",   "speedrun",                            "viewer",    250, "Ask Gaming: Speedrun"),
        ("ask",   "c'est quoi un FPS",                   "viewer",    250, "Ask Gaming: FPS genre"),
        ("ask",   "Dark Souls vs Bloodborne",            "viewer",    250, "Ask Gaming: Souls compare"),
        ("ask",   "comment optimiser son setup gaming",  "viewer",    250, "Ask Gaming: Setup"),
        ("ask",   "pourquoi Skyrim est populaire",       "viewer",    250, "Ask Gaming: Skyrim"),
        ("ask",   "c'est quoi le ray tracing",           "viewer",    250, "Ask Gaming: Ray tracing"),
        
        # ===== ASK MODE - CULTURE / DIVERS =====
        ("ask",   "croissant",                           "viewer",    250, "Ask Culture: Croissant"),
        ("ask",   "pourquoi le ciel est bleu",           "viewer",    250, "Ask Science: Ciel bleu"),
        ("ask",   "c'est quoi Twitch",                   "viewer",    250, "Ask Méta: Twitch"),
        ("ask",   "différence entre IRC et Discord",     "viewer",    250, "Ask Tech: IRC vs Discord"),
        
        # ===== CHILL MODE - SOCIAL =====
        ("chill", "Salut !",                             "viewer",    250, "Chill Social: Salut"),
        ("chill", "yo les gens",                         "viewer",    250, "Chill Social: Yo"),
        ("chill", "comment ça va ?",                     "viewer",    250, "Chill Social: Comment ça va"),
        ("chill", "bonsoir",                             "viewer",    250, "Chill Social: Bonsoir"),
        
        # ===== CHILL MODE - REACTIONS =====
        ("chill", "lol",                                 "viewer",    250, "Chill Reaction: lol"),
        ("chill", "mdr ce fail",                         "viewer",    250, "Chill Reaction: mdr fail"),
        ("chill", "GG le stream",                        "viewer",    250, "Chill Reaction: GG"),
        ("chill", "F dans le chat",                      "viewer",    250, "Chill Reaction: F chat"),
        ("chill", "poggers",                             "viewer",    250, "Chill Reaction: poggers"),
        ("chill", "PepeLaugh",                           "viewer",    250, "Chill Reaction: PepeLaugh"),
        
        # ===== CHILL MODE - GAMEPLAY =====
        ("chill", "le boss est trop dur",                "viewer",    250, "Chill Gameplay: Boss dur"),
        ("chill", "skill issue",                         "viewer",    250, "Chill Gameplay: Skill issue"),
        ("chill", "ez clap",                             "viewer",    250, "Chill Gameplay: Ez clap"),
        ("chill", "comment tu as fait ce jump ?",        "viewer",    250, "Chill Gameplay: Jump question"),
        ("chill", "gg c'était chaud",                    "viewer",    250, "Chill Gameplay: GG chaud"),
        
        # ===== CHILL MODE - RANDOM =====
        ("chill", "tu préfères pizza ou burger ?",       "viewer",    250, "Chill Random: Pizza burger"),
        ("chill", "il est quelle heure ?",               "viewer",    250, "Chill Random: Heure"),
        ("chill", "quel jeu tu stream demain ?",         "viewer",    250, "Chill Random: Jeu demain"),
        ("chill", "j'ai faim",                           "viewer",    250, "Chill Random: Faim"),
        
        # ===== EDGE CASES =====
        ("ask",   "???",                                 "viewer",    250, "Edge: ??? seul"),
        ("chill", "...",                                 "viewer",    250, "Edge: ... seul"),
        ("ask",   "réponds en une phrase: c'est quoi linux", "viewer", 250, "Edge: Directive explicite"),
    ]
    
    passed = 0
    failed = 0
    
    for mode, msg, user, max_tok, label in tests:
        print(f"\n{'='*80}")
        print(f"🎯 {label}")
        print(f"   MODE: {mode.upper()} | USER: {user} | INPUT: {msg}")
        print(f"   MAX_TOKENS: {max_tok}")
        print(f"{'='*80}")
        
        try:
            run_case_with_lang(mode, msg, user, lang="zh", max_tokens=max_tok)
            passed += 1
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"✅ MEGA TEST TERMINÉ - {passed} succès / {failed} échecs")
    print(f"📊 Score: {passed}/{passed+failed} ({100*passed/(passed+failed):.0f}%)")
    print("=" * 80)
