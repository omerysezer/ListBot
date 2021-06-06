import json
import discord
from discord.ext import commands
from JsonHandler import read, save

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_data = read()

        # the dictionary in index 0 will save a key:value pair consisting of member id's and member nicknames
        # the list in index 1 will store the lists for the server
        server_data[guild.id] = [
            {},
            []
        ]

        save(server_data)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        server_data = read()

        del server_data[str(guild.id)]

        save(server_data)


def setup(bot):
    bot.add_cog(Events(bot))