import asyncio
from typing import Optional
import discord
from discord.ext import commands
from JsonHandler import save, read

embed_color = 0x8f24f9


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    '''
    Command that allows admins to change other users nicknames and users to set their own names
    '''

    @commands.command()
    @commands.guild_only()
    async def setname(self, ctx, member: Optional[discord.Member] = None, *, name):
        new_name = discord.utils.remove_markdown(name)

        if not new_name:
            await ctx.send('My robotic brain couldn\'t handle that name. Try a different name.')
            return

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

        server_data[guild_key][0][member_key] = new_name

        save(server_data)

        if ctx.author is not member:
            await ctx.channel.send(f'The name for {member.mention} has been set to **\'{new_name}\'**')
            return

        await ctx.channel.send(f'Your name has been set to **\'{new_name}\'**.')

    '''
    command that allows the user to see what their current nickname is
    '''

    @commands.command()
    @commands.guild_only()
    async def name(self, ctx):
        author_id = str(ctx.author.id)

        server_data = read()

        names_dict = server_data[str(ctx.guild.id)][0]
        if author_id in names_dict:
            name = names_dict[author_id]
        else:
            name = ctx.author.nick

        await ctx.channel.send(f'Your name is **\'{name}\'**')

    '''
    Command that allows the user to create a list
    '''

    @commands.command()
    @commands.guild_only()
    async def create(self, ctx, *, list_name):
        name = discord.utils.remove_markdown(list_name)

        if not name:
            await ctx.send('My robotic brain couldn\'t handle that name. Try a different name.')
            return

        guild_id = str(ctx.guild.id)

        if len(name) >= 100:
            name = f'{name[0:96]}...'

        role_name = name
        role_id = (await ctx.guild.create_role(name=role_name, mentionable=True)).id

        server_data = read()

        yes_list, no_list, maybe_list = [], [], []
        server_data[guild_id][1].append([name, role_id, yes_list, no_list, maybe_list])

        save(server_data)

        await ctx.channel.send(f'Created a new list: \'{name}\'')

    '''
    Command that lets users delete a list
    '''

    @commands.command()
    @commands.guild_only()
    async def delete(self, ctx, list_number):
        index = int(list_number) - 1
        guild_key = str(ctx.guild.id)

        server_data = read()
        guild_lists = server_data[guild_key][1]

        if index < 0 or index >= len(guild_lists):
            await ctx.send('That list doesn\'t exist. Use =lists to see a list of all lists in this server')
            return

        li = guild_lists[index]
        name = li[0]
        role_id = li[1]

        del guild_lists[index]

        role = ctx.guild.get_role(role_id)
        if role:
            await role.delete()

        save(server_data)

        await ctx.send(f'Deleted the list {name}.')

    '''
    Command that lets users rename a specified list
    '''

    @commands.command()
    @commands.guild_only()
    async def rename(self, ctx, list_number):
        index = int(list_number) - 1
        guild_key = str(ctx.guild.id)

        server_data = read()
        guild_lists = server_data[guild_key][1]

        if index < 0 or index >= len(guild_lists):
            await ctx.send('That list doesn\'t exist. Use =lists to see a list of all lists in this server')
            return

        li = guild_lists[index]
        list_name = li[0]
        list_role_id = li[1]

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        await ctx.send(f'What do you want to rename **\'{list_name}\'** to? (Please respond within 1 minute)')
        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send('Sorry the timer ran out and I stopped listening.')
            return

        new_name = discord.utils.remove_markdown(message.content)

        if len(new_name) >= 100:
            new_name = f'{new_name[0:96]}...'

        if not new_name:
            await ctx.send('My robotic brain couldn\'t handle that name. Try a different name.')
            return

        role = discord.utils.get(ctx.guild.roles, id=list_role_id)
        await role.edit(name=new_name)
        li[0] = new_name
        save(server_data)

        await ctx.send(f'Changed the list name from **\'{list_name}\'** to **\'{new_name}\'**.')

    '''
    Command that allows the user to add themselves to the yes category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def yes(self, ctx, list_number):
        guild_key = str(ctx.guild.id)
        index = int(list_number) - 1

        server_data = read()

        if index < 0 or index >= len(server_data[guild_key][1]):
            await ctx.send('That list doesn\'t exist.\nUse =lists to view a list of all lists in this server')
            return

        li = server_data[guild_key][1][index]

        list_role = discord.utils.get(ctx.guild.roles, id=li[1])

        if ctx.author.id in li[2]:
            await ctx.send(f'You are already in the **yes** section of **\'{li[0]}\'**.')
            return
        if ctx.author.id in li[3]:
            li[3].remove(ctx.author.id)
            li[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)
        if ctx.author.id in li[4]:
            li[4].remove(ctx.author.id)
            li[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)
        if ctx.author.id not in li[2]:
            li[2].append(ctx.author.id)
            await ctx.author.add_roles(list_role)

        save(server_data)

        await ctx.send(f'Added you to the **yes** section of **\'{li[0]}\'**.')

    '''
    Command that allows users to add themselves to the no category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def no(self, ctx, list_index):
        guild_key = str(ctx.guild.id)
        index = int(list_index) - 1

        server_data = read()

        if index < 0 or index >= len(server_data[guild_key][1]):
            await ctx.send('That list doesn\'t exist.\nUse =lists to view a list of all lists in this server')
            return

        li = server_data[guild_key][1][index]
        list_role = discord.utils.get(ctx.guild.roles, id=li[1])

        if ctx.author.id in li[3]:
            await ctx.send(f'You are already in the **no** section of **\'{li[0]}\'**.')
            return
        if ctx.author.id in li[2]:
            li[2].remove(ctx.author.id)
            li[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id in li[4]:
            li[4].remove(ctx.author.id)
            li[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id not in li[3]:
            li[3].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)

        save(server_data)

        await ctx.send(f'Added you to the **no** section of **\'{li[0]}\'**.')

    '''
    Command that allows users to add themselves to the maybe category of a list
    '''

    @commands.command()
    @commands.guild_only()
    async def maybe(self, ctx, list_index):
        guild_key = str(ctx.guild.id)
        index = int(list_index) - 1

        server_data = read()

        if index < 0 or index >= len(server_data[guild_key][1]):
            await ctx.send('That list doesn\'t exist.\nUse =lists to view a list of all lists in this server')
            return
        li = server_data[guild_key][1][index]
        list_role = discord.utils.get(ctx.guild.roles, id=li[1])

        if ctx.author.id in li[4]:
            await ctx.send(f'You are already in the **maybe** section of **\'{li[0]}\'**.')
            return
        if ctx.author.id in li[2]:
            li[2].remove(ctx.author.id)
            li[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id in li[3]:
            li[3].remove(ctx.author.id)
            li[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)
        if ctx.author.id not in li[4]:
            li[4].append(ctx.author.id)
            await ctx.author.remove_roles(list_role)

        save(server_data)

        await ctx.send(f'Added you to the **maybe** section of **\'{li[0]}\'**.')

    '''
    Command that displays all the lists for the server
    '''

    @commands.command()
    @commands.guild_only()
    async def lists(self, ctx):
        guild_key = str(ctx.guild.id)

        server_data = read()

        server_lists = server_data[guild_key][1]

        server_lists = [li[0] for li in server_lists]

        lists_text = ''

        for i in range(len(server_lists)):
            lists_text += f'**{i + 1}.** {server_lists[i]}\n'

        if not lists_text:
            lists_text = 'There are no lists in this server'

        embed = discord.Embed(
            title='Lists',
            description=lists_text,
            color=embed_color
        )

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

        server_data = read()

        if index < 0 or index >= len(server_data[guild_key][1]):
            await ctx.send('That list doesn\'t exist.\nUse =lists to view a list of all lists in this server')
            return

        member_list = server_data[guild_key][0]
        li = server_data[guild_key][1][index]
        list_name = li[0]
        yes_members_lists, no_members_lists, maybe_members_list = li[2], li[3], li[4]
        # quote text will not occur without the empty white space characters \u200b
        yes_names, no_names, maybe_names = '>>> \u200b', '>>> \u200b', '>>> \u200b'

        def swap_ids_for_names(member_id: int):
            def get_name(x: int):
                return member_list.get(str(x)) or ctx.guild.get_member(x).nick or ctx.guild.get_member(x).display_name

            name = get_name(member_id)
            if len(name) >= 20:
                name = f'{name[0:16]}...'
            return name

        yes_members_lists = list(map(swap_ids_for_names, yes_members_lists))
        no_members_lists = list(map(swap_ids_for_names, no_members_lists))
        maybe_members_list = list(map(swap_ids_for_names, maybe_members_list))

        yes_names, no_names, maybe_names = (yes_names + '\n'.join(yes_members_lists)), (no_names + '\n'.join(no_members_lists)), (maybe_names + '\n'.join(maybe_members_list))

        embed = discord.Embed(
            title=list_name,
            color=embed_color
        )

        embed.add_field(name=f':smiley: **Yes ({len(yes_members_lists)})                   **', value=yes_names)
        embed.add_field(name=f':rage: **No ({len(no_members_lists)})                      **', value=no_names)
        embed.add_field(name=f':thinking: **Maybe ({len(maybe_members_list)})**', value=maybe_names)
        embed.set_footer(text=f'\n=yes {i} to add yourself to the yes list\n=no {i} to add yourself to the no list\n=maybe {i} to add yourself to the maybe list')
        await ctx.send(embed=embed)

    '''
    Help Command
    '''

    @commands.command()
    @commands.guild_only()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Help',
            description='Help Command',
            color=embed_color
        )

        embed.add_field(name='**=create [list name]**', value='Creates a new list', inline=False)

        embed.add_field(name='**=delete [list number]**', value='Deletes the list', inline=False)

        embed.add_field(name='**=rename [list number]**', value='Renames a list', inline=False)

        embed.add_field(name='**=lists**', value='Shows all the lists', inline=False)

        embed.add_field(name='**=list [list number]**', value='Shows the list\'s details', inline=False)

        embed.add_field(name='**=yes [list number]**', value='Adds you to the *yes* section of the list', inline=False)

        embed.add_field(name='**=no [list number]**', value='Adds you to the *no* section of the list', inline=False)

        embed.add_field(name='**=maybe [list number]**', value='Adds you to the *maybe* section of the list', inline=False)

        embed.add_field(name='**=name**', value='Shows what your nickname is', inline=False)

        embed.add_field(name='**=setname [ping a user] [name]**', value='`If no user is included` set your own nickname\n'
                                                                        '`If a user is included` set that user\'s nickname **[admins only]**', inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
