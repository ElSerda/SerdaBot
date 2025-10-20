"""
Command handler for game information lookup.

Version refactorée avec RAWG comme source prioritaire.
Architecture propre avec séparation des responsabilités.
"""

import json

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game
from utils.game_utils import compress_platforms, normalize_platforms, sanitize_slug
from utils.translator import Translator

from .api import fetch_game_data  # Nouveau module API centralisé


def clean_translation(text: str) -> str:
    """Clean common translation mistakes in French game descriptions."""
    replacements = {
        "plateforme super étanche": "jeu de plateforme",
        "secrets dérisoires": "secrets cachés",
        "rassemble le mystère": "découvre les mystères",
        "défis réalisés à la main": "niveaux faits main",
        "ouvert-monde": "monde ouvert",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text


async def handle_game_command(message: Message, config: dict, game_name: str, now):  # pylint: disable=unused-argument
    """
    Handler de la commande !gameinfo - Version refactorée.
    
    Délègue la récupération des données à api.fetch_game_data()
    qui gère la priorité RAWG → IGDB → Web scraping.
    
    Args:
        message: Message Twitch
        config: Configuration globale du bot
        game_name: Nom du jeu recherché
        now: Timestamp actuel (pour cooldown, unused)
    """
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)

    # Validation
    if not game_name.strip():
        await message.channel.send(
            f"@{user} Tu as oublié de spécifier un jeu. Utilise `!gameinfo nom_du_jeu`."
        )
        if debug:
            print(f"[GAME] ⚠️ Requête vide ignorée de @{user}")
        return

    # 🔍 VÉRIFICATION DU CACHE
    cache_key = get_cache_key("gameinfo", game_name)
    cached_message = GAME_CACHE.get(cache_key)
    
    if cached_message:
        if debug:
            print(f"[GAME] ⚡ Cache HIT pour '{game_name}'")
        await message.channel.send(cached_message)
        return

    await message.channel.send("🎮 Recherche du jeu...")
    
    try:
        # 🔥 RÉCUPÉRATION via le nouveau module API (RAWG prioritaire)
        data = await fetch_game_data(game_name, config)

        if not data:
            await message.channel.send(f"❌ Jeu introuvable : {game_name}")
            if debug:
                print(f"[GAME] ❌ Aucun résultat pour '{game_name}'")
            return

        if debug:
            debug_data = {k: v for k, v in data.items() if k not in ["summary", "background_image"]}
            print(
                "[GAME] 🔎 Données brutes API (hors summary) :\n"
                + json.dumps(debug_data, indent=2, ensure_ascii=False)
            )

        # 📊 FORMATAGE du message
        message_text = await _format_game_message(data, user, config, debug, cooldown)
        
        # � MISE EN CACHE avec TTL adapté
        release_year = data.get("release_year", "9999")
        ttl = get_ttl_for_game(release_year)
        GAME_CACHE.set(cache_key, message_text, ttl=ttl)
        
        if debug:
            print(f"[GAME] 💾 Mis en cache '{game_name}' (TTL: {ttl}s)")
        
        # �📤 ENVOI
        await message.channel.send(message_text)

    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        await message.channel.send(f"@{user} ⚠️ Erreur lors du traitement.")
        print(f"❌ [GAME] Exception : {e}")


