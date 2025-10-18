"""Command handler for chill/sarcastic bot responses."""

import re
import time
from datetime import datetime

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model
from utils.game_selector import match_selection


async def extract_game_name_from_query(query: str, use_llm_fallback: bool = True) -> str:
    """Extrait le nom d'un jeu d'une question utilisateur.
    
    Stratégie modulaire (pas de liste hardcodée):
    1. Patterns regex génériques pour extraire noms propres/titres
    2. Si échec ET use_llm_fallback=True: demander au modèle LLM
    
    Exemples:
    - "quel est le dernier jeu pokemon ?" → "pokemon"
    - "c'est quoi Elden Ring ?" → "elden ring"
    - "Baldur's Gate 3 est sorti quand ?" → "baldur's gate 3"
    """
    query_lower = query.lower()
    original_query = query  # Garde la casse originale pour noms propres
    
    # === 1. Extraction par patterns génériques (sans liste hardcodée) ===
    
    # Pattern 1: "jeu X" ou "nouveau X" ou "dernier X"
    pattern_1 = r"(?:jeu|nouveau|dernier|récent)\s+([A-Z][a-zA-Z0-9\s:''\-]+?)(?:\s+\?|\s+est|\s+sorti|$)"
    match = re.search(pattern_1, original_query)
    if match:
        extracted = match.group(1).strip()
        # Nettoyer (enlever mots communs de fin)
        extracted = re.sub(r'\s+(le|la|les|de|du|des)$', '', extracted, flags=re.IGNORECASE)
        if len(extracted) > 2:  # Au moins 3 chars
            return extracted.lower()
    
    # Pattern 2: Nom propre suivi de verbe (ex: "Starfield est sorti")
    pattern_2 = r"([A-Z][a-zA-Z0-9\s:''\-]+?)\s+(?:est|sorti|sortit|dispo|disponible)"
    match = re.search(pattern_2, original_query)
    if match:
        extracted = match.group(1).strip()
        if len(extracted) > 2:
            return extracted.lower()
    
    # Pattern 3: Entre guillemets ou après "c'est quoi"
    pattern_3 = r"(?:c'est quoi|quoi)\s+(?:le\s+)?([A-Z][a-zA-Z0-9\s:''\-]+?)(?:\s+\?|$)"
    match = re.search(pattern_3, original_query)
    if match:
        extracted = match.group(1).strip()
        if len(extracted) > 2:
            return extracted.lower()
    
    # Pattern 4: Mots après "jeu" ou "game" (même en minuscules)
    pattern_4 = r'(?:jeu|game)\s+([a-z][a-z0-9\s]+?)(?:\s+\?|\s+est|\s+sorti|$)'
    match = re.search(pattern_4, query_lower)
    if match:
        extracted = match.group(1).strip()
        # Enlever mots de liaison
        extracted = re.sub(r'\s+(le|la|les|de|du|des|en|sur|pour)$', '', extracted)
        if len(extracted) > 2:
            return extracted
    
    # === 2. Fallback LLM (si activé) ===
    if use_llm_fallback:
        try:
            import httpx
            
            extraction_prompt = f"""Extrait le nom du jeu vidéo ou de la franchise. Réponds UNIQUEMENT avec le nom, ou AUCUN.
Exemples: 'quel est le dernier jeu pokemon ?' → 'Pokemon' | 'c est quoi Elden Ring ?' → 'Elden Ring' | 'salut' → 'AUCUN'
Question: {query}"""
            
            payload = {
                "model": "qwen2.5-3b-instruct",
                "messages": [{"role": "user", "content": extraction_prompt}],
                "temperature": 0.1,
                "max_tokens": 20,
            }
            
            response = httpx.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                extracted = result["choices"][0]["message"]["content"].strip()
                
                if extracted and extracted.upper() != "AUCUN":
                    return extracted.lower()
        except Exception:
            pass  # Si LLM échoue, on continue sans
    
    return ""


