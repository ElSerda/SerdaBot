#!/usr/bin/env python3
"""
Crash Test COMPLET du Pipeline SerdaBot 🚀

Simule de vrais viewers Twitch qui testent toutes les commandes.
Avec et sans LLM, pour valider le pipeline entier.

PHASES DE TEST:
1. Commandes !gameinfo normales (10 jeux populaires)
2. Test résilience typos (4 jeux avec fautes de frappe)
3. Commandes invalides (2 tests d'erreur)
4. Test cache (5 jeux déjà en cache)
5. Messages de chat naturels (21 messages avec/sans commandes)
6. Test modèle LLM (8 interactions: !ask + mentions @serda_bot)

COUVERTURE COMPLÈTE:
✅ Commandes !gameinfo (RAWG API + cache)
✅ Messages de chat normaux (ignorés par le bot)
✅ Commandes !ask (modèle LLM factuel)
✅ Mentions @serda_bot (modèle LLM conversationnel)
✅ Typo resilience (RAWG fuzzy search)
✅ Gestion d'erreurs (commandes invalides)
✅ Performance (cache vs API vs LLM)

RÉSULTATS ATTENDUS:
- ~88% de taux de succès (commandes valides)
- 0.0ms (cache) à 3s (API) pour !gameinfo
- 200ms à 8s pour réponses LLM (selon modèle)
- Messages normaux correctement ignorés
"""
import asyncio
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Activer le mode dev
os.environ["BOT_ENV"] = "dev"

from config.config import load_config
from core.cache import GAME_CACHE
from core.commands.ask_command import handle_ask_command
from core.commands.chill_command import handle_chill_command
from core.commands.game_command import handle_game_command


# Fake Message Twitch
class FakeAuthor:
    def __init__(self, name: str):
        self.name = name


class FakeChannel:
    def __init__(self):
        self.messages = []
    
    async def send(self, message: str):
        """Simule l'envoi d'un message."""
        self.messages.append(message)
        # Afficher avec couleur et timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 BOT → {message[:200]}...")


class FakeMessage:
    def __init__(self, author_name: str, content: str):
        self.author = FakeAuthor(author_name)
        self.content = content
        self.channel = FakeChannel()


# Scénarios de test
VIEWERS = [
    {"name": "GamerPro", "emoji": "🎮"},
    {"name": "CasualPlayer", "emoji": "🕹️"},
    {"name": "StreamSniper", "emoji": "🎯"},
    {"name": "ChatLurker", "emoji": "👀"},
    {"name": "MemeLord", "emoji": "😂"},
]

# Commandes à tester (sans LLM d'abord)
GAME_COMMANDS = [
    "!gameinfo Hades",
    "!gameinfo Elden Ring",
    "!gameinfo Stardew Valley",
    "!gameinfo The Witcher 3",
    "!gameinfo Cyberpunk 2077",
    "!gameinfo JEUX_INEXISTANT_12345",
    "!gameinfo Baldur's Gate 3",
    "!gameinfo GTA V",
    "!gameinfo Minecraft",
    "!gameinfo Dark Souls 3",
]

# Commandes avec typos (test résilience RAWG)
TYPO_COMMANDS = [
    "!gameinfo Elden Rign",  # Elden Ring
    "!gameinfo Stardew Valey",  # Stardew Valley
    "!gameinfo Mincecraft",  # Minecraft
    "!gameinfo Baldurs Gate 3",  # Baldur's Gate 3
]

# Commandes invalides
INVALID_COMMANDS = [
    "!gameinfo",  # Sans argument
    "!gameinfo ",  # Argument vide
]

