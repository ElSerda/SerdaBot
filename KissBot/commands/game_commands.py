from twitchio.ext import commands
from backends import GameLookup
import aiohttp
import json

class GameCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.game_lookup = GameLookup(bot.config)
    
    @commands.command(name='gameinfo', aliases=['gi'])
    async def game_info(self, ctx: commands.Context):
        if not ctx.message.content.strip().split(maxsplit=1)[1:]:
            await ctx.send("Usage: !game <nom_du_jeu>")
            return
        
        game_name = ctx.message.content.strip().split(maxsplit=1)[1]
        
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=5.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=5.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        if hasattr(self.bot, 'quantum_game_cache') and self.bot.quantum_game_cache:
            try:
                result = await self.bot.quantum_game_cache.search_quantum_game(
                    query=game_name,
                    observer=ctx.author.name
                )
                
                if result:
                    response = self.bot.quantum_game_cache.format_quantum_game_result(result)
                    await ctx.send(f"@{ctx.author.name} {response}")
                    return
            except Exception as e:
                self.bot.logger.warning(f"Cache quantique erreur: {e}")
        
        result = await self.game_lookup.search_game(game_name)
        
        if not result:
            await ctx.send(f"@{ctx.author.name} Aucun jeu trouvé pour: {game_name}")
            return
        
        response = self._format_game_response(result, game_name)
        
        try:
            if hasattr(self.bot, 'game_cache') and self.bot.game_cache:
                await self.bot.game_cache.save_to_cache(game_name, result)
        except Exception as e:
            self.bot.logger.warning(f"Erreur sauvegarde cache: {e}")
        
        await ctx.send(response)
    
    @commands.command(name='gamecategory', aliases=['gc'])
    async def game_category(self, ctx: commands.Context):
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=10.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=10.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        channel_name = ctx.channel.name
        game_name = await self._get_current_game(channel_name)
        
        if not game_name:
            await ctx.send(f"@{ctx.author.name} {channel_name} n'est pas sur un jeu nullos! 🎮")
            return
        
        enriched_result = await self.game_lookup.search_game(game_name)
        
        if not enriched_result:
            await ctx.send(f"🎮 Stream actuel : {game_name} (pas d'infos dispo)")
            return
        
        response = self._format_game_response(enriched_result, game_name)
        await ctx.send(f"🎮 Stream actuel : {response}")
    
    @commands.command(name='trad', aliases=['tr'])
    async def translate_command(self, ctx: commands.Context):
        if not ctx.message.content.strip().split(maxsplit=1)[1:]:
            await ctx.send("Usage: !trad <texte>")
            return
        
        text_to_translate = ctx.message.content.strip().split(maxsplit=1)[1]
        
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=8.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=8.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        try:
            translated_text = await self.bot.translator.translate_auto(text_to_translate)
            if translated_text:
                await ctx.send(f"@{ctx.author.name} Trad: {translated_text}")
            else:
                await ctx.send(f"@{ctx.author.name} Impossible de traduire ce texte.")
        except Exception as e:
            self.bot.logger.error(f"Erreur traduction: {e}")
            await ctx.send(f"@{ctx.author.name} Erreur lors de la traduction.")
    
    @commands.command(name='devs')
    async def devs_command(self, ctx: commands.Context):
        if not self.bot.rate_limiter.is_allowed(ctx.author.name, cooldown=30.0):
            remaining = self.bot.rate_limiter.get_remaining_cooldown(ctx.author.name, cooldown=30.0)
            await ctx.send(f"@{ctx.author.name} Cooldown! Attends {remaining:.1f}s")
            return
        
        try:
            with open('data/devs.json', 'r', encoding='utf-8') as f:
                devs_data = json.load(f)
            
            devs_list = ", ".join(devs_data.get('developers', []))
            if devs_list:
                await ctx.send(f"🚀 Dév Team: {devs_list}")
            else:
                await ctx.send("🤖 Aucun développeur configuré.")
        except Exception as e:
            self.bot.logger.error(f"Erreur lecture devs: {e}")
            await ctx.send("Erreur lors de la lecture des développeurs.")
    
    async def _get_current_game(self, channel_name):
        try:
            headers = {
                'Client-ID': self.bot.config['twitch']['client_id'],
                'Authorization': f"Bearer {self.bot.config['twitch']['oauth_token']}"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.twitch.tv/helix/channels?broadcaster_login={channel_name}"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data'):
                            return data['data'][0].get('game_name')
            return None
        except Exception:
            return None
    
    def _format_game_response(self, result, game_name):
        name = result.get('name', game_name)
        released = result.get('released', 'N/A')
        rating = result.get('rating', 'N/A')
        genres = result.get('genres', [])
        platforms = result.get('platforms', [])
        
        response = f"🎮 {name}"
        
        if released != 'N/A':
            response += f" ({released})"
        
        if rating != 'N/A':
            response += f" - ⭐ {rating}/5"
        
        if genres:
            genre_names = [g.get('name', str(g)) for g in genres[:2]]
            response += f" - {', '.join(genre_names)}"
        
        if platforms:
            platform_names = [p.get('platform', {}).get('name', str(p)) for p in platforms[:3]]
            if platform_names:
                response += f" - 🎯 {', '.join(platform_names)}"
        
        return response