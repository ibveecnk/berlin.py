import shutil
import discord
from discord.ext import commands
from pathlib import Path
import os
from discord.ext.commands.errors import CommandNotFound


class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f'Bot is logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # ignore command not found errors, because these are caused by a command
        # simply not existing, where we shall do nothing
        if isinstance(error, CommandNotFound):
            return
        raise error

    @commands.command()
    @commands.is_owner()
    async def sysinfo(self, ctx: commands.Context):
        """Lists system information"""
        async with ctx.typing():
            sysname = os.uname().sysname
            total, used, free = shutil.disk_usage("/")
            cpu_cores = os.cpu_count()
            cpu_architecture = os.uname().machine
            mem = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')

            embed = discord.Embed(title="System Information", color=0x00ff00)
            embed.add_field(name="Operating System",
                            value=sysname, inline=False)
            embed.add_field(name="CPU Cores", value=cpu_cores)
            embed.add_field(name="CPU Arch", value=cpu_architecture)
            embed.add_field(
                name="Memory", value=f"{mem / (1024.0 ** 3):.2f} GB", inline=False)
            embed.add_field(name="Used Disk Space",
                            value=f"{used // (2**30)} GB / {total // (2**30)} GB", inline=False)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        """Reloads selected/all modules"""
        async with ctx.typing():
            selected_modules = ctx.message.content.split()[1:]
            if selected_modules:
                reloaded = await reload_extensions(self.bot, selected_modules)
                if (reloaded):
                    await ctx.send(f'Reloaded: {", ".join(reloaded)}')
                else:
                    await ctx.send(f'No modules reloaded')
            else:
                reloaded = await reload_all_extenions(bot=self.bot)
                if (reloaded):
                    await ctx.send(f'Reloaded: {", ".join(reloaded)}')
                else:
                    await ctx.send(f'No modules reloaded')


async def reload_all_extenions(bot):
    modules = [file.stem for file in Path("modules").glob("*.py")]
    return await reload_extensions(bot, modules)


async def reload_extensions(bot, modules):
    reloaded = []
    for extension in modules:
        cap_extension = extension.capitalize()
        if cap_extension in bot.cogs:
            await bot.reload_extension(f"modules.{cap_extension}")
            reloaded.append(cap_extension)
        else:
            bot.logger.error(
                f'Failed to reload module {cap_extension}')
    bot.logger.info(f"Modules reloaded: {', '.join(reloaded)}")
    return reloaded


async def setup(bot):
    await bot.add_cog(Maintenance(bot))