import discord
import youtube_dl as ytdl
from discord.ext import commands

from Helpers.PlayerSource import PlayerSource


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.guild_only()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        async with ctx.typing():
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)
            await channel.connect()
        await ctx.send(f'Joined {channel.name}.')

    @commands.hybrid_command()
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, search: str):
        """Plays a song from a search query"""
        async with ctx.typing():
            async with ctx.typing():
                player = await PlayerSource.create_source(ctx, search=search, loop=self.bot.loop, download=False)
                ctx.voice_client.play(player, after=lambda e: print(
                    f'Player error: {e}') if e else None)
        await ctx.send(f'Now playing: {player.title}')

    @commands.hybrid_command()
    @commands.guild_only()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        async with ctx.typing():
            if ctx.voice_client is None:
                return await ctx.send("Not connected to a voice channel.")

            ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.hybrid_command()
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        async with ctx.typing():
            await ctx.voice_client.disconnect()
        await ctx.send('Disconnected.')

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


async def setup(bot):
    await bot.add_cog(Music(bot))
