"""Command handler for !ask - AI-powered question answering."""

import re
from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from utils.model_utils import call_model
from src.utils.cache_manager import get_cached_or_fetch
from src.core.fallbacks import get_fallback_response


async def extract_game_entity(question: str) -> str | None:
    """Extrait le nom d'un jeu potentiel d'une question !ask.
    
    Exemples:
    - "Qui a développé Stardew Valley ?" → "Stardew Valley"
    - "C'est quoi Celeste ?" → "Celeste"
    - "Sur quelles plateformes est Hades ?" → "Hades"
    - "Qui est le président ?" → None
    """
    # Pattern 1: Après "c'est quoi" ou "qu'est-ce que" (prioritaire)
    pattern_quoi = r"(?:c'est quoi|qu'est[- ]ce que)\s+(.+?)(?:\s*\?|$)"
    match = re.search(pattern_quoi, question, re.IGNORECASE)
    if match:
        entity = match.group(1).strip()
        # Nettoyer les articles
        entity = re.sub(r'^(le|la|les|un|une|des)\s+', '', entity, flags=re.IGNORECASE)
        if len(entity) > 2:
            return entity
    
    # Pattern 2: Noms propres consécutifs avec majuscules (pour jeux multi-mots)
    # Ex: "Stardew Valley", "Baldur's Gate", "The Last of Us"
    # Chercher séquence de mots commençant par majuscule + mots minuscules intermédiaires (of, the, etc)
    pattern_multi = r'\b([A-Z][a-z]+(?:[\s\'][A-Z][a-z]+|[\s]+(?:of|the|and|de|du|des)[\s]+[A-Z][a-z]+)+)\b'
    matches = re.findall(pattern_multi, question)
    
    # Filtrer les mots communs (pas des noms de jeux)
    exclude_starts = {'Qui', 'Quoi', 'Comment', 'Quand', 'Quelle', 'Quel'}
    for match in matches:
        first_word = match.split()[0]
        if first_word not in exclude_starts and len(match) > 4:
            return match
    
    # Pattern 3: Nom propre simple (un seul mot avec majuscule)
    # Ex: "Hades", "Celeste", "Minecraft"
    pattern_single = r'\b([A-Z][a-z]{2,})\b'
    matches = re.findall(pattern_single, question)
    
    # Filtrer les mots communs
    exclude_single = {'Qui', 'Quoi', 'Comment', 'Quand', 'Quelle', 'Quel', 'Sur', 'Dans', 'France', 'Paris', 'Est'}
    candidates = [m for m in matches if m not in exclude_single and len(m) > 2]
    
    if candidates:
        # Retourner le premier candidat valide
        return candidates[0]
    
    return None


def format_game_answer(game_data: dict, question: str) -> str:
    """Formate une réponse basée sur les données RAWG et le type de question.
    
    Args:
        game_data: Dict retourné par fetch_game_data()
        question: Question originale de l'utilisateur
    
    Returns:
        Réponse formatée et factuelle
    """
    name = game_data.get("name", "Ce jeu")
    question_lower = question.lower()
    
    # Type 1: Qui a développé/créé ?
    if any(word in question_lower for word in ["développ", "créé", "créa", "fait", "dev", "studio"]):
        devs = game_data.get("developers", [])
        if devs:
            dev_str = " et ".join(devs[:3])  # Max 3 devs pour éviter liste trop longue
            return f"{name} a été développé par {dev_str}."
        else:
            return f"Les développeurs de {name} ne sont pas répertoriés."
    
    # Type 2: Qui a publié/édité ?
    if any(word in question_lower for word in ["publi", "édit", "publisher"]):
        pubs = game_data.get("publishers", [])
        if pubs:
            pub_str = " et ".join(pubs[:3])
            return f"{name} a été publié par {pub_str}."
        else:
            return f"Les éditeurs de {name} ne sont pas répertoriés."
    
    # Type 3: Plateformes ?
    if any(word in question_lower for word in ["plateforme", "console", "pc", "où jouer", "dispo"]):
        platforms = game_data.get("platforms", [])
        if platforms:
            plat_str = ", ".join(platforms[:8])  # Max 8 plateformes
            return f"{name} est disponible sur : {plat_str}."
        else:
            return f"Les plateformes de {name} ne sont pas répertoriées."
    
    # Type 4: Date de sortie ?
    if any(word in question_lower for word in ["sortie", "sorti", "quand", "date", "année"]):
        year = game_data.get("release_year")
        date = game_data.get("release_date")
        if date:
            return f"{name} est sorti le {date}."
        elif year:
            return f"{name} est sorti en {year}."
        else:
            return f"La date de sortie de {name} n'est pas répertoriée."
    
    # Type 5: Genre ?
    if any(word in question_lower for word in ["genre", "type", "catégorie"]):
        genres = game_data.get("genres", [])
        if genres:
            genre_str = ", ".join(genres[:3])
            return f"{name} est un jeu de type {genre_str}."
        else:
            return f"Le genre de {name} n'est pas répertorié."
    
    # Type 6: Note/Score ?
    if any(word in question_lower for word in ["note", "score", "avis", "rating", "metacritic"]):
        metacritic = game_data.get("metacritic")
        rating = game_data.get("rating")
        
        parts = []
        if metacritic:
            parts.append(f"Metacritic: {metacritic}/100")
        if rating:
            parts.append(f"Note RAWG: {rating}/5")
        
        if parts:
            return f"{name} - {', '.join(parts)}."
        else:
            return f"Les notes de {name} ne sont pas disponibles."
    
    # Défaut: Résumé complet (comme !gameinfo mais plus court)
    summary = game_data.get("summary", "")
    devs = game_data.get("developers", [])
    year = game_data.get("release_year")
    
    response = f"{name}"
    if year:
        response += f" ({year})"
    if devs:
        response += f" - développé par {', '.join(devs[:2])}"
    if summary:
        # Prendre première phrase du summary (max 200 chars)
        first_sentence = summary.split('.')[0][:200]
        response += f". {first_sentence}."
    
    return response


