import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.core import command

from youtube_dl import YoutubeDL


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            voice = self.vc
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing:
                    time = 0
                if time == 20:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" %item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            await ctx.send(f"""Playing **{self.music_queue[0][0]['title']}** requested by {self.music_queue[0][2]}""")


            self.vc.play(discord.FFmpegPCMAudio(
                m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.music_queue.pop(0)

        else:
            self.is_playing = False

    @commands.command(name="p", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword.")
            else:
                await ctx.send(f"""**{song["title"]}** has been added to the queue by {ctx.author.mention}""")
                self.music_queue.append(
                    [song, voice_channel, ctx.author.mention])

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="q", help="Displays the current songs in queue")
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"""{i+1}. **{self.music_queue[i][0]['title']}** added by {self.music_queue[i][2]}\n"""

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="s", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            await ctx.send("""**Skipped current song**""")
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="l", help="Leaves if commanded to the voice channel")
    @commands.has_any_role('DJ','Moderator', 'GDSC Lead', 'Core Team')
    async def leave(self, ctx, *args):
        if self.vc.is_connected():
            await ctx.send("""Bye :wave:""")
            await self.vc.disconnect(force=True)

    @commands.command(name="pn", help="Skips the queue and plays the current song!")
    @commands.has_any_role('DJ','Moderator', 'GDSC Lead', 'Core Team')
    async def playnext(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword.")
            else:
                await ctx.send(f"""**{song['title']}** has been added to the top of the queue by {ctx.author.mention}""")

                self.music_queue.insert(
                    0,
                    [song, voice_channel,ctx.author.mention]
                )
                
                print(self.music_queue[0][0]['title'])
                if self.is_playing == False or (self.vc == "" or not self.vc.is_connected() or self.vc == None):
                    await self.play_music(ctx)

    @commands.command(name="r", help="Removes the song indexed in the queue")
    @commands.has_any_role('DJ','Moderator', 'GDSC Lead', 'Core Team')
    async def remove(self, ctx, *args):
        query = "".join(*args)
        index = 0
        negative = True if (query[0]=='-') else False
        if not negative:
            for i in range(len(query)):
                convert = (int)(query[i])
                index = index*10 + convert
        index -= 1
        
        if negative:
            await ctx.send("Index cannot be less than one")
        elif(index>=len(self.music_queue)):
            await ctx.send("Wrong index. Indexed music not present in the queue")
        else:
            await ctx.send(f""":x: Song {query} removed from queue by {ctx.author.mention}""")
            self.music_queue.pop(index)

    @commands.command(name="help", help="Return all the possible commands")
    async def help(self, ctx):
        help_message = 
        discord.Embed(
    description="!p : Plays the song with search keyword following the command\n!s : Skips the currently playing music\n!q : Shows the music added in list/queue\n!l : Commands the bot to leave the voice channel\n!pn : Moves the song to the top of the queue\n!r : removes song from queue at index given.\n!help : shows all the commands of the bot.",
    color=0xFF0000 #i added hex code of red u can add any like of blue
)
        await ctx.send(embed=help_message)
