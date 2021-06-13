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

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_key = str(member.guild.id)
        server_data = read()
        member_list = server_data[guild_key][0]
        server_lists = server_data[guild_key][1]

        member_list.pop(str(member.id), None)

        for plan in server_lists:
            yes, no, maybe = plan[2], plan[3], plan[4]
            if member.id in yes:
                yes.remove(member.id)
            if member.id in no:
                no.remove(member.id)
            if member.id in maybe:
                maybe.remove(member.id)

        save(server_data)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.ArgumentParsingError):
            await ctx.send("Please don't put quotes `(\")` in your name, it hurts my robot head.")


def setup(bot):
    bot.add_cog(Events(bot))
