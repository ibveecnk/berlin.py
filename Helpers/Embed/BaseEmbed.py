import discord
from discord.ext import commands


class BaseEmbed(discord.Embed):
    def __init__(self, ctx: commands.Context = None, bot: commands.Bot = None, **kwargs):
        super().__init__(**kwargs)
        self.color = discord.Color.green()
        if (ctx):
            self.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            self.set_author(name=ctx.me.name,
                            icon_url=ctx.me.avatar.url)
        elif (bot):
            self.set_author(name=bot.user.name,
                            icon_url=bot.user.avatar.url)
