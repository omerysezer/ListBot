import discord
from discord.ext import commands
import json


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def change_name(self, ctx, name):
        new_name = name
        guild_key = str(ctx.guild.id)
        with open('SERVER_SETTINGS.json', 'r') as file:
            server_data = json.load(file)

        server_data[guild_key][0][ctx.message.author.id] = name

        with open('SERVER_SETTINGS.json', 'w') as file:
            json.dump(server_data, file)

def setup(bot):
    bot.add_cog(Commands(bot))
