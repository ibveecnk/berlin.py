import asyncio
import itertools
from lib2to3.pytree import Base
import random
import sys
import traceback
import discord
import youtube_dl as ytdl
from discord.ext import commands
from Helpers.Embed.BaseEmbed import BaseEmbed
from Helpers.Music import MusicPlayer

from Helpers.Music.PlayerSource import PlayerSource


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer.MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.hybrid_command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        """
        async with ctx.typing():
            vc = ctx.voice_client
            if not vc:
                await ctx.invoke(self.connect_)
            player = self.get_player(ctx)

            # If download is False, source will be a dict which will be used later to regather the stream.
            # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
            source = await PlayerSource.create_source(ctx, search, loop=self.bot.loop, download=False)
            await player.queue.put(source)

    @commands.hybrid_command(aliases=["vol"])
    @commands.guild_only()
    async def volume(self, ctx, vol: int):
        """Changes the player's volume"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(
                title="", description="I am not currently connected to voice", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if not vol:
            embed = discord.Embed(
                title="", description=f"🔊 **{(vc.source.volume)*100}%**", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if not 0 < vol < 101:
            embed = discord.Embed(
                title="", description="Please enter a value between 1 and 100", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(
            title="", description=f'**`{ctx.author}`** set the volume to **{vol}%**', color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["np"])
    @commands.guild_only()
    async def nowplaying(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = BaseEmbed(
                ctx, title="Error", description="I am not currently connected to voice")
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if not player.current:
            embed = BaseEmbed(ctx, title="Nothing playing",
                              description="I am currently not playing anything")
            return await ctx.send(embed=embed)

        # Format the time
        seconds = vc.source.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = BaseEmbed(
            ctx, title="Now Playing", description=f"**[{vc.source.title}]({vc.source.web_url})**")
        embed.add_field(name="Duration", value=f"{duration}", inline=False)
        embed.add_field(name="Requester",
                        value=f"{vc.source.requester}", inline=False)
        embed.set_thumbnail(url=vc.source.thumbnail)
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["q"])
    @commands.guild_only()
    async def queue(self, ctx: commands.Context):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(
                title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(
                title="", description="queue is empty", color=discord.Color.green())
            return await ctx.send(embed=embed)

        seconds = vc.source.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue,
                        0, int(len(player.queue._queue))))

        plural_s = "s" if len(upcoming) > 1 else ""

        embed = BaseEmbed(ctx, title="Upcoming Song" + plural_s)

        for i, song in enumerate(upcoming):
            if (i > 9):
                embed.add_field(
                    name=f"And {len(upcoming) - i} more...", value=None)
                break
            embed.add_field(name=f"{i+1}. {song['title']}",
                            value=f"Duration: {duration}, Requester: {song['requester']}, [link]({song['webpage_url']})", inline=False)
        await ctx.send(embed=embed)

    @ commands.hybrid_command(aliases=["l"])
    @ commands.guild_only()
    async def leave(self, ctx: commands.Context):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(
                title="", description="I'm not connected to a voice channel", color=discord.Color.green())
            return await ctx.send(embed=embed)

        if (random.randint(0, 1) == 0):
            await ctx.message.add_reaction('👋')
        await ctx.send('**Successfully disconnected**')

        await self.cleanup(ctx.guild)

    @ commands.hybrid_command(aliases=["s"])
    @ commands.guild_only()
    async def skip(self, ctx: commands.Context):
        """Skip the song."""
        vc: discord.VoiceClient = ctx.voice_client

        async with ctx.typing():
            if not vc or not vc.is_connected():
                embed = discord.Embed(
                    title="", description="I'm not connected to a voice channel", color=discord.Color.green())
                return await ctx.send(embed=embed)

            self.get_player(ctx).current.cleanup()
            await ctx.send('**Skipped**')

    @ play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")


async def setup(bot):
    await bot.add_cog(Music(bot))
