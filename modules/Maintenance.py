import datetime
import shutil
import discord
from discord.ext import commands
from pathlib import Path
import os


class Maintenance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f'Bot is logged in as {self.bot.user}')
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Streaming(name=f"{len(self.bot.guilds)} guilds.", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        await sync_command_tree(self.bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permissions to run this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required argument.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("You have provided an invalid argument.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("An error occurred while running this command.")
            await ctx.send(f"```python\n{error}```")
            self.bot.logger.error(
                f'An error occurred while running command {ctx.command.name}: {error.original}')
            raise error
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used in a server.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is currently disabled.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to run this command.")
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandError):
            if hasattr(error, 'message'):
                self.bot.logger.error(f'Command error: {error.message}')
            return
        else:
            raise error

    @commands.hybrid_command()
    @commands.is_owner()
    async def sysinfo(self, ctx: commands.Context):
        """Lists system information"""
        async with ctx.typing():
            sysname = os.uname().sysname
            total, used, free = shutil.disk_usage("/")
            cpu_cores = os.cpu_count()
            cpu_architecture = os.uname().machine
            mem = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            timediff = (datetime.datetime.now() - self.bot.start_time)
            # convert seconds to days, hours, minutes, seconds
            days = timediff.days
            hours = timediff.seconds // 3600
            minutes = (timediff.seconds // 60) % 60
            seconds = timediff.seconds % 60
            uptime = f"{days} d, {hours} h, {minutes} min, {seconds} s"

            embed = discord.Embed(title="System Information", color=0x00ff00)
            embed.add_field(name="Operating System",
                            value=sysname, inline=False)
            embed.add_field(name="CPU Cores", value=cpu_cores)
            embed.add_field(name="CPU Arch", value=cpu_architecture)
            embed.add_field(
                name="Memory", value=f"{mem / (1024.0 ** 3):.2f} GB", inline=False)
            embed.add_field(name="Used Disk Space",
                            value=f"{used // (2**30)} GB / {total // (2**30)} GB", inline=False)
            embed.add_field(
                name="Uptime", value=uptime, inline=False)
            await ctx.send(embed=embed)

    @commands.hybrid_command()
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
    await sync_command_tree(bot)
    return reloaded


async def sync_command_tree(bot):
    bot.logger.info('Syncing command tree...')
    await bot.tree.sync()
    bot.logger.info('Command tree synced.')


async def setup(bot):
    await bot.add_cog(Maintenance(bot))
