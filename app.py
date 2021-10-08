from music import Music
import os
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='_', intents=intents)
bot.remove_command('help')
bot.add_cog(Music(bot))

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name='!help'))

bot.run(os.getenv('TOKEN'))
