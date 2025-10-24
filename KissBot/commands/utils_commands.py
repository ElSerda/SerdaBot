"""
Utils Commands Component - !ping, !stats, !help, !cache
"""

from twitchio.ext import commands
import time


class UtilsCommands(commands.Cog):
    """Commandes utilitaires."""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.command(name='ping')
    async def ping_command(self, ctx: commands.Context):
        """Test de latence."""
        await ctx.send(f"Pong! 🏓 Uptime: {self._get_uptime()}")
    
    @commands.command(name='stats')
    async def stats_command(self, ctx: commands.Context):
        """Statistiques du bot."""
        stats = []
        
        # Uptime
        stats.append(f"⏱️ Uptime: {self._get_uptime()}")
        
        # Cache game stats si disponible
        if hasattr(self.bot, 'game_cache'):
            try:
                cache_stats = self.bot.game_cache.get_stats()
                if 'hits' in cache_stats and 'misses' in cache_stats:
                    hit_rate = (cache_stats['hits'] / max(1, cache_stats['hits'] + cache_stats['misses'])) * 100
                    stats.append(f"📊 Cache: {hit_rate:.1f}% hit rate")
                else:
                    stats.append(f"📊 Cache: {len(getattr(self.bot.game_cache, '_cache', {}))} entrées")
            except Exception:
                stats.append("📊 Cache: Stats indisponibles")
        
        await ctx.send(" | ".join(stats))
    
    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Liste des commandes."""
        commands_list = [
            "!gameinfo <nom>: Info jeu",
            "!gc: Jeu actuel du stream",
            "!ask <question>: IA",
            "@mention: IA conversationnelle",
            "!ping: Test latence",
            "!stats: Stats bot",
            "!cache: Stats cache",
            "!serdagit: Code source"
        ]
        
        await ctx.send(f"Commandes: {' | '.join(commands_list)}")
    
    @commands.command(name='serdagit')
    async def serdagit_command(self, ctx: commands.Context):
        """Info GitHub du créateur."""
        await ctx.send("🤖 Bot codé par El_Serda ! Retrouvez KissBot et tous mes projets sur GitHub/ElSerda ✨")
    
    @commands.command(name='cache')
    async def cache_command(self, ctx: commands.Context):
        """Stats du cache de jeux."""
        if not hasattr(self.bot, 'game_cache'):
            await ctx.send("📦 Cache indisponible")
            return
        
        try:
            stats = self.bot.game_cache.get_stats()
            
            if 'hits' in stats and 'misses' in stats:
                total = stats['hits'] + stats['misses']
                hit_rate = (stats['hits'] / max(1, total)) * 100
                response = f"📦 Cache: {stats['size']} entrées | {hit_rate:.1f}% hit rate | {stats['hits']} hits / {stats['misses']} miss"
            else:
                # Fallback si pas de stats hits/misses
                cache_size = len(getattr(self.bot.game_cache, '_cache', {}))
                response = f"📦 Cache: {cache_size} entrées actives"
                
        except Exception as e:
            response = f"📦 Cache: Erreur stats ({str(e)[:20]}...)"
        
        await ctx.send(response)
    
    def _get_uptime(self) -> str:
        """Calcule l'uptime formaté."""
        elapsed = time.time() - self.start_time
        
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


def prepare(bot):
    """Setup function for TwitchIO."""
    bot.add_cog(UtilsCommands(bot))
