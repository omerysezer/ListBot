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

    @commands.command()
    @commands.guild_only()
    async def create(self, ctx, *, name):
        list_name = name
        guild_id = str(ctx.guild.id)
        role_id = (await ctx.guild.create_role(name=list_name, mentionable=True)).id

        with open('SERVER_SETTINGS.json', 'r') as file:
            server_settings = json.load(file)

        yes_list, no_list, maybe_list = [], [], []
        server_settings[guild_id][1].append([list_name, role_id, yes_list, no_list, maybe_list])

        with open('SERVER_SETTINGS.json', 'w') as file:
            json.dump(server_settings, file)

        await ctx.channel.send(f'Created a new list: \'{list_name}\'')


def setup(bot):
    bot.add_cog(Commands(bot))