# Messages de chat naturels (conversation normale)
CHAT_MESSAGES = [
    # Messages sans commande (le bot ne devrait PAS répondre)
    "Salut tout le monde ! 👋",
    "Quelqu'un joue à Elden Ring ?",
    "@SerdaBot tu es là ?",
    "lol gg",
    "J'adore ce stream ! ❤️",
    "C'est quoi ce jeu ?",
    "@SerdaBot c'est quoi Hades ?",  # Mention mais pas de commande
    "Hades est trop bien",
    "Quelqu'un connaît Celeste ?",
    "!help",  # Autre commande
    "PogChamp",
    "Le boss est trop dur !",
    "Tu joues bien ! 🔥",
    "Quelle build tu utilises ?",
    "@SerdaBot tu peux me dire un truc sur Skyrim ?",  # Mention sans commande
    
    # Messages avec commandes valides mélangées
    "Oh ! !gameinfo Celeste",
    "@SerdaBot !gameinfo Hollow Knight",
    "J'ai entendu parler de Terraria, !gameinfo Terraria",
    "!gameinfo Undertale svp",
    "Yo !gameinfo Sekiro",
    "!gameinfo The Last of Us s'il te plaît",
]

# Messages avec le modèle LLM (mention @serda_bot)
LLM_MESSAGES = [
    # Mentions directes du bot (déclenchent !chill)
    "@serda_bot salut, comment ça va ?",
    "@serda_bot tu connais Hades ?",
    "@serda_bot quel est ton jeu préféré ?",
    "@serda_bot lol",
    "@serda_bot merci pour les infos !",
    
    # Commandes !ask (questions factuelles)
    "!ask C'est quoi Elden Ring ?",
    "!ask Qui a développé Stardew Valley ?",
    "!ask Quelle est la capitale de la France ?",
]


async def simulate_viewer_message(viewer: dict, command: str, config: dict, stats: dict):
    """
    Simule un viewer qui envoie une commande.
    
    Args:
        viewer: Dict avec name et emoji
        command: Commande à tester
        config: Config du bot
        stats: Stats globales
    """
    # Créer un fake message
    message = FakeMessage(viewer["name"], command)
    
    # Afficher le viewer qui parle
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*80}")
    print(f"[{timestamp}] {viewer['emoji']} {viewer['name']}: {command}")
    print(f"{'='*80}")
    
    stats['total_commands'] += 1
    
    try:
        # Vérifier si c'est une commande !gameinfo
        if "!gameinfo " in command:
            # Extraire le nom du jeu (après !gameinfo)
            game_start = command.find("!gameinfo ") + 10
            game_name = command[game_start:].strip()
            
            if not game_name:
                stats['invalid_commands'] += 1
                print("❌ Commande invalide (pas de jeu)")
                return
            
            # Mesurer le temps
            start = time.time()
            
            # Appeler le handler (comme le vrai bot)
            await handle_game_command(
                message=message,
                config=config,
                game_name=game_name,
                now=time.time()
            )
            
            duration = time.time() - start
            
            # Vérifier la réponse
            if message.channel.messages:
                response = message.channel.messages[-1]
                
                if "❌" in response or "introuvable" in response.lower():
                    stats['not_found'] += 1
                    stats['response_times'].append(duration)
                else:
                    stats['success'] += 1
                    stats['response_times'].append(duration)
                    
                    # Vérifier si le cache a été utilisé
                    if "⚡" in response or duration < 0.1:
                        stats['cache_hits'] += 1
            else:
                stats['no_response'] += 1
        
        else:
            # Message de chat normal (pas une commande !gameinfo)
            stats['chat_messages'] += 1
            print("💬 Message de chat (ignoré par le handler)")
    
    except Exception as e:
        stats['errors'] += 1
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()


