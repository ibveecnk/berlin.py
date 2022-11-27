import discord
import discord.ext.commands


class Help(discord.ext.commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()
        self.no_category = 'Miscellaneous'
        self.remove_mentions = True
        self.command_attrs['help'] = 'Shows this message'

    async def send_pages(self):
        destination = self.get_destination()
        async with destination.typing():
            for page in self.paginator.pages:
                embed = discord.Embed(
                    description=page, color=discord.Color.green())
                await destination.send(embed=embed)
