import discord
from discord.ext import commands
import os


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='=', intents=intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f"cogs.{filename[:-3]}")

with open("BOT_TOKEN") as file:
    bot.run(file.read())
