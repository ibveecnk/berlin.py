from asyncio import sleep
import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome to {member.guild.name} with {member.guild.member_count} members, {member.mention}.')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason="no reason"):
        """Kicks a member from the server."""
        async with ctx.typing():
            await member.kick(reason=reason)
            await ctx.send(f'Kicked {member.mention} for {reason}.')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason="no reason"):
        """Bans a member from the server."""
        async with ctx.typing():
            await member.ban(reason=reason)
            await ctx.send(f'Banned {member.mention} for {reason}.')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, *, member):
        """Unbans a member from the server."""
        async with ctx.typing():
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f'Unbanned {user.mention}.')
                    return

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount=5):
        """Clears the specified amount of messages."""
        async with ctx.typing():
            limit = amount < 100 and amount or 100
            async for message in ctx.message.channel.history(limit=limit+1):
                await message.delete()
                await sleep(0.5)
            await ctx.send(f'Cleared {limit} messages.')

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason):
        """Warns a member."""
        async with ctx.typing():
            await ctx.send(f'Warned {member.mention} for {reason}.')
            await member.send(f'```You were warned in server {ctx.guild.name}\n\nReason: {reason}.```')


async def setup(bot):
    await bot.add_cog(Moderation(bot))
