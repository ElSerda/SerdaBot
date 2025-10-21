"""Commande !chill - Mode conversationnel"""

import asyncio
import re
import time

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from prompts.prompt_loader import make_prompt
from src.core.fallbacks import get_fallback_response
from utils.model_utils import call_model


def detect_and_translate_artifacts(response: str, translator, debug: bool = False) -> tuple[str, bool, str, str]:
    """
    Détecte les caractères chinois dans la réponse et ajoute leur traduction entre parenthèses.
    
    Exemple: "C'est une百科全书!" → "C'est une百科全书 (encyclopédie)!"
    
    Args:
        response: Réponse du LLM
        translator: Instance du Translator pour la traduction
        debug: Mode debug pour logs
    
    Returns:
        Tuple (response_filtrée, has_artifact, premier_mot_chinois, traduction)
    """
    # Pattern pour détecter les caractères chinois
    chinese_pattern = r'([\u4e00-\u9fff]+)'
    
    # Variables pour tracker le premier artefact
    first_chinese = None
    first_translation = None
    has_artifact = False
    
    # Fonction de remplacement appelée pour chaque match
    def add_translation(match):
        nonlocal first_chinese, first_translation, has_artifact
        chinese_word = match.group(1)
        translation = translator.translate_chinese(chinese_word)
        
        # Capturer le premier artefact pour la félicitation
        if not has_artifact:
            first_chinese = chinese_word
            first_translation = translation
            has_artifact = True
        
        if debug:
            print(f"[ARTIFACT] 🀄 Détecté: '{chinese_word}' → '{translation}'")
        
        # Injecter la traduction juste après le mot chinois
        return f"{chinese_word} ({translation})"
    
    # Remplacer chaque occurrence de caractères chinois
    filtered_response = re.sub(chinese_pattern, add_translation, response)
    
    # Log si des artefacts ont été détectés
    if has_artifact and debug:
        print(f"[ARTIFACT] ✅ Filtre appliqué: {response[:50]}... → {filtered_response[:50]}...")
        print(f"[ARTIFACT] 🎓 Easter egg détecté: '{first_chinese}' = '{first_translation}'")
    
    return filtered_response, has_artifact, first_chinese or "", first_translation or ""


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


