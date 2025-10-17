"""Command handler for donation/support commands."""

from twitchio import Message  # pyright: ignore[reportPrivateImportUsage]


async def handle_donation_command(message: Message, config: dict, now):  # pylint: disable=unused-argument
    """Gère les commandes de donation/support"""
    user = (message.author.name or "user").lower()
    debug = config["bot"].get("debug", False)

    # URLs de donation/support
    kofi_url = config["bot"].get("kofi_url", "https://ko-fi.com/your_username")
    donation_message = config["bot"].get("donation_message",
        "☕ Merci pour le support ! Tu peux soutenir le stream ici : {kofi_url} 💜")

    if debug:
        print(f"[DONATION] 💰 Commande donation appelée par @{user}")

    # Formater le message avec l'URL
    final_message = donation_message.format(kofi_url=kofi_url)

    # Limiter la longueur (au cas où)
    if len(final_message) > 500:
        final_message = final_message[:497] + "..."

    await message.channel.send(final_message)

    if debug:
        print(f"[DONATION] ✅ Message envoyé: {final_message}")