def filter_generic_responses(response: str) -> str:
    """Filter out generic/cringe AI phrases and make responses punchier."""
    # Liste de phrases génériques à éviter (auto-congratulation)
    generic_phrases = [
        "je vais devoir ajouter",
        "ma liste de qualités",
        "ma longue liste",
        "quelqu'un doit bien le faire",
        "c'est mon travail",
        "je suis là pour",
        "mes capacités incroyables",
        "fantastique",
    ]
    
    # Si la réponse contient des phrases génériques, on la rejette (retourne vide)
    response_lower = response.lower()
    for phrase in generic_phrases:
        if phrase in response_lower:
            return ""  # Force un retry ou fallback
    
    return response


async def handle_chill_command(message: Message, config: dict, now, conversation_manager=None):  # pylint: disable=unused-argument
    """Handle chill command with sarcastic AI responses for all users."""
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    user_name = str(message.author.name or "user").lower()

    # Extraire le contenu du message sans le nom du bot
    raw_content = message.content or ""
    content = raw_content.strip().lower().replace(botname, "").strip()
    if not content:
        content = "Salut !"

    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # === PROACTIVE REASONING: Détection "dernier jeu" AVANT le modèle ===
    # Trigger IGDB direct si question sur "dernier/récent/nouveau jeu"
    proactive_triggers = ["dernier", "récent", "nouveau", "latest", "recent", "new"]
    game_indicators = ["jeu", "game", "pokemon", "pokémon", "zelda", "mario", "sortit", "sorti", "sortie"]
    
    is_latest_query = any(trigger in content.lower() for trigger in proactive_triggers)
    has_game_keyword = any(indicator in content.lower() for indicator in game_indicators)
    
    if is_latest_query and has_game_keyword:
        if debug:
            print("[CHILL] 🎯 Proactive Reasoning: Détection question 'dernier jeu'")
        
        # Extraire le nom du jeu
        game_name = await extract_game_name_from_query(content)
        
        if game_name:
            if debug:
                print(f"[CHILL] 🔍 Extraction proactive du jeu: '{game_name}'")
            
            # Appeler IGDB directement (bypass modèle)
            from utils.game_utils import fetch_game_data
            game_data = await fetch_game_data(game_name)
            
            if game_data and game_data.get("name"):
                # Construire contexte avec données IGDB
                release_date = game_data.get("release") or game_data.get("first_release_date")
                if release_date and release_date != "Date inconnue":
                    try:
                        year = datetime.utcfromtimestamp(int(release_date)).year
                    except (ValueError, TypeError):
                        year = "inconnue"
                else:
                    year = "inconnue"
                
                current_year = datetime.now().year
                context = f"Nous sommes en {current_year}. Info IGDB (données fiables): {game_data.get('name')} sorti en {year}."
                
                if debug:
                    print(f"[CHILL] 📚 Contexte IGDB proactif: {context}")
                
                # Appeler le modèle AVEC le contexte IGDB
                prompt_with_context = make_prompt(mode="chill", content=f"{content}\n\nContexte: {context}", user=user_name, game=game, title=title)
                response = await call_model(prompt_with_context, config, user=user_name, mode="chill")
                
                if debug:
                    print(f"[CHILL] 🧠 Réponse avec contexte proactif: {response[:100]}...")
                
                # Envoyer réponse et terminer
                if response:
                    filtered = filter_generic_responses(response.strip())
                    if not filtered:
                        filtered = "🤔 Hmm, laisse-moi réfléchir à ça..."
                    
                    final_response = filtered if len(filtered) <= 500 else filtered[:497] + "…"
                    
                    try:
                        if debug:
                            print(f"[SEND] 📤 Envoi CHILL (proactif): {final_response[:100]}...")
                        await message.channel.send(final_response)
                        if debug:
                            print(f"[CHILL] ✅ Réponse proactive envoyée à @{user_name}")
                    except Exception as e:
                        print(f"[CHILL] ❌ Erreur d'envoi: {e}")
                    
                    return
    
    # === LOGIQUE NORMALE (pas de trigger proactif) ===
    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="chill", content=content, user=user_name, game=game, title=title)

    if debug:
        print(f"[CHILL] 📝 USER Prompt ({len(prompt)} chars): {prompt[:150]}{'...' if len(prompt) > 150 else ''}")

    response = await call_model(prompt, config, user=user_name, mode="chill")
    
    # === REACTIVE REASONING LOOP: Si le bot dit ne pas connaître un jeu, interroger IGDB ===
    uncertainty_keywords = ["ne sais pas", "sais pas", "connais pas", "après 2023", "pas sûr", "pas sur", "ne suis pas sûr"]
    if response and any(keyword in response.lower() for keyword in uncertainty_keywords):
        # Détecter si c'est une question sur un jeu (mots-clés: jeu, pokemon, zelda, etc.)
        game_keywords = ["jeu", "game", "pokemon", "pokémon", "zelda", "mario", "sortit", "sorti", "sortie", "2024", "2025"]
        if any(keyword in content.lower() for keyword in game_keywords):
            if debug:
                print("[CHILL] 🧠 Reasoning Loop: Détection question sur jeu inconnu")
            
            # Extraire le nom du jeu de la question
            game_name = await extract_game_name_from_query(content)
            
            if game_name:
                if debug:
                    print(f"[CHILL] 🔍 Extraction du jeu: '{game_name}'")
                
                # Appeler IGDB (même fonction que !gameinfo)
                from utils.game_utils import fetch_game_data
                game_data = await fetch_game_data(game_name)
                
                if game_data and game_data.get("name"):
                    # Construire un contexte pour le modèle
                    release_date = game_data.get("release") or game_data.get("first_release_date")
                    if release_date and release_date != "Date inconnue":
                        try:
                            year = datetime.utcfromtimestamp(int(release_date)).year
                        except (ValueError, TypeError):
                            year = "inconnue"
                    else:
                        year = "inconnue"
                    
                    # Ajouter la date actuelle pour que le modèle se repère dans le temps
                    current_year = datetime.now().year
                    context = f"Nous sommes en {current_year}. Info IGDB: {game_data.get('name')} sorti en {year}."
                    
                    if debug:
                        print(f"[CHILL] 📚 Contexte IGDB: {context}")
                    
                    # 2ème passe du modèle avec le contexte
                    reasoning_prompt = f"{content}\n\nContexte (tu peux maintenant répondre): {context}"
                    response = await call_model(reasoning_prompt, config, user=user_name, mode="chill")
                    
                    if debug:
                        print(f"[CHILL] 🧠 Réponse après reasoning: {response[:100]}...")
                else:
                    if debug:
                        print("[CHILL] ❌ IGDB: Aucune donnée trouvée")
                    # Fallback: suggérer !gameinfo
                    response = f"{response} Essaye `!gameinfo {game_name}` pour plus d'infos !"
            else:
                if debug:
                    print("[CHILL] ⚠️ Impossible d'extraire le nom du jeu")
                # Fallback générique
                response = f"{response} Essaye `!gameinfo [nom du jeu]` pour plus d'infos !"

    if debug:
        print(f"[CHILL] 📨 Réponse du modèle: {response[:100] if response else 'VIDE'}...")

    if not response:
        await message.channel.send("🤷 Réponse manquante.")
        return

    # Filtre anti-générique (garde la spontanéité du bot)
    filtered = filter_generic_responses(response.strip())
    if not filtered:
        if debug:
            print(f"[CHILL] ⚠️ Réponse générique filtrée: {response[:50]}...")
        filtered = "🤔 Hmm, laisse-moi réfléchir à ça..."

    # Sécurité Twitch (rare mais filet de sécurité)
    final_response = filtered if len(filtered) <= 500 else filtered[:497] + "…"
    
    try:
        if debug:
            print(f"[SEND] 📤 Envoi CHILL: {final_response[:100]}...")
        await message.channel.send(final_response)
        if debug:
            print(f"[CHILL] ✅ Réponse envoyée à @{user_name}")
    except Exception as e:
        print(f"[CHILL] ❌ Erreur d'envoi: {e}")
