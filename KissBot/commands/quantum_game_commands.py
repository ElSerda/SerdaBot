"""Quantum-inspired game commands. See: docs/api/quantum_game_commands.md"""

import asyncio
import logging
from typing import Optional
from twitchio.ext import commands

from backends.quantum_game_cache import QuantumGameCache


class QuantumGameCommands(commands.Cog):
    """Commandes de jeu avec comportements quantiques."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        
        # Cache quantique des jeux
        self.quantum_game_cache: Optional[QuantumGameCache] = None
        
        # Initialiser le cache si config disponible
        if hasattr(bot, 'config'):
            try:
                self.quantum_game_cache = QuantumGameCache(bot.config)
                self.logger.info("🎮🔬 QuantumGameCache initialisé")
            except Exception as e:
                self.logger.error(f"Erreur init QuantumGameCache: {e}")
    
    @commands.command(name='qgame', aliases=['qg'])
    async def quantum_game_search(self, ctx: commands.Context, *, game_name: str = ""):
        """
        !qgame <nom> - Recherche quantique de jeu
        
        SUPERPOSITION: Propose des états possibles jusqu'à validation
        OBSERVATION: Chaque recherche influence les probabilités futures
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        if not game_name:
            await ctx.send("❓ Usage: !qgame <nom du jeu> (ex: !qgame hades)")
            return
        
        observer = ctx.author.name
        
        try:
            # Recherche quantique avec observation
            result = await self.quantum_game_cache.search_quantum_game(
                query=game_name,
                observer=observer
            )
            
            if not result:
                await ctx.send(f"❌ Aucun jeu quantique trouvé pour: {game_name}")
                return
            
            # INTERFACE VISUELLE QUANTIQUE ⚛️
            visual_format = self.quantum_game_cache.format_quantum_visual(result)
            formatted = self.quantum_game_cache.format_quantum_game_result(result)
            
            # Affichage visuel + détails
            response = f"{visual_format}\n{formatted}"
            
            # Ajouter infos quantiques si superposition
            if result.get('verified') != 1:
                suggestions = self.quantum_game_cache.get_quantum_suggestions(game_name)
                if len(suggestions) > 1:
                    response += f" • {len(suggestions)} états en superposition"
            
            await ctx.send(response)
            
            self.logger.info(f"🔍 Recherche quantique: {game_name} par {observer}")
            
        except Exception as e:
            self.logger.error(f"Erreur recherche quantique {game_name}: {e}")
            await ctx.send(f"⚠️ Erreur recherche quantique: {game_name}")
    
    @commands.command(name='collapse', aliases=['confirm'])
    async def collapse_game_state(self, ctx: commands.Context, *, game_name: str = ""):
        """
        !collapse <jeu> - COLLAPSE quantique (fixe l'état définitivement)
        
        EFFONDREMENT: Superposition → État permanent (verified: 1)
        LEARNING: Le bot apprend de vos confirmations
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        if not game_name:
            await ctx.send("❓ Usage: !collapse <nom du jeu> (ex: !collapse hades)")
            return
        
        observer = ctx.author.name
        
        try:
            # Tentative de collapse
            success = self.quantum_game_cache.confirm_game(
                query=game_name,
                observer=observer
            )
            
            if success:
                await ctx.send(f"💥 @{observer} a fait COLLAPSE l'état '{game_name}' → État figé permanent !")
                self.logger.info(f"💥 Collapse quantique: {game_name} par {observer}")
            else:
                # Vérifier si le jeu existe en superposition
                suggestions = self.quantum_game_cache.get_quantum_suggestions(game_name)
                if suggestions:
                    await ctx.send(f"⚠️ État '{game_name}' déjà collapsed ou inexistant. "
                                 f"Utilisez !qgame {game_name} d'abord")
                else:
                    await ctx.send(f"❌ Aucun état quantique trouvé pour: {game_name}")
                    
        except Exception as e:
            self.logger.error(f"Erreur collapse {game_name}: {e}")
            await ctx.send(f"⚠️ Erreur collapse: {game_name}")
    
    @commands.command(name='qstats', aliases=['quantumstats'])  
    async def quantum_game_stats(self, ctx: commands.Context):
        """
        !qstats - Statistiques du système quantique des jeux
        
        MÉTRIQUES: États, superpositions, intrications, apprentissage
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        try:
            stats = self.quantum_game_cache.get_quantum_game_stats()
            
            message = (f"🔬 Cache Quantique Jeux: {stats['game_keys']} jeux, "
                      f"{stats['confirmed_games']} confirmés, "
                      f"{stats['pending_games']} en superposition, "
                      f"{stats['entangled_pairs']} intrications, "
                      f"apprentissage: {stats['learning_rate']:.1%}")
            
            await ctx.send(message)
            self.logger.info(f"📊 Stats quantiques jeux par {ctx.author.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur stats quantiques: {e}")
            await ctx.send("⚠️ Erreur récupération statistiques quantiques")
    
    @commands.command(name='qdash', aliases=['quantumdash', 'qboard'])
    async def quantum_dashboard(self, ctx: commands.Context, *, query: str = ""):
        """
        !qdash [jeu] - Dashboard visuel quantique
        
        INTERFACE: Affichage visuel des états quantiques avec barres de progression
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        try:
            # Génération dashboard visuel
            if query.strip():
                dashboard = self.quantum_game_cache.format_quantum_dashboard(query)
            else:
                dashboard = self.quantum_game_cache.format_quantum_dashboard()
            
            if "🔬 [SERDA_BOT]" in dashboard and len(dashboard.split('\n')) > 1:
                await ctx.send(dashboard)
            else:
                await ctx.send("🔬 [SERDA_BOT]\n💫 Aucun état quantique actif")
            
            self.logger.info(f"📊 Dashboard quantique consulté par {ctx.author.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur dashboard quantique: {e}")
            await ctx.send("⚠️ Erreur affichage dashboard quantique")

    @commands.command(name='qsuggest', aliases=['suggest'])
    async def quantum_suggestions(self, ctx: commands.Context, *, game_name: str = ""):
        """
        !qsuggest <jeu> - Affiche tous les états en superposition
        
        SUPERPOSITION: Visualise tous les états possibles avant collapse
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        if not game_name:
            await ctx.send("❓ Usage: !qsuggest <nom du jeu>")
            return
        
        try:
            suggestions = self.quantum_game_cache.get_quantum_suggestions(game_name)
            
            if not suggestions:
                await ctx.send(f"❌ Aucune superposition trouvée pour: {game_name}")
                return
            
            if len(suggestions) == 1 and suggestions[0]['verified'] == 1:
                await ctx.send(f"🔒 {game_name}: État déjà collapsed (permanent)")
                return
            
            # Formater suggestions multiples
            lines = [f"⚛️ {game_name}: {len(suggestions)} états en superposition:"]
            for i, sugg in enumerate(suggestions):
                status = "🔒" if sugg['verified'] == 1 else "⚛️"
                conf_bar = "█" * int(sugg['confidence'] * 5)  # Barre sur 5
                lines.append(f"[{i}] {status} {sugg['name']} ({sugg['year']}) "
                           f"{conf_bar} {sugg['confidence']:.1f}")
            
            # Limite Twitch (max ~400 chars)
            message = " • ".join(lines[:3])  # Max 3 suggestions affichées
            if len(suggestions) > 3:
                message += f" • +{len(suggestions)-3} autres"
            
            await ctx.send(message)
            self.logger.info(f"📋 Suggestions quantiques: {game_name} par {ctx.author.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur suggestions {game_name}: {e}")
            await ctx.send(f"⚠️ Erreur suggestions: {game_name}")
    
    @commands.command(name='qentangle', aliases=['link'])
    async def entangle_games(self, ctx: commands.Context, game1: str = "", game2: str = ""):
        """
        !qentangle <jeu1> <jeu2> - Créer intrication entre jeux
        
        INTRICATION: Confirmations d'un jeu influencent l'autre
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        if not game1 or not game2:
            await ctx.send("❓ Usage: !qentangle <jeu1> <jeu2>")
            return
        
        # Vérifier permissions (éviter spam)
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            await ctx.send("⚠️ Intrication réservée aux modérateurs")
            return
        
        try:
            key1 = f"game:{game1.lower()}"
            key2 = f"game:{game2.lower()}"
            
            self.quantum_game_cache.quantum_cache.entangle(key1, key2)
            
            observer = ctx.author.name
            await ctx.send(f"🔗 @{observer} a créé intrication: {game1} ↔ {game2}")
            self.logger.info(f"🔗 Intrication jeux: {game1} ↔ {game2} par {observer}")
            
        except Exception as e:
            self.logger.error(f"Erreur intrication {game1}/{game2}: {e}")
            await ctx.send(f"⚠️ Erreur intrication: {game1} ↔ {game2}")
    
    @commands.command(name='qclean', aliases=['decoherence'])
    async def quantum_cleanup(self, ctx: commands.Context):
        """
        !qclean - Décohérence manuelle (évaporation états expirés)
        
        DÉCOHÉRENCE: Supprime les "particules virtuelles" non-confirmées
        """
        if not self.quantum_game_cache:
            await ctx.send("🚫 Cache quantique non disponible")
            return
        
        # Permissions modérateurs seulement
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            await ctx.send("⚠️ Décohérence réservée aux modérateurs")
            return
        
        try:
            cleaned_count = await self.quantum_game_cache.cleanup_quantum_games()
            
            observer = ctx.author.name
            await ctx.send(f"💨 @{observer} a déclenché décohérence → "
                          f"{cleaned_count} états évaporés")
            self.logger.info(f"💨 Décohérence manuelle: {cleaned_count} par {observer}")
            
        except Exception as e:
            self.logger.error(f"Erreur décohérence: {e}")
            await ctx.send("⚠️ Erreur décohérence quantique")
    
    @commands.command(name='qhelp', aliases=['qh'])
    async def quantum_help(self, ctx: commands.Context):
        """
        !qhelp - Aide commandes quantiques
        
        DOCUMENTATION: Guide d'utilisation du système quantique
        """
        help_text = ("🔬 Commandes Quantiques: !qgame <jeu> (recherche), "
                    "!collapse <jeu> (confirmer), !qstats (stats), "
                    "!qsuggest <jeu> (voir superposition), "
                    "!qhelp (aide) • Système d'apprentissage adaptatif !")
        
        await ctx.send(help_text)
    
    async def cog_unload(self):
        """Nettoyage à la décharge du cog."""
        if self.quantum_game_cache:
            await self.quantum_game_cache.close()


def prepare(bot):
    """Prépare le cog pour TwitchIO."""
    bot.add_cog(QuantumGameCommands(bot))