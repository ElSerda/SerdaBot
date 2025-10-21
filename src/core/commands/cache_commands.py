"""Admin command to manage fact cache."""

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]

from utils.cache_manager import add_to_cache, clear_cache, get_cache_stats


async def handle_cacheadd_command(message: Message, config: dict, args: str):
    """Admin command: !cacheadd <query> | <answer>"""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    
    # Vérifier si l'utilisateur est dev/admin
    devs = config.get("bot", {}).get("devs", [])
    if user not in devs:
        if debug:
            print(f"[CACHEADD] ⛔ {user} n'est pas autorisé")
        return
    
    # Parse args: "query | answer"
    if "|" not in args:
        await message.channel.send(f"@{user} Format: !cacheadd <question> | <réponse>")
        return
    
    parts = args.split("|", 1)
    query = parts[0].strip()
    answer = parts[1].strip()
    
    if not query or not answer:
        await message.channel.send(f"@{user} Question et réponse requises.")
        return
    
    # Ajouter au cache
    success = add_to_cache(query, answer)
    
    if success:
        await message.channel.send(f"@{user} ✅ Ajouté au cache: '{query[:30]}...'")
        if debug:
            print(f"[CACHEADD] ✅ {user} ajouté: {query} -> {answer[:50]}")
    else:
        await message.channel.send(f"@{user} ❌ Réponse invalide (trop courte ou 'Je ne sais pas')")


async def handle_cachestats_command(message: Message, config: dict):
    """Admin command: !cachestats"""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    
    # Vérifier si l'utilisateur est dev/admin
    devs = config.get("bot", {}).get("devs", [])
    if user not in devs:
        if debug:
            print(f"[CACHESTATS] ⛔ {user} n'est pas autorisé")
        return
    
    stats = get_cache_stats()
    await message.channel.send(
        f"@{user} 📊 Cache: {stats['total_entries']} faits | {stats['cache_file']}"
    )


async def handle_cacheclear_command(message: Message, config: dict):
    """Admin command: !cacheclear (DANGER)"""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    
    # Vérifier si l'utilisateur est dev/admin
    devs = config.get("bot", {}).get("devs", [])
    if user not in devs:
        if debug:
            print(f"[CACHECLEAR] ⛔ {user} n'est pas autorisé")
        return
    
    clear_cache()
    await message.channel.send(f"@{user} 🗑️ Cache vidé complètement.")
    if debug:
        print(f"[CACHECLEAR] ⚠️ {user} a vidé le cache")
