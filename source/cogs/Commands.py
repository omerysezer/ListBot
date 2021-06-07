import sys
from typing import Optional
import discord
from discord.ext import commands
from JsonHandler import save, read


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    '''
    Command that allows admins to change other users nicknames and users to set their own names
    '''

    @commands.command()
    @commands.guild_only()
    async def setname(self, ctx, member: Optional[discord.Member] = None, *, name):
        admin_req = False
        if member:
            admin_req = True
        else:
            member = ctx.author

        if admin_req and not ctx.message.author.guild_permissions.administrator:
            return

        guild_key = str(ctx.guild.id)
        member_key = str(member.id)
        server_data = read()

        server_data[guild_key][0][member_key] = name

        save(server_data)

        await ctx.channel.send(f'The name for {member.mention} has been set to **\'{name}\'**')

    '''
    command that allows the user to see what their current nickname is
    '''

    @commands.command()
    @commands.guild_only()
    async def name(self, ctx):
        author_id = str(ctx.author.id)

        server_data = read()

        server_names_list = server_data[str(ctx.guild.id)][0]
        if author_id in server_names_list:
            name = server_names_list[author_id]
        else:
            name = ctx.author.nick

        await ctx.channel.send(f'Your name is {name}')

    '''
    Command that allows the user to create a list
    '''

    @commands.command()
    @commands.guild_only()
    async def create(self, ctx, *, name):
        list_name = name
        guild_id = str(ctx.guild.id)
        role_id = (await ctx.guild.create_role(name=list_name, mentionable=True)).id

        server_settings = read()

        yes_list, no_list, maybe_list = [], [], []
        server_settings[guild_id][1].append([list_name, role_id, yes_list, no_list, maybe_list])

        save(server_settings)

        await ctx.channel.send(f'Created a new list: \'{list_name}\'')

    '''
    Command that allows the user to add themselves to the yes category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def yes(self, ctx, list_index):
        guild_key = str(ctx.guild.id)
        index = int(list_index) - 1

        server_settings = read()

        list = server_settings[guild_key][1][index]
        list_role = discord.utils.get(ctx.guild.roles, id=list[1])

        if ctx.author.id in list[2]:
            return
        if ctx.author.id in list[3]:
            list[3].remove(ctx.author.id)
            list[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)
        if ctx.author.id in list[4]:
            list[4].remove(ctx.author.id)
            list[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)
        if ctx.author.id not in list[2]:
            list[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)

        save(server_settings)

    '''
    Command that allows users to add themselves to the no category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def no(self, ctx, list_index):
        guild_key = str(ctx.guild.id)
        index = int(list_index) - 1

        server_settings = read()

        list = server_settings[guild_key][1][index]
        list_role = discord.utils.get(ctx.guild.roles, id=list[1])

        if ctx.author.id in list[3]:
            return
        if ctx.author.id in list[2]:
            list[2].remove(ctx.author.id)
            list[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id in list[4]:
            list[4].remove(ctx.author.id)
            list[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id not in list[3]:
            list[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)

        save(server_settings)

    '''
    Command that allows users to add themselves to the maybe category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def maybe(self, ctx, list_index):
        guild_key = str(ctx.guild.id)
        index = int(list_index) - 1

        server_settings = read()

        list = server_settings[guild_key][1][index]
        list_role = discord.utils.get(ctx.guild.roles, id=list[1])

        if ctx.author.id in list[4]:
            return
        if ctx.author.id in list[2]:
            list[2].remove(ctx.author.id)
            list[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id in list[3]:
            list[3].remove(ctx.author.id)
            list[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id not in list[4]:
            list[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)

        save(server_settings)

    '''
    Command that displays all the lists for the server
    '''

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx):
        guild_key = str(ctx.guild.id)

        server_settings = read()

        server_lists = server_settings[guild_key][1]

        server_lists = [list[0] for list in server_lists]

        lists_text = ''

        for i in range(len(server_lists)):
            lists_text += f'**{i + 1}.** {server_lists[i]}\n'

        if not lists_text:
            lists_text = 'There are no lists in this server'

        embed = discord.Embed(
            title='Lists',
            description=lists_text,
            color=0x8f24f9
        )

        #embed.add_field(name='\u200b', value=lists_text)
        embed.set_footer(text='\n\n=create [list name] to create a new list\n=list [list number] to view a list')

        await ctx.send(embed=embed)

    '''
    Command that shows all the members in the yes, no, and maybe categories of the specified list
    '''

    @commands.command()
    @commands.guild_only()
    async def list(self, ctx, i):
        guild_key = str(ctx.guild.id)
        index = int(i) - 1

        server_settings = read()

        member_list = server_settings[guild_key][0]
        list = server_settings[guild_key][1][index]
        list_name = list[0]
        yes_list, no_list, maybe_list = list[2], list[3], list[4]

        yes_names, no_names, maybe_names = '>>> \u200b', '>>> \u200b', '>>> \u200b'

        yes_list = [member_list[str(name)] if str(name) in member_list
                    else ctx.guild.get_member(name).nick if ctx.guild.get_member(name).nick
                    else ctx.guild.get_member(name).display_name
                    for name in yes_list]
        no_list = [member_list[str(name)] if str(name) in member_list
                   else ctx.guild.get_member(name).nick if ctx.guild.get_member(name).nick
                   else ctx.guild.get_member(name).display_name
                   for name in no_list]
        maybe_list = [member_list[str(name)] if str(name) in member_list
                      else ctx.guild.get_member(name).nick if ctx.guild.get_member(name).nick
                      else ctx.guild.get_member(name).display_name
                      for name in maybe_list]

        yes_list = [name[0:16]+'...' if len(name) >=17 else name for name in yes_list]
        no_list = [name[0:16]+'...' if len(name) >=17 else name for name in no_list]
        maybe_list = [name[0:16]+'...' if len(name) >=17 else name for name in maybe_list]

        yes_names, no_names, maybe_names = (yes_names + ',\n'.join(yes_list)), (no_names + ',\n'.join(no_list)), (maybe_names + ',\n'.join(maybe_list))

        if len(yes_names) == 0:
            yes_names = '\u200b'
        if len(no_names) == 0:
            no_names = '\u200b'
        if len(maybe_names) == 0:
            maybe_names = '\u200b'

        embed = discord.Embed(
            title=list_name,
            color=0x8f24f9
        )

        embed.add_field(name=':smiley: **__Yes__                                        **', value=yes_names)
        embed.add_field(name=':rage: **__No__                                        **', value=no_names)
        embed.add_field(name=':thinking: **__Maybe__**', value=maybe_names)
        embed.set_footer(text=f'\n=yes {i} to add yourself to the yes list\n=no {i} to add yourself to the no list\n=maybe {i} to add yourself to the maybe list')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
