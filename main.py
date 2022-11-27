import os
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import logging
import logging.handlers
from dotenv import load_dotenv
from pathlib import Path
import asyncio


async def main():
    async def load_extenions():
        modules = [file.stem for file in Path("modules").glob("*.py")]
        for extension in modules:
            await bot.load_extension(f"modules.{extension}")
        logger.info(f"Modules loaded: {', '.join(bot.cogs)}")

    # Setup custom logger
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Load token from .env
    load_dotenv()
    TOKEN = os.getenv('TOKEN')

    # subscribe to intents
    intents = discord.Intents.default()
    intents.message_content = True
    bot = Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
    bot.logger = logger

    async with bot:
        await load_extenions()
        await bot.start(TOKEN)


if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        print('Async event loop already running. Adding coroutine to the event loop.')
        tsk = loop.create_task(main())
        tsk.add_done_callback(
            lambda t: print(f'Task done with result={t.result()}  << return val of main()'))
    else:
        print('Starting new event loop')
        result = asyncio.run(main())