async def handle_chill_command(message: Message, config: dict, now, conversation_manager=None, llm_available: bool = True, bot=None, translator=None):  # pylint: disable=unused-argument
    """Commande !chill - Répond en mode conversationnel.
    
    Args:
        message: Message Twitch
        config: Configuration du bot
        now: Timestamp actuel
        conversation_manager: Gestionnaire de conversation (optionnel)
        llm_available: Si le LLM est disponible (défaut: True pour rétrocompatibilité)
        bot: Instance du bot (pour safe_send avec badge)
        translator: Instance du Translator (pour filtre artefacts multilingues)
    """
    botname = config["bot"]["name"].lower()
    debug = config["bot"].get("debug", False)
    user_name = str(message.author.name or "user").lower()
    
    # Helper pour envoyer avec ou sans badge
    async def send(msg):
        if bot:
            await bot.safe_send(message.channel, msg)
        else:
            await message.channel.send(msg)

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

    # === MODE CHILL: PAS DE ROUTING ===
    # En mode CHILL (conversation casual), on va TOUJOURS au LLM direct
    # Le routing est réservé au mode ASK (!ask) pour les questions factuelles
    if debug:
        print("[CHILL] 💬 Mode conversation → LLM direct (pas de routing)")
    
    # === Vérifier disponibilité LLM ===
    if not llm_available:
        if debug:
            print(f"[CHILL] 🤖 LLM non disponible → mode fallback")
        
        fallback_msg = get_fallback_response("chill")
        
        try:
            await send(fallback_msg)
            if debug:
                print(f"[CHILL] ✅ Fallback envoyé: {fallback_msg}")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi fallback: {e}")
        return
    
    # === CONTEXTE CONVERSATIONNEL ===
    # Récupérer l'historique des 3 derniers messages de cet utilisateur
    conversation_history = []
    if conversation_manager:
        state = conversation_manager.get(user_name)
        with state.lock:
            # Garder les 3 derniers messages (user + assistant)
            conversation_history = state.messages[-6:] if len(state.messages) > 0 else []
            if debug and conversation_history:
                print(f"[CONTEXT] 💬 {len(conversation_history)} messages d'historique pour {user_name}")
    
    # === LOGIQUE NORMALE (pas de trigger proactif) ===
    # Construire le prompt avec make_prompt + contexte
    if conversation_history:
        # Construire un contexte texte pour le prompt
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        prompt = make_prompt(mode="chill", content=f"[Contexte conversation]\n{context_text}\n\n[Message actuel]\n{content}", user=user_name, game=game, title=title)
    else:
        prompt = make_prompt(mode="chill", content=content, user=user_name, game=game, title=title)

    if debug:
        print(f"[LLM] 📝 Prompt: user={user_name} | content='{content[:40]}...' | size={len(prompt)} chars | historique={len(conversation_history)} msg")

    llm_start = time.time()
    response = await call_model(prompt, config, user=user_name, mode="chill")
    llm_time = (time.time() - llm_start) * 1000  # ms

    if debug:
        print(f"[LLM] 📨 Réponse: size={len(response) if response else 0} chars | latence={llm_time:.0f}ms | preview='{response[:60] if response else 'VIDE'}...'")

    # === FILTRE ARTEFACTS MULTILINGUES ===
    has_artifact = False
    chinese_word = ""
    translation = ""
    if response and translator:
        response, has_artifact, chinese_word, translation = detect_and_translate_artifacts(response, translator, debug)

    # === SAUVEGARDER DANS L'HISTORIQUE ===",
    if conversation_manager and response:
        conversation_manager.add_message(user_name, "user", content)
        conversation_manager.add_message(user_name, "assistant", response)
        if debug:
            print(f"[CONTEXT] 💾 Messages sauvegardés pour {user_name}")

    # Si tous les LLM ont échoué (LM Studio + OpenAI) → fallback répliques
    if response is None:
        if debug:
            print(f"[CHILL] 🤖 Tous LLM indisponibles → fallback répliques")
        fallback_msg = get_fallback_response("chill")
        try:
            await send(f"@{user_name} {fallback_msg}")
            if debug:
                print(f"[CHILL] ✅ Fallback error envoyé: {fallback_msg}")
        except Exception as e:
            print(f"[SEND] ❌ Erreur envoi fallback: {e}")
        return
    
    if not response:
        await send("🤷 Réponse manquante.")
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
        await send(final_response)
        send_time = (time.time() - send_start) * 1000  # ms
        
        if debug:
            total_time = (llm_time if 'llm_time' in locals() else 0) + (filter_time if 'filter_time' in locals() else 0) + send_time
            print(f"[SEND] ✅ Envoyé: @{user_name} | size={len(final_response)} chars | latence={send_time:.0f}ms")
            print(f"[METRICS] ⏱️  Total: {total_time:.0f}ms (llm={llm_time if 'llm_time' in locals() else 0:.0f} + filter={filter_time if 'filter_time' in locals() else 0:.0f} + send={send_time:.0f})")
        
        # === EASTER EGG: FÉLICITATION RETARDÉE SI ARTEFACT CHINOIS ===
        if has_artifact and chinese_word and translation:
            if debug:
                print(f"[ARTIFACT] ⏳ Attente 3s avant félicitation...")
            
            await asyncio.sleep(3)  # Suspense de 3 secondes
            
            congrats_msg = f"🎓 @{user_name} Wow ! Tu viens d'unlock un easter egg chinois : {chinese_word} = {translation} !"
            try:
                await send(congrats_msg)
                if debug:
                    print(f"[ARTIFACT] 🎉 Félicitation envoyée: {congrats_msg}")
            except Exception as e:
                print(f"[SEND] ❌ Erreur envoi félicitation: {e}")
    except Exception as e:
        print(f"[SEND] ❌ Erreur: {e}")
