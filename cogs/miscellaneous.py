import discord
from discord.ext import commands
from discord.utils import find
import asyncio


class Miscellaneous(commands.Cog):

  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_guild_join(self, guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Thank you for inviting me! I created a role for the p!rob command so that the `DISABLE` and `ENABLE` commands for robing could work!'.format(guild.name))
    await guild.create_role(name="safe")

async def setup(commands):
  await commands.add_cog(Miscellaneous(commands))