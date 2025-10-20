"""Command handler for chill/sarcastic bot responses."""

import re
import time
from datetime import datetime

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model
from utils.routing_utils import should_route_to_gameinfo
from src.core.fallbacks import get_fallback_response


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


def detect_vague_game_response(user_msg: str, response: str) -> str | None:
    """Détecte si le bot parle d'un jeu de façon dangereuse (vague OU avec dates).
    
    Philosophie KISS : Le LLM ne doit JAMAIS citer une année dans un contexte jeu.
    C'est IGDB qui parle des dates, pas le LLM.
    
    Args:
        user_msg: Message original de l'utilisateur
        response: Réponse générée par le modèle
        
    Returns:
        Message de redirection si détection, None sinon
    """
    game_keywords = [
        # Mots génériques contextuels (pas de noms de jeux)
        "jeu", "game", "sorti", "sortie", "sortit", "sortira", "sort", "quand", "date", 
        "plateforme", "pc", "ps5", "ps4", "ps3", "xbox", "switch", 
        "steam", "mobile", "console", "dispo", "disponible",
        # Noms de franchises courantes (pour attraper "Quand sort Zelda ?")
        "zelda", "mario", "pokemon", "pokémon", "gta", "elden", "skyrim", 
        "cyberpunk", "witcher", "god of war", "horizon", "final fantasy"
    ]
    
    vague_words = [
        "je crois", "peut-être", "il parait", "annoncé", 
        "je cherche", "non", "pas de", "peut-être une",
        "keepers 2", "serda, je cherche", "je ne sais pas",
        "sera", "serait", "pourrait", "devrait", "va", "irait",  # Futur/conditionnel = souvent invention
        "bientot", "biento", "bientôt", "prochainement"  # Argot courant = évasion
    ]
    
    user_lower = user_msg.lower()
    response_lower = response.lower()
    
    # Détection contexte jeu : keywords obligatoires
    has_game = any(kw in user_lower for kw in game_keywords)
    
    # Pas de contexte jeu → pas de filtre
    if not has_game:
        return None
    
    # Détection 1 : Mots vagues
    is_vague = any(vw in response_lower for vw in vague_words)
    
    # Détection 2 : TOUTE année (1000-2999) - Pattern intemporel
    # Le LLM ne doit JAMAIS dater un jeu, peu importe l'année
    year_pattern = re.compile(r'\b(1[0-9]{3}|2[0-9]{3})\b')
    has_year = year_pattern.search(response)
    
    # Si user parle de jeu ET (bot vague OU bot cite une année)
    if is_vague or has_year:
        # Extraire le nom du jeu du message user
        game_hint = ""
        
        # Termes génériques à exclure (pas des noms de jeux)
        GENERIC_TERMS = {"aaa", "jeu", "game", "titre", "truc", "machin", "prochain", "nouveau", "dernier"}
        
        # Chercher noms propres (majuscules) dans le message
        words = user_msg.split()
        game_words = []
        
        for word in words:
            word_clean = word.strip(",.!?")
            word_lower = word_clean.lower()
            
            # Filtrage : exclure termes génériques ou trop courts
            if word_lower in GENERIC_TERMS or len(word_clean) < 3:
                continue
            
            # Nom propre = majuscule ET pas mot interrogatif/commun
            if (word_clean and word_clean[0].isupper() 
                and word_lower not in ["date", "quand", "pour", "dans", "avec", "sans", "quel", "quelle"]):
                game_words.append(word_lower)
            elif game_words:
                # Si on avait commencé à collecter et qu'on rencontre un mot non-propre, stop
                break
        
        if game_words:
            game_hint = f" {' '.join(game_words)}"
        
        return f"Pas sûr des dates. Essaye `!gameinfo{game_hint}` 😉"
    
    return None


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


