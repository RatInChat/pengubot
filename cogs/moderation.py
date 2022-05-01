import discord
from discord.ext import commands

class Moderation(commands.Cog):

  def __init__(self, client):
    self.client = client
  @commands.Cog.listener()
  async def on_command_error(ctx, error): 
      pass
  def is_it_me(self, ctx):
    return ctx.author.id == 826175329110196244, 728619566997045290  
  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, member: discord.Member, *, reason=None): 
        await member.kick(reason=reason)
        await ctx.send(f"User {member.mention} has been kicked for {reason}")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, member: discord.Member, *, reason=None):
      await member.ban(reason=reason)
      await ctx.send(f"User {member.mention} has been banned for {reason}!")
  
    
  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def purge(self, ctx, amount=5):
      await ctx.channel.purge(limit=amount)
  
  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def unban(self, ctx, *, member):
      banned_users = await ctx.guild.bans()
      member_name, member_discriminator = member.split('#')
  
      for ban_entry in banned_users:
          user = ban_entry.user
  
          if (user.name, user.discriminator) == (member_name, member_discriminator):
              await ctx.guild.unban(user)
              await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
              return
  # errors
  
  @unban.error
  async def unban_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("<:Error:965018891573133312> - Please specify the user to unban! p!unban userid")
    elif isinstance(error, commands.BadArgument):
          await ctx.send('I could not find that member...')
  
  @kick.error
  async def kick_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("<:Error:965018891573133312> - Could not kick user! Please use the correct format! p!kick @user")
    elif isinstance(error, commands.BadArgument):
          await ctx.send('I could not find that member...')
      
  @ban.error 
  async def ban_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("<:Error:965018891573133312> - Could not ban user! Please use the correct format! p!ban @user")
    elif isinstance(error, commands.BadArgument):
          await ctx.send('<:thinking:970130578466803722> - I could not find that member...')

async def setup(client):
  await client.add_cog(Moderation(client))