from music import music
import os
import discord
from discord.ext import commands

# from dotenv import load_dotenv
# load_dotenv()

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
bot.add_cog(music(bot))

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name='!help'))

# token = ""
# with open("tokens.txt") as file:
#     token = file.read()

# bot.run(token)

bot.run(os.getenv('TOKEN'))