async def handle_chill_command(message: Message, config: dict, now, conversation_manager=None, llm_available: bool = True):  # pylint: disable=unused-argument
    """Handle chill command with sarcastic AI responses for all users.
    
    Args:
        message: Message Twitch reçu
        config: Configuration du bot
        now: Timestamp actuel
        conversation_manager: Gestionnaire de conversation (optionnel)
        llm_available: Si le LLM est disponible (défaut: True pour rétrocompatibilité)
    """
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    user_name = str(message.author.name or "user").lower()

    # Extraire le contenu du message
    raw_content = message.content or ""
    
    # Vérifier si le bot est mentionné (KISS: chercher botname n'importe où avec espaces)
    content_lower = f" {raw_content.lower()} "
    has_mention = f" {botname} " in content_lower or f"@{botname}" in content_lower
    
    # Si pas de mention du bot, ignorer le message
    if not has_mention:
        if debug:
            print(f"[CHILL] ⏭️  Pas de mention du bot dans: '{raw_content[:40]}...'")
        return
    
    # Nettoyer le message: retirer @ et le nom du bot
    content = raw_content.replace("@", "").strip()
    content_lower = content.lower()
    
    # Retirer le botname du contenu
    words = content_lower.split()
    
    # Si le botname est le seul mot, remplacer par "Salut !"
    if len(words) == 1 and words[0] == botname:
        content = "Salut !"
    # Sinon retirer le botname en début ou fin de phrase
    else:
        # Retirer en début
        if content_lower.startswith(botname + " "):
            content = content[len(botname):].strip()
        # Retirer en fin
        elif content_lower.endswith(" " + botname):
            content = content[:-len(botname)].strip()
        else:
            # Si au milieu, le laisser (ex: "comment va serda_bot ?")
            content = content.strip()
    
    if not content:
        content = "Salut !"

    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # === ROUTAGE INTELLIGENT: RAWG-FIRST ===
    # Détecter si le message parle d'un jeu vidéo → utiliser RAWG au lieu du LLM
    routing_start = time.time()
    
    # Import de la fonction extract_game_entity depuis ask_command
    from src.core.commands.ask_command import extract_game_entity, format_game_answer
    
    game_entity = await extract_game_entity(content)
    routing_time = (time.time() - routing_start) * 1000  # ms
    
    if game_entity:
        if debug:
            print(f"[ROUTING] 🎮 Entité jeu détectée: '{game_entity}'")
            print(f"[ROUTING] 🧠 Décision: RAWG (jeu détecté)")
        
        # Tenter de récupérer les données du jeu via RAWG (avec cache)
        try:
            from src.core.commands.api.game_data_fetcher import fetch_game_data
            
            rawg_start = time.time()
            game_data = await fetch_game_data(game_entity, config, cache_only=False)
            rawg_time = (time.time() - rawg_start) * 1000  # ms
            
            if game_data:
                if debug:
                    print(f"[ROUTING] ✅ Données RAWG trouvées: {game_data.get('name')} ({rawg_time:.0f}ms)")
                
                # Formater la réponse basée sur les données RAWG
                factual_response = format_game_answer(game_data, content)
                
                # Sécurité Twitch
                if len(factual_response) > 480:
                    factual_response = factual_response[:477] + "…"
                
                try:
                    await message.channel.send(factual_response)
                    if debug:
                        print(f"[ROUTING] ✅ Réponse RAWG envoyée (0% LLM, 100% factuel)")
                    return
                except Exception as e:
                    print(f"[ROUTING] ❌ Erreur envoi: {e}")
                    return
            else:
                if debug:
                    print(f"[ROUTING] ⚠️ Jeu '{game_entity}' non trouvé dans RAWG, fallback LLM")
        except Exception as e:
            if debug:
                print(f"[ROUTING] ⚠️ Erreur fetch_game_data: {e}, fallback LLM")
    
    # Si pas de jeu détecté, vérifier routing date/sortie (ancien système)
    game_name = await should_route_to_gameinfo(content)
    
    if game_name:
        if debug:
            print(f"[ROUTING] 🎯 Détection date/sortie: '{content[:60]}' → game='{game_name}' ({routing_time:.1f}ms)")
        
        # Appeler handle_game_command directement
        from core.commands.game_command import handle_game_command
        
        igdb_start = time.time()
        await handle_game_command(message, config, game_name, datetime.now())
        igdb_time = (time.time() - igdb_start) * 1000  # ms
        
        if debug:
            print(f"[ROUTING] ✅ IGDB terminé: @{user_name} | game={game_name} | latence={igdb_time:.0f}ms")
        return
    
    if debug:
        print(f"[ROUTING] ⏭️  Pas de routage détecté ({routing_time:.1f}ms) → LLM")
    
    # === Vérifier disponibilité LLM ===
    if not llm_available:
        if debug:
            print(f"[CHILL] 🤖 LLM non disponible → mode fallback")
        
        fallback_msg = get_fallback_response("chill")
        
        try:
            await message.channel.send(fallback_msg)
            if debug:
                print(f"[CHILL] ✅ Fallback envoyé: {fallback_msg}")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi fallback: {e}")
        return
    
    # === LOGIQUE NORMALE (pas de trigger proactif) ===
    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="chill", content=content, user=user_name, game=game, title=title)

    if debug:
        print(f"[LLM] 📝 Prompt: user={user_name} | content='{content[:40]}...' | size={len(prompt)} chars")

    llm_start = time.time()
    response = await call_model(prompt, config, user=user_name, mode="chill")
    llm_time = (time.time() - llm_start) * 1000  # ms

    if debug:
        print(f"[LLM] 📨 Réponse: size={len(response) if response else 0} chars | latence={llm_time:.0f}ms | preview='{response[:60] if response else 'VIDE'}...'")

    # Si tous les LLM ont échoué (LM Studio + OpenAI) → fallback répliques
    if response is None:
        if debug:
            print(f"[CHILL] 🤖 Tous LLM indisponibles → fallback répliques")
        fallback_msg = get_fallback_response("chill")
        try:
            await message.channel.send(f"@{user_name} {fallback_msg}")
            if debug:
                print(f"[CHILL] ✅ Fallback error envoyé: {fallback_msg}")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi fallback: {e}")
        return
    
    if not response:
        await message.channel.send("🤷 Réponse manquante.")
        return

    # Post-filter: détection réponses vagues sur les jeux
    filter_start = time.time()
    vague_redirect = detect_vague_game_response(content, response)
    filter_time = (time.time() - filter_start) * 1000  # ms
    
    if vague_redirect:
        if debug:
            # Extraire game hint du message de redirection
            hint_match = re.search(r'!gameinfo\s*(\w+)?', vague_redirect)
            game_hint = hint_match.group(1) if hint_match and hint_match.group(1) else "(vide)"
            print(f"[POST-FILTER] 🛡️  BLOQUÉ: user='{content[:40]}' | llm='{response[:40]}...' | hint={game_hint} | latence={filter_time:.1f}ms")
        final_response = vague_redirect
    else:
        if debug:
            print(f"[POST-FILTER] ✅ OK: pas de détection ({filter_time:.1f}ms)")
        # Filtre anti-générique (garde la spontanéité du bot)
        filtered = filter_generic_responses(response.strip())
        if not filtered:
            if debug:
                print(f"[CHILL] ⚠️ Réponse générique filtrée: {response[:50]}...")
            filtered = "🤔 Hmm, laisse-moi réfléchir à ça..."

        # Sécurité Twitch (rare mais filet de sécurité)
        final_response = filtered if len(filtered) <= 500 else filtered[:497] + "…"
    
    try:
        send_start = time.time()
        await message.channel.send(final_response)
        send_time = (time.time() - send_start) * 1000  # ms
        
        if debug:
            total_time = routing_time + (llm_time if 'llm_time' in locals() else 0) + (filter_time if 'filter_time' in locals() else 0) + send_time
            print(f"[SEND] ✅ Envoyé: @{user_name} | size={len(final_response)} chars | latence={send_time:.0f}ms")
            print(f"[METRICS] ⏱️  Total: {total_time:.0f}ms (routing={routing_time:.0f} + llm={llm_time if 'llm_time' in locals() else 0:.0f} + filter={filter_time if 'filter_time' in locals() else 0:.0f} + send={send_time:.0f})")
    except Exception as e:
        print(f"[SEND] ❌ Erreur: {e}")
