"""
Command handler for game information lookup.

Version refactorée avec RAWG comme source prioritaire.
Architecture propre avec séparation des responsabilités.
"""

import json
import re

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from core.cache import GAME_CACHE, get_cache_key, get_ttl_for_game
from utils.game_utils import compress_platforms, normalize_platforms
from utils.translator import Translator

from .api import fetch_game_data  # Nouveau module API centralisé


async def handle_game_command(message: Message, config: dict, game_name: str, now, bot=None):  # pylint: disable=unused-argument
    """
    Handler de la commande !gameinfo - Version refactorée.
    
    Délègue la récupération des données à api.fetch_game_data()
    qui gère la priorité RAWG → IGDB → Web scraping.
    
    Args:
        message: Message Twitch
        config: Configuration globale du bot
        game_name: Nom du jeu recherché
        now: Timestamp actuel (pour cooldown, unused)
        bot: Instance du bot (pour safe_send avec badge)
    """
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    cooldown = config["bot"].get("cooldown", 60)

    # Validation
    if not game_name.strip():
        if bot:
            await bot.safe_send(message.channel, f"@{user} Tu as oublié de spécifier un jeu. Utilise `!gameinfo nom_du_jeu`.")
        else:
            await message.channel.send(f"@{user} Tu as oublié de spécifier un jeu. Utilise `!gameinfo nom_du_jeu`.")
        if debug:
            print(f"[GAME] ⚠️ Requête vide ignorée de @{user}")
        return

    # 🔍 VÉRIFICATION DU CACHE (données traduites + compteur de hits)
    cache_key = get_cache_key("gamedata", game_name)
    cached_entry = GAME_CACHE.get(cache_key)
    
    hit_count = 1  # Première recherche par défaut
    
    if cached_entry:
        if debug:
            print(f"[GAME] ⚡ Cache HIT pour '{game_name}'")
        data = cached_entry["data"]
        hit_count = cached_entry.get("hit_count", 1) + 1
        
        # Mettre à jour le compteur dans le cache
        cached_entry["hit_count"] = hit_count
        release_year = data.get("release_year", "9999")
        ttl = get_ttl_for_game(release_year)
        GAME_CACHE.set(cache_key, cached_entry, ttl=ttl)
        
        if debug:
            print(f"[GAME] 📊 Popularité: {hit_count}× demandé")
    else:
        if bot:
            await bot.safe_send(message.channel, "🎮 Recherche du jeu...")
        else:
            await message.channel.send("🎮 Recherche du jeu...")
        
        try:
            # 🔥 RÉCUPÉRATION via le nouveau module API (RAWG prioritaire)
            data = await fetch_game_data(game_name, config)

            if not data:
                if bot:
                    await bot.safe_send(message.channel, f"@{user} 🤔 Aucun jeu trouvé pour '{game_name}'. T'es sûr du nom ?")
                else:
                    await message.channel.send(f"@{user} 🤔 Aucun jeu trouvé pour '{game_name}'. T'es sûr du nom ?")
                if debug:
                    print(f"[GAME] ❌ Aucun résultat pour '{game_name}'")
                return

            if debug:
                debug_data = {k: v for k, v in data.items() if k not in ["summary", "background_image"]}
                print(
                    "[GAME] 🔎 Données brutes API (hors summary) :\n"
                    + json.dumps(debug_data, indent=2, ensure_ascii=False)
                )

            # 💾 MISE EN CACHE des données + compteur (pas de traduction summary)
            cache_entry = {
                "data": data,
                "hit_count": 1
            }
            release_year = data.get("release_year", "9999")
            ttl = get_ttl_for_game(release_year)
            GAME_CACHE.set(cache_key, cache_entry, ttl=ttl)
            
            if debug:
                print(f"[GAME] 💾 Mis en cache '{game_name}' (TTL: {ttl}s)")
        
        except (RuntimeError, ValueError, KeyError, TypeError) as e:
            if bot:
                await bot.safe_send(message.channel, f"@{user} 🔌 Désolé, j'ai pas accès à ma base de données jeux pour le moment ! 🎮💤")
            else:
                await message.channel.send(f"@{user} 🔌 Désolé, j'ai pas accès à ma base de données jeux pour le moment ! 🎮💤")
            print(f"❌ [GAME] Exception API : {e}")
            return
    
    # 🌍 TRADUCTION du summary si nécessaire (après cache, avant formatage)
    summary = data.get('summary', '')
    if summary:
        # Détecter si c'est de l'anglais (heuristique simple)
        is_english = _detect_english(summary)
        
        if is_english:
            if debug:
                print(f"[GAME] 🌍 Summary détecté en anglais, traduction...")
            
            try:
                translator = Translator()
                translated = translator.translate(summary, source='en', target='fr')
                
                if translated and not translated.startswith('⚠️'):
                    data['summary'] = translated
                    if debug:
                        print(f"[GAME] ✅ Summary traduit: {translated[:80]}...")
                else:
                    if debug:
                        print(f"[GAME] ⚠️ Traduction échouée, garde l'anglais")
            except Exception as e:
                print(f"[GAME] ❌ Erreur traduction: {e}")
        else:
            if debug:
                print(f"[GAME] ✅ Summary déjà en français")
    
    # 📊 FORMATAGE du message (toujours refait pour avoir le bon @user)
    try:
        result = await _format_game_message(data, user, config, debug, cooldown, hit_count)
        
        if debug:
            print(f"[GAME] 📝 Message formaté: {result['main'][:100]}...")
            print(f"[GAME] 📏 Longueur: {len(result['main'])} chars")
            print(f"[GAME] 📺 Channel: {message.channel.name}")
            print(f"[GAME] 🔍 Message complet:\n{result['main']}")
        
        # 📤 ENVOI (message principal + description si disponible)
        if bot:
            await bot.safe_send(message.channel, result["main"])
            # Envoyer la description sur une 2ème ligne si présente
            if result.get("description"):
                await bot.safe_send(message.channel, result["description"])
        else:
            await message.channel.send(result["main"])
            # Envoyer la description sur une 2ème ligne si présente
            if result.get("description"):
                await message.channel.send(result["description"])
        
        if debug:
            print(f"[GAME] ✅ Message envoyé sur Twitch (channel: {message.channel.name})")
            if result.get("description"):
                print(f"[GAME] ✅ Description envoyée: {result['description'][:80]}...")
    
    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        if bot:
            await bot.safe_send(message.channel, f"@{user} 🔌 Ma connexion aux infos jeux marche pas. Désolé ! (erreur formatage)")
        else:
            await message.channel.send(f"@{user} 🔌 Ma connexion aux infos jeux marche pas. Désolé ! (erreur formatage)")
        print(f"❌ [GAME] Exception formatage : {e}")


