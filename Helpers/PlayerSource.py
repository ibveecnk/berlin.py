import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import discord
import youtube_dl

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'cache/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class PlayerSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.title = data.get('title')
        self.url = data.get('url')

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    # create a method that returns a PlayerSource object from a url
    async def create_source(cls, ctx, search: str, *, loop, download: bool = False):
        with ytdl:
            data = await loop.run_in_executor(None, partial(ytdl.extract_info, url=search, download=download))
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]
            return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, requester=ctx.author)