async def handle_ask_command(message: Message, config: dict, question: str, now, llm_available: bool = True):  # pylint: disable=unused-argument
    """Handle the !ask command to answer user questions using AI.
    
    Args:
        message: Message Twitch reçu
        config: Configuration du bot
        question: Question de l'utilisateur
        now: Timestamp actuel
        llm_available: Si le LLM est disponible (défaut: True pour rétrocompatibilité)
    """
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)

    if not question.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de poser ta question après `!ask`."
        )
        if debug:
            print(f"[ASK] ⚠️ Question vide reçue de @{user}")
        return

    if debug:
        print(f"[ASK] 🔎 Traitement de la question de @{user}...")

    # === NOUVELLE STRATÉGIE: Essayer d'abord de détecter un jeu vidéo ===
    game_entity = await extract_game_entity(question)
    
    if game_entity:
        if debug:
            print(f"[ASK] 🎮 Entité jeu détectée: '{game_entity}'")
            print(f"[ASK] 🧠 Décision: RAWG (jeu détecté)")
        
        # Tenter de récupérer les données du jeu via RAWG (avec cache)
        try:
            from src.core.commands.api.game_data_fetcher import fetch_game_data
            
            game_data = await fetch_game_data(game_entity, config, cache_only=False)
            
            if game_data:
                if debug:
                    print(f"[ASK] ✅ Données jeu trouvées via RAWG: {game_data.get('name')}")
                
                # Formater la réponse basée sur les données RAWG
                factual_response = format_game_answer(game_data, question)
                
                # Sécurité Twitch
                if len(factual_response) > 480:
                    factual_response = factual_response[:477] + "…"
                
                try:
                    if debug:
                        print(f"[ASK] 📤 Réponse factuelle RAWG: {factual_response[:100]}...")
                    await message.channel.send(f"@{user} {factual_response}")
                    if debug:
                        print(f"[ASK] ✅ Réponse RAWG envoyée (0% LLM, 100% factuel)")
                    return
                except Exception as e:
                    print(f"[ASK] ❌ Erreur envoi: {e}")
                    return
            else:
                if debug:
                    print(f"[ASK] ⚠️ Jeu '{game_entity}' non trouvé dans RAWG")
                    print(f"[ASK] 🧠 Décision: Fallback Wikipedia/LLM")
        except Exception as e:
            if debug:
                print(f"[ASK] ⚠️ Erreur fetch_game_data: {e}")
                print(f"[ASK] 🧠 Décision: Fallback Wikipedia/LLM")
    else:
        if debug:
            print(f"[ASK] 🧠 Décision: LLM (hors-jeu)")
    
    # === FALLBACK 1: Cache Wikipedia ===
    cached_answer = await get_cached_or_fetch(question)
    if cached_answer:
        if debug:
            print(f"[ASK] 💡 Réponse depuis cache/Wikipedia")
        
        # Sécurité Twitch (500 chars max absolu avec @mention)
        final_response = cached_answer.strip()
        if len(final_response) > 480:
            final_response = final_response[:477] + "…"
        
        try:
            if debug:
                print(f"[SEND] 📤 Envoi CACHE: {final_response[:100]}...")
            await message.channel.send(f"@{user} {final_response}")
            if debug:
                print(f"[SEND] ✅ Envoyé avec succès (cache)")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi: {e}")
        return

    # === FALLBACK 2: Appel au modèle LLM (dernier recours) ===
    # Vérifier si le LLM est disponible
    if not llm_available:
        if debug:
            print(f"[ASK] 🤖 LLM non disponible → mode fallback")
        
        fallback_msg = get_fallback_response("ask")
        
        try:
            await message.channel.send(f"@{user} {fallback_msg}")
            if debug:
                print(f"[ASK] ✅ Fallback envoyé: {fallback_msg}")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi fallback: {e}")
        return
    
    if debug:
        print(f"[ASK] 🤖 Appel modèle LLM (dernier recours)...")
    
    # Récupérer game/title depuis config (si disponible)
    game = config.get("stream", {}).get("game")
    title = config.get("stream", {}).get("title")

    # Construire le prompt avec make_prompt
    prompt = make_prompt(mode="ask", content=question, user=user, game=game, title=title)
    
    if debug:
        print(f"[ASK] 📝 USER Prompt ({len(prompt)} chars): {prompt[:150]}{'...' if len(prompt) > 150 else ''}")
    
    response = await call_model(prompt, config, user=user, mode="ask")

    if not response:
        await message.channel.send(f"@{user} ⚠️ Erreur ou pas de réponse.")
        return

    # Sécurité Twitch (500 chars max absolu avec @mention)
    final_response = response.strip()
    if len(final_response) > 480:
        final_response = final_response[:477] + "…"

    try:
        if debug:
            print(f"[SEND] 📤 Envoi ASK LLM: {final_response[:100]}...")
        await message.channel.send(f"@{user} {final_response}")
        if debug:
            print(f"[ASK] ✅ Réponse LLM envoyée à @{user}")
    except Exception as e:
        print(f"[ASK] ❌ Erreur d'envoi: {e}")