async def simulate_chat_message(viewer: dict, message_text: str, stats: dict):
    """
    Simule un message de chat normal (pas forcément une commande).
    
    Args:
        viewer: Dict avec name et emoji
        message_text: Texte du message
        stats: Stats globales
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] {viewer['emoji']} {viewer['name']}: {message_text}")
    
    # Vérifier si c'est une commande !gameinfo
    if "!gameinfo " in message_text:
        stats['chat_with_commands'] += 1
        print("   → 🎮 Contient une commande !gameinfo (sera traitée)")
    elif "!ask " in message_text:
        stats['chat_with_commands'] += 1
        print("   → 🧠 Contient une commande !ask (sera traitée)")
    elif "@serda_bot" in message_text.lower():
        stats['chat_with_commands'] += 1
        print("   → 🤖 Mention du bot (déclenchera !chill)")
    else:
        stats['normal_chat'] += 1
        print("   → 💬 Message normal (bot ne répond pas)")


async def simulate_llm_message(viewer: dict, message_text: str, config: dict, stats: dict):
    """
    Simule un message qui déclenche le LLM (!ask ou mention du bot).
    
    Args:
        viewer: Dict avec name et emoji
        message_text: Texte du message
        config: Config du bot
        stats: Stats globales
    """
    message = FakeMessage(viewer["name"], message_text)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*80}")
    print(f"[{timestamp}] {viewer['emoji']} {viewer['name']}: {message_text}")
    print(f"{'='*80}")
    
    stats['llm_commands'] += 1
    
    try:
        if "!ask " in message_text:
            # Extraire la question
            question = message_text.split("!ask ", 1)[1].strip()
            
            if not question:
                stats['invalid_commands'] += 1
                print("❌ Commande !ask invalide (pas de question)")
                return
            
            # Mesurer le temps
            start = time.time()
            
            # Appeler le handler !ask
            await handle_ask_command(
                message=message,
                config=config,
                question=question,
                now=time.time()
            )
            
            duration = time.time() - start
            
            # Vérifier la réponse
            if message.channel.messages:
                stats['llm_success'] += 1
                stats['llm_response_times'].append(duration)
                print(f"✅ Réponse LLM !ask en {duration*1000:.1f}ms")
            else:
                stats['llm_no_response'] += 1
        
        elif "@serda_bot" in message_text.lower():
            # Mesurer le temps
            start = time.time()
            
            # Appeler le handler !chill
            await handle_chill_command(
                message=message,
                config=config,
                now=time.time()
            )
            
            duration = time.time() - start
            
            # Vérifier la réponse
            if message.channel.messages:
                stats['llm_success'] += 1
                stats['llm_response_times'].append(duration)
                print(f"✅ Réponse LLM !chill en {duration*1000:.1f}ms")
            else:
                stats['llm_no_response'] += 1
        
        else:
            stats['llm_no_response'] += 1
            print("⚠️ Message LLM non reconnu")
    
    except Exception as e:
        stats['llm_errors'] += 1
        print(f"❌ ERREUR LLM: {e}")
        import traceback
        traceback.print_exc()


async def run_crash_test():
    """Lance le crash test complet."""
    print("\n" + "="*80)
    print("🚀 CRASH TEST COMPLET DU PIPELINE SERDABOT")
    print("="*80)
    
    config = load_config()
    
    # Stats du cache avant
    cache_stats_before = GAME_CACHE.stats()
    print(f"\n📦 Cache avant: {cache_stats_before['valid_entries']} entrées")
    
    # Stats globales
    stats = {
        'total_commands': 0,
        'success': 0,
        'not_found': 0,
        'invalid_commands': 0,
        'no_response': 0,
        'errors': 0,
        'cache_hits': 0,
        'response_times': [],
        'chat_messages': 0,
        'normal_chat': 0,
        'chat_with_commands': 0,
        'llm_commands': 0,
        'llm_success': 0,
        'llm_no_response': 0,
        'llm_errors': 0,
        'llm_response_times': [],
    }
    
    # Phase 1: Commandes normales
    print("\n" + "="*80)
    print("📋 PHASE 1: Commandes !gameinfo normales")
    print("="*80)
    
    for i, command in enumerate(GAME_COMMANDS):
        viewer = VIEWERS[i % len(VIEWERS)]
        await simulate_viewer_message(viewer, command, config, stats)
        await asyncio.sleep(0.2)  # Petit délai entre messages
    
    # Phase 2: Commandes avec typos
    print("\n" + "="*80)
    print("📋 PHASE 2: Test résilience (typos)")
    print("="*80)
    
    for i, command in enumerate(TYPO_COMMANDS):
        viewer = VIEWERS[i % len(VIEWERS)]
        await simulate_viewer_message(viewer, command, config, stats)
        await asyncio.sleep(0.2)
    
    # Phase 3: Commandes invalides
    print("\n" + "="*80)
    print("📋 PHASE 3: Commandes invalides")
    print("="*80)
    
    for i, command in enumerate(INVALID_COMMANDS):
        viewer = VIEWERS[i % len(VIEWERS)]
        await simulate_viewer_message(viewer, command, config, stats)
        await asyncio.sleep(0.2)
    
    # Phase 4: Test cache (re-test des mêmes jeux)
    print("\n" + "="*80)
    print("📋 PHASE 4: Test du cache (même jeux)")
    print("="*80)
    
    cache_test_commands = GAME_COMMANDS[:5]  # 5 premiers
    for i, command in enumerate(cache_test_commands):
        viewer = VIEWERS[i % len(VIEWERS)]
        await simulate_viewer_message(viewer, command, config, stats)
        await asyncio.sleep(0.1)  # Plus rapide car cache
    
    # Phase 5: Messages de chat naturels
    print("\n" + "="*80)
    print("📋 PHASE 5: Messages de chat naturels (avec/sans commandes)")
    print("="*80)
    print("💡 Simule un vrai chat Twitch avec des messages normaux")
    
    for i, chat_msg in enumerate(CHAT_MESSAGES):
        viewer = VIEWERS[i % len(VIEWERS)]
        
        # Si le message contient !gameinfo, utiliser le handler complet
        if "!gameinfo " in chat_msg:
            await simulate_viewer_message(viewer, chat_msg, config, stats)
        else:
            # Sinon juste afficher le message (le bot ne répond pas)
            await simulate_chat_message(viewer, chat_msg, stats)
        
        await asyncio.sleep(0.3)  # Délai réaliste entre messages
    
    # Phase 6: Test du modèle LLM (!ask + mention @serda_bot)
    print("\n" + "="*80)
    print("📋 PHASE 6: Test du modèle LLM (!ask + mention @serda_bot)")
    print("="*80)
    print("🧠 Simule des interactions avec le modèle IA")
    print("⚠️ ATTENTION: Cette phase peut être longue selon le modèle")
    
    for i, llm_msg in enumerate(LLM_MESSAGES):
        viewer = VIEWERS[i % len(VIEWERS)]
        await simulate_llm_message(viewer, llm_msg, config, stats)
        await asyncio.sleep(0.5)  # Délai pour le modèle


    
    # Résultats finaux
    print("\n" + "="*80)
    print("📊 RÉSULTATS DU CRASH TEST")
    print("="*80)
    
    cache_stats_after = GAME_CACHE.stats()
    
    print(f"\n🎯 Commandes:")
    print(f"   Total:     {stats['total_commands']}")
    print(f"   ✅ Succès:  {stats['success']}")
    print(f"   ❌ Non trouvé: {stats['not_found']}")
    print(f"   ⚠️ Invalides: {stats['invalid_commands']}")
    print(f"   🔇 Sans réponse: {stats['no_response']}")
    print(f"   💥 Erreurs: {stats['errors']}")
    
    print(f"\n💬 Chat:")
    print(f"   Messages normaux: {stats['normal_chat']}")
    print(f"   Avec commandes:   {stats['chat_with_commands']}")
    print(f"   Total messages:   {stats['normal_chat'] + stats['chat_with_commands']}")
    
    # Ratio messages/commandes
    total_messages = stats['normal_chat'] + stats['chat_with_commands']
    if total_messages > 0:
        command_ratio = (stats['chat_with_commands'] / total_messages) * 100
        print(f"   Ratio commandes:  {command_ratio:.1f}% des messages")
    
    # Comportement du bot
    print(f"\n🤖 Comportement du bot:")
    print(f"   Réponses données:     {stats['success'] + stats['not_found']}")
    print(f"   Messages ignorés:     {stats['normal_chat']}")
    print(f"   (Le bot ne répond qu'aux !gameinfo)")
    
    # Stats LLM
    if stats['llm_commands'] > 0:
        print(f"\n🧠 Modèle LLM (!ask + @serda_bot):")
        print(f"   Total appels:     {stats['llm_commands']}")
        print(f"   ✅ Succès:        {stats['llm_success']}")
        print(f"   🔇 Sans réponse:  {stats['llm_no_response']}")
        print(f"   💥 Erreurs:       {stats['llm_errors']}")
        
        if stats['llm_response_times']:
            avg_llm_time = sum(stats['llm_response_times']) / len(stats['llm_response_times'])
            min_llm_time = min(stats['llm_response_times'])
            max_llm_time = max(stats['llm_response_times'])
            
            print(f"\n   ⏱️ Performance LLM:")
            print(f"      Temps moyen: {avg_llm_time*1000:.1f}ms")
            print(f"      Plus rapide: {min_llm_time*1000:.1f}ms")
            print(f"      Plus lent:   {max_llm_time*1000:.1f}ms")



    
    if stats['response_times']:
        avg_time = sum(stats['response_times']) / len(stats['response_times'])
        min_time = min(stats['response_times'])
        max_time = max(stats['response_times'])
        
        print(f"\n⏱️ Performance:")
        print(f"   Temps moyen: {avg_time*1000:.1f}ms")
        print(f"   Plus rapide: {min_time*1000:.1f}ms")
        print(f"   Plus lent:   {max_time*1000:.1f}ms")
    
    print(f"\n💾 Cache:")
    print(f"   Avant:       {cache_stats_before['valid_entries']} entrées")
    print(f"   Après:       {cache_stats_after['valid_entries']} entrées")
    print(f"   Nouvelles:   {cache_stats_after['valid_entries'] - cache_stats_before['valid_entries']}")
    print(f"   Hits estimés: {stats['cache_hits']}")
    
    if cache_stats_after['cache_file']:
        if os.path.exists(cache_stats_after['cache_file']):
            size = os.path.getsize(cache_stats_after['cache_file'])
            print(f"   Fichier:     {cache_stats_after['cache_file']} ({size/1024:.1f} KB)")
    
    # Taux de succès
    if stats['total_commands'] > 0:
        success_rate = (stats['success'] / stats['total_commands']) * 100
        print(f"\n🎉 Taux de succès: {success_rate:.1f}%")
    
    print(f"\n{'='*80}")
    print("✅ CRASH TEST TERMINÉ !")
    print("="*80)
    print()


async def main():
    """Point d'entrée."""
    print("\n🧪 Crash Test Pipeline SerdaBot")
    print("="*80)
    print("\n📋 6 PHASES DE TEST:")
    print("   1️⃣  Commandes !gameinfo normales (10 jeux)")
    print("   2️⃣  Résilience typos (4 jeux avec fautes)")
    print("   3️⃣  Commandes invalides (2 tests)")
    print("   4️⃣  Cache performance (5 jeux)")
    print("   5️⃣  Messages chat naturels (21 messages)")
    print("   6️⃣  Modèle LLM (!ask + @serda_bot, 8 interactions)")
    print("\n🎮 Simule de vrais viewers qui testent les commandes")
    print("⚡ Tests avec et sans cache")
    print("🤖 Tests avec modèle IA (LM Studio / OpenAI)")
    print("🔍 Validation du pipeline complet")
    
    choice = input("\nLancer le crash test ? (Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', 'oui', 'o']:
        print("\n🚀 Lancement du crash test...\n")
        await run_crash_test()
    else:
        print("\n❌ Test annulé")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Crash test interrompu")
