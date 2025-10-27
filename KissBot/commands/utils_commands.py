from twitchio.ext import commands
from core.handlers import HandlersFactory
import time


class UtilsCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.handlers = HandlersFactory()
        
    @commands.command(name='ping')
    async def ping_command(self, ctx: commands.Context):
        handler = self.handlers.create_ping_handler(getattr(self.bot, 'start_time', None))
        response = handler.get_ping_response()
        await ctx.send(response)
    
    @commands.command(name='stats')
    async def stats_command(self, ctx: commands.Context):
        handler = self.handlers.create_stats_handler(getattr(self.bot, 'start_time', None))
        
        cache_stats = None
        if hasattr(self.bot, 'game_cache'):
            try:
                cache_stats = self.bot.game_cache.get_stats()
            except Exception:
                pass
        
        response = handler.get_stats_response(cache_stats)
        await ctx.send(response)
    
    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        handler = self.handlers.create_help_handler()
        response = handler.get_help_response()
        await ctx.send(response)
    
    @commands.command(name='cache')
    async def cache_command(self, ctx: commands.Context):
        handler = self.handlers.create_cache_handler()
        
        cache_stats = None
        if hasattr(self.bot, 'game_cache'):
            try:
                cache_stats = self.bot.game_cache.get_stats()
            except Exception:
                pass
        
        response = handler.get_cache_response(cache_stats)
        await ctx.send(response)
    
    @commands.command(name='serdagit')
    async def serdagit_command(self, ctx: commands.Context):
        await ctx.send("🤖 Bot codé par El_Serda ! Retrouvez KissBot et tous mes projets sur GitHub/ElSerda ✨")
    
    @commands.command(name='latency')
    async def latency_command(self, ctx: commands.Context):
        start_time = time.time()
        handler = self.handlers.create_latency_handler(start_time)
        response = handler.get_latency_response()
        await ctx.send(response)
    
    @commands.command(name='qpipeline', aliases=['qp'])
    async def quantum_pipeline_stats(self, ctx: commands.Context):
        pipeline_stats = None
        if hasattr(self.bot, 'get_quantum_pipeline_stats'):
            try:
                pipeline_stats = self.bot.get_quantum_pipeline_stats()
            except Exception:
                pass
        
        handler = self.handlers.create_quantum_pipeline_handler()
        response = handler.get_quantum_pipeline_response(pipeline_stats)
        await ctx.send(response)


def prepare(bot):
    bot.add_cog(UtilsCommands(bot))