async def _format_game_message(
    data: dict, 
    user: str, 
    config: dict, 
    debug: bool,
    cooldown: int
) -> str:
    """
    Formate les données du jeu en message Twitch optimisé.
    
    Gère :
    - Traduction EN→FR si nécessaire
    - Formatage des notes/ratings (Metacritic, RAWG)
    - Compression des plateformes
    - Troncature intelligente de la description
    - Construction du message final (<500 chars)
    
    Args:
        data: Données normalisées du jeu (depuis RAWG ou IGDB)
        user: Nom de l'utilisateur Twitch
        config: Configuration du bot
        debug: Mode debug activé
        cooldown: Durée du cooldown à afficher
    
    Returns:
        Message formaté prêt à envoyer sur Twitch
    """
    translator = Translator()
    
    # Extraction des données
    name = data.get("name", "Inconnu")
    summary_raw = data.get("summary", "")
    slug = data.get("slug", "")
    release_year = data.get("release_year", "?")
    
    # Notes et ratings (seulement si RAWG)
    metacritic = data.get("metacritic")
    rating = data.get("rating")
    ratings_count = data.get("ratings_count", 0)
    
    # Developers et Publishers (seulement si RAWG)
    developers = data.get("developers", [])
    publishers = data.get("publishers", [])
    
    # URL IGDB (pour compatibilité)
    igdb_url = f"https://www.igdb.com/games/{sanitize_slug(slug or name)}"
    
    # 🌐 TRADUCTION du résumé si nécessaire
    summary = summary_raw
    try:
        # Détection simple: si mots anglais présents
        if any(word in summary.lower() for word in ['the', 'and', 'you', 'with', 'for', 'this', 'that']):
            input_len = len(summary)
            input_tokens = input_len // 4
            print(f"[METRICS-GAME] 🌐 Traduction EN→FR: {input_len} chars (~{input_tokens} tokens)")

            result = translator.translate(summary, source='en', target='fr')
            if result and not result.startswith('⚠️'):
                summary = result
                output_len = len(summary)
                output_tokens = output_len // 4
                print(f"[METRICS-GAME] ✅ Traduit: {output_len} chars (~{output_tokens} tokens)")
            else:
                print("[METRICS-GAME] ⚠️ Traduction échouée, texte original conservé")
                
    except (RuntimeError, ValueError, KeyError) as e:
        if debug:
            print(f"[GAME] ⚠️ Translation error: {e}")
    
    # Nettoyage des erreurs de traduction courantes
    summary = clean_translation(summary)
    
    # 📝 CONSTRUCTION DU MESSAGE
    # Ligne 1: @user 🎮 NomDuJeu (année), plateformes
    base = f"@{user} 🎮 {name}"
    base += f" ({release_year})" if release_year != "?" else " (date inconnue)"
    
    # Plateformes
    platforms = compress_platforms(normalize_platforms(data.get("platforms", [])))
    base += f", {', '.join(platforms)}" if platforms else ", plateformes inconnues"
    
    # Developers et Publishers (si disponibles)
    if developers:
        dev_str = ", ".join(developers[:2])  # Max 2 devs
        base += f" | Dev: {dev_str}"
    if publishers:
        pub_str = ", ".join(publishers[:2])  # Max 2 publishers
        base += f" | Pub: {pub_str}"
    
    # Ligne 2 (optionnelle): Notes et ratings
    rating_line = ""
    if metacritic or rating:
        rating_parts = []
        if metacritic:
            rating_parts.append(f"⭐ Metacritic: {metacritic}/100")
        if rating:
            rating_parts.append(f"Note: {rating}/5")
            if ratings_count > 0:
                # Afficher le nombre d'avis de manière compacte
                if ratings_count >= 1000:
                    count_str = f"{ratings_count // 1000}k"
                else:
                    count_str = str(ratings_count)
                rating_parts[-1] += f" ({count_str} avis)"
        
        rating_line = " | ".join(rating_parts)
        if rating_line:
            rating_line = "\n" + rating_line
    
    # Suffix avec lien et cooldown
    suffix = f" ({igdb_url}) ({cooldown}s)"
    
    # Calcul de l'espace disponible pour la description
    max_chars = 500 - len(base) - len(rating_line) - len(suffix) - 5  # Marge de sécurité
    
    # Troncature intelligente de la description
    if len(summary) > max_chars:
        cut_dot = summary[:max_chars].rfind(". ")
        cut_comma = summary[:max_chars].rfind(", ")
        
        if cut_dot > 100:
            summary = summary[:cut_dot + 1].strip()
        elif cut_comma > 100:
            summary = summary[:cut_comma + 1].strip()
        else:
            summary = summary[:max_chars].strip() + "…"
    
    # Message final
    final = f"{base}{rating_line} :\n{summary}{suffix}"
    
    # Métriques
    final_len = len(final)
    final_tokens = final_len // 4
    print(f"[METRICS-GAME] 📤 Message final: {final_len} chars (~{final_tokens} tokens)")
    
    if debug:
        print(f"[GAME] ✅ Jeu: {name} ({release_year})")
        print(f"[GAME] Plateformes: {platforms}")
        if metacritic:
            print(f"[GAME] Metacritic: {metacritic}/100")
        if rating:
            print(f"[GAME] Rating: {rating}/5 ({ratings_count} avis)")
    
    return final