async def _format_game_message(
    data: dict, 
    user: str, 
    config: dict, 
    debug: bool,
    cooldown: int,
    hit_count: int = 1
) -> dict:
    """
    Formate les données du jeu en message Twitch optimisé.
    
    IMPORTANT: Le summary est déjà traduit dans data["summary"] avant l'appel !
    
    Gère :
    - Formatage des notes/ratings (Metacritic, RAWG)
    - Compression des plateformes
    - Troncature intelligente de la description
    - Construction du message principal
    
    Args:
        data: Données normalisées ET TRADUITES du jeu (depuis RAWG ou IGDB)
        user: Nom de l'utilisateur Twitch
        config: Configuration du bot (unused mais gardé pour compatibilité)
        debug: Mode debug activé
        cooldown: Cooldown en secondes
    
    Returns:
        Dict avec {"main": str, "description": str | None}
    """
    # Extraction des données (summary est déjà traduit !)
    name = data.get("name", "Inconnu")
    summary = data.get("summary", "")  # Déjà traduit et nettoyé
    slug = data.get("slug", "")
    release_year = data.get("release_year", "?")
    
    # Notes et ratings (seulement si RAWG)
    metacritic = data.get("metacritic")
    rating = data.get("rating")
    ratings_count = data.get("ratings_count", 0)
    
    # Developers et Publishers (seulement si RAWG)
    developers = data.get("developers", [])
    publishers = data.get("publishers", [])
    
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
    
    # Construire le message principal (ligne 1 + ratings sur même ligne)
    message_main = base
    if rating_line:
        message_main += f" | {rating_line}"
    
    # Suffix avec cooldown et popularité
    if hit_count > 1:
        message_main += f" ({hit_count}× demandé, {cooldown}s)"
    else:
        message_main += f" ({cooldown}s)"
    
    # Nettoyer le summary des artefacts de traduction
    # Supprimer les marqueurs de section (###, ##, etc.)
    summary = re.sub(r'#{1,6}\s*\w+', '', summary)
    summary = summary.strip()
    
    # Message de description (séparé, max 400 chars)
    max_summary_chars = 400
    if len(summary) > max_summary_chars:
        cut_dot = summary[:max_summary_chars].rfind(". ")
        cut_comma = summary[:max_summary_chars].rfind(", ")
        
        if cut_dot > 100:
            summary = summary[:cut_dot + 1].strip()
        elif cut_comma > 100:
            summary = summary[:cut_comma + 1].strip()
        else:
            summary = summary[:max_summary_chars].strip() + "…"
    
    # Retourner dict avec 2 messages au lieu d'un seul
    result = {
        "main": message_main,
        "description": f"📝 {summary}" if summary else None
    }
    
    # Métriques
    total_len = len(message_main) + (len(summary) if summary else 0)
    total_tokens = total_len // 4
    print(f"[METRICS-GAME] 📤 Message total: {total_len} chars (~{total_tokens} tokens)")
    
    if debug:
        print(f"[GAME] ✅ Jeu: {name} ({release_year})")
        print(f"[GAME] Plateformes: {platforms}")
        if metacritic:
            print(f"[GAME] Metacritic: {metacritic}/100")
        if rating:
            print(f"[GAME] Rating: {rating}/5 ({ratings_count} avis)")
    
    return result


def _detect_english(text: str) -> bool:
    """
    Détecte si un texte est en anglais (heuristique simple).
    
    Vérifie la présence de mots anglais courants absents du français.
    Plus précis qu'une détection de langue complète pour ce cas.
    
    Args:
        text: Texte à analyser
    
    Returns:
        True si probablement anglais, False sinon
    """
    if not text or len(text) < 20:
        return False
    
    text_lower = text.lower()
    
    # Mots anglais courants dans les descriptions de jeux
    english_indicators = [
        ' the ', ' you ', ' your ', ' with ', ' from ',
        ' this ', ' that ', ' have ', ' will ', ' can ',
        ' game ', ' play ', ' world ', ' story '
    ]
    
    # Mots français uniques (absents en anglais)
    french_indicators = [
        ' le ', ' la ', ' les ', ' des ', ' vous ',
        ' dans ', ' avec ', ' pour ', ' sur ', ' est '
    ]
    
    english_count = sum(1 for word in english_indicators if word in text_lower)
    french_count = sum(1 for word in french_indicators if word in text_lower)
    
    # Si plus de mots anglais que français → probablement anglais
    return english_count > french_count
