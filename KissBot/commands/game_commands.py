"""
Game Commands Component - !gameinfo, !gamecategory, !trad, !devs
Commandes explicites pour éviter conflits avec WizeBot [game_name]
"""

import aiohttp
import json
import os
from datetime import datetime
from twitchio.ext import commands
from backends import GameLookup


class GameCommands(commands.Cog):
    """Commandes de jeux."""
    
    def __init__(self, bot):
        self.bot = bot
        self.game_lookup = GameLookup(bot.config)
    
    # ========================================
    # COMMANDE: !gameinfo (évite conflit WizeBot)
    # ========================================
    
    @commands.command(name='gameinfo', aliases=['gi'])
    async def game_info(self, ctx: commands.Context):
        """Recherche d'informations détaillées sur un jeu."""
        if not ctx.message.content.strip().split(maxsplit=1)[1:]:
            await ctx.send("Usage: !game <nom_du_jeu>")
            return
        
        game_name = ctx.message.content.strip().split(maxsplit=1)[1]
        
        # Rate limit check
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=5.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=5.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        # Recherche du jeu
        result = await self.game_lookup.search_game(game_name)
        
        if not result:
            await ctx.send(f"@{ctx.author.name} Jeu non trouvé : {game_name}")
            return
        
        # 🎯 NOUVEAU: Refuser les matches LOW quality OU avec gros écart TYPO
        if result.confidence == "LOW":
            await ctx.send(f"@{ctx.author.name} Résultat trop imprécis pour '{game_name}'. Essaye le nom complet ou une suite spécifique (ex: Hades, Mario Kart 8, Zelda Breath Wild)")
            return
        
        # 🚨 NOUVEAU: Détecter les résultats complètement faux (gros écarts)
        query_words = set(game_name.lower().split())
        result_words = set(result.name.lower().split())
        shared_words = query_words.intersection(result_words)
        
        # Si aucun mot en commun ET query > 2 mots → probablement faux
        if len(query_words) >= 2 and len(shared_words) == 0:
            await ctx.send(f"@{ctx.author.name} Aucun résultat pertinent pour '{game_name}'. Vérifie l'orthographe ou essaye un autre nom")
            return
        
        # Format de la réponse
        response = self._format_game_response(result, game_name)
        await ctx.send(response)
    
    # ========================================
    # COMMANDE: !gamecategory
    # ========================================
    
    @commands.command(name='gamecategory', aliases=['gc'])
    async def game_category(self, ctx: commands.Context):
        """Affiche le jeu actuel du stream et enrichit automatiquement le cache."""
        
        # Rate limit check
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=10.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=10.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        # 1. Récupère le jeu actuel via Twitch Helix API
        channel_name = ctx.channel.name
        game_name = await self._get_current_game(channel_name)
        
        # 2. Si pas de jeu actif
        if not game_name:
            await ctx.send(f"@{ctx.author.name} {channel_name} n'est pas sur un jeu nullos! 🎮")
            return
        
        # 3. ENRICHISSEMENT AUTOMATIQUE DU CACHE
        # Recherche les infos complètes (RAWG+Steam) et cache enrichi
        enriched_result = await self.game_lookup.search_game(game_name)
        
        if not enriched_result:
            # Fallback si enrichissement échoue
            await ctx.send(f"🎮 Stream actuel : {game_name} (pas d'infos dispo)")
            return
        
        # 4. Réponse format !gc (MÊME FORMAT que !gameinfo)
        response = self._format_game_response(enriched_result, game_name)
        await ctx.send(f"🎮 Stream actuel : {response}")
    
    # ========================================
    # HELPERS PRIVÉS
    # ========================================
    
    # ========================================
    # UTILS: Cache Enrichment
    

    
    # ========================================
    # HELPERS PRIVÉS
    # ========================================
    
    async def _get_current_game(self, channel_name: str) -> str | None:
        """Récupère le jeu actuel du stream via Twitch Helix API.
        
        Args:
            channel_name: Nom du channel Twitch
            
        Returns:
            Nom du jeu si stream live, None sinon
        """
        url = f"https://api.twitch.tv/helix/streams?user_login={channel_name}"
        
        # Extract token sans prefix "oauth:" pour Helix API
        token = self.bot.config['twitch']['token']
        if token.startswith('oauth:'):
            token = token[6:]  # Remove "oauth:" prefix
        
        headers = {
            "Client-Id": self.bot.config['twitch']['client_id'],
            "Authorization": f"Bearer {token}"  # Helix API nécessite "Bearer"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        streams = data.get('data', [])
                        
                        if streams:
                            game = streams[0].get('game_name', '').strip()
                            
                            # Filter non-gaming categories
                            if game and game.lower() not in ['just chatting', 'music', 'talk shows & podcasts']:
                                return game
            
            return None
            
        except Exception as e:
            self.bot.logger.error(f"Erreur Helix API: {e}")
            return None
    
    def _format_game_response(self, result, original_query: str = "") -> str:
        """Formate la réponse du jeu de manière consistante.
        
        Args:
            result: GameResult object
            original_query: Requête originale de l'utilisateur
            
        Returns:
            Message formaté
        """
        response = f"{result.name}"
        
        if result.year and result.year != "?":
            response += f" ({result.year})"
        
        # 🎯 AJOUT PLATEFORMES
        if result.platforms:
            platforms = ', '.join(result.platforms[:4])  # Max 4 plateformes
            response += f" - {platforms}"
        
        if result.genres:
            genres = ', '.join(result.genres[:3])
            response += f" - {genres}"
        
        if result.rating_rawg > 0:
            response += f" - ⭐ {result.rating_rawg:.1f}/5"
        
        # ⚠️ Warning si faute de frappe possible
        if result.possible_typo and original_query:
            response += f" (Tu cherchais '{original_query}' ?)"
        
        return response
    
    def _is_broadcaster_or_mod(self, ctx: commands.Context) -> bool:
        """Vérifie si l'utilisateur est broadcaster ou modérateur."""
        # Broadcaster
        if ctx.author.name.lower() == ctx.channel.name.lower():
            return True
        
        # Modérateur (badges TwitchIO)
        if hasattr(ctx.author, 'badges') and ctx.author.badges:
            return 'moderator' in ctx.author.badges or 'broadcaster' in ctx.author.badges
        
        # Fallback: check si c'est toi
        return ctx.author.name.lower() in ['elserda', 'serda']
    
    def _is_french_message(self, text: str) -> bool:
        """Détection simple si un message est en français."""
        if not text or len(text.strip()) < 3:
            return True  # Messages courts = pas de traduction
        
        # Mots français communs
        french_words = {
            'le', 'la', 'de', 'et', 'à', 'un', 'une', 'du', 'des', 'les',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'avoir', 'être', 'faire', 'aller', 'voir', 'savoir', 'pouvoir',
            'avec', 'pour', 'dans', 'sur', 'par', 'sans', 'sous', 'entre',
            'très', 'plus', 'moins', 'bien', 'mal', 'tout', 'tous', 'toutes',
            'bonjour', 'salut', 'merci', 'oui', 'non', 'peut', 'être'
        }
        
        words = set(word.lower().strip('.,!?;:()[]{}"\'-') for word in text.split()[:10])
        french_count = sum(1 for word in words if word in french_words)
        
        # Si 25%+ des mots sont français = probablement français
        return french_count >= len(words) * 0.25
    
    
def prepare(bot):
    """Setup function for TwitchIO."""
    bot.add_cog(GameCommands(bot))
