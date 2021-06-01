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

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def change_users_name(self, ctx, member: discord.Member, *, name):
        guild_key = str(ctx.guild.id)
        member_key = str(member.id)
        with open('SERVER_SETTINGS.json', 'r') as file:
            server_data = json.load(file)

        server_data[guild_key][0][member_key] = name

        with open('SERVER_SETTINGS.json', 'w') as file:
            json.dump(server_data, file)

    @commands.command()
    @commands.guild_only()
    async def name(self, ctx):
        author_id = str(ctx.author.id)

        with open('SERVER_SETTINGS.json', 'r') as file:
            server_data = json.load(file)

        server_names_list = server_data[str(ctx.guild.id)][0]
        if author_id in server_names_list:
            name = server_names_list[author_id]
        else:
            name = ctx.author.nick

        await ctx.channel.send(f'Your name is {name}')


def setup(bot):
    bot.add_cog(Commands(bot))
