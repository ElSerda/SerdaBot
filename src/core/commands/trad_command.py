from datetime import datetime

from twitchio import Message

from utils.translation_utils import detect_language, translate_text

# Cooldown par utilisateur (datetime)
user_cooldowns = {}
# Statistiques globales
translation_stats = {
    "total_requests": 0,
    "per_user": {},
}


async def handle_trad_command(message: Message, config: dict, user_input: str, now: datetime):
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)
    default_lang = config["bot"].get("language", "fr")
    cooldown_sec = config["bot"].get("cooldown", 10)

    if not user_input.strip():
        await message.channel.send(f"@{user} ⚠️ Tu dois fournir un texte à traduire.")
        return

    # Gérer le cooldown par utilisateur
    last_time = user_cooldowns.get(user)
    if last_time and (now - last_time).total_seconds() < cooldown_sec:
        await message.channel.send(f"@{user} ⏳ Merci de patienter avant une autre traduction.")
        return
    user_cooldowns[user] = now

    # Gestion de la langue cible
    words = user_input.strip().split()
    if len(words) > 1 and len(words[0]) == 2:
        target_lang = words[0]
        text_to_translate = " ".join(words[1:])
    else:
        target_lang = default_lang
        text_to_translate = user_input.strip()

    # Détection de la langue source
    src_lang = detect_language(text_to_translate)
    if src_lang == target_lang:
        await message.channel.send(
            f"@{user} ⚠️ Ton message est déjà en {target_lang}. Utilise !trad [lang] ton message pour choisir une autre langue."
        )
        return

    # Temps de traitement
    start_time = datetime.now()
    translated = translate_text(text_to_translate, src_lang, target_lang)
    duration = (datetime.now() - start_time).total_seconds()

    # Réponse utilisateur
    await message.channel.send(f"@{user} 🈯 Traduction ({src_lang} → {target_lang}) : {translated}")

    # Logs / Historique
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] @{user}: ({src_lang}->{target_lang}) '{text_to_translate}' => '{translated}' [{duration:.2f}s]\n"
    with open("logs/traductions.log", "a", encoding="utf-8") as f:
        f.write(log_line)

    # Statistiques
    translation_stats["total_requests"] += 1
    translation_stats["per_user"].setdefault(user, 0)
    translation_stats["per_user"][user] += 1

    # Debug
    if debug:
        print(f"[TRAD] {log_line.strip()}")
        print(f"[STATS] Total: {translation_stats['total_requests']} | {user}: {translation_stats['per_user'][user]}")
