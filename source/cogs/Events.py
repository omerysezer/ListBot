import json
import discord
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('SERVER_SETTINGS.json', 'r') as file:
            server_data = json.load(file)

        # the dictionary in index 0 will save a key:value pair consisting of member id's and member nicknames
        # the list in index 1 will store the lists for the server
        server_data[guild.id] = [
            {},
            []
        ]

        with open('SERVER_SETTINGS.json', 'w') as file:
            json.dump(server_data, file)


def setup(bot):
    bot.add_cog(Events(bot))