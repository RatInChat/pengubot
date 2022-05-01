from urllib.parse import uses_relative
import discord
from discord.ext import commands, tasks
from itertools import cycle
import random
import DiscordEconomy
import asyncio
from DiscordEconomy.Sqlite import Economy
import os
from datetime import datetime

intents = discord.Intents.all()

client = commands.Bot(command_prefix='p!', case_insensitive=True, intents=intents)
status = cycle([f'{len(client.guilds)} servers!', "ICE", "p!help"])
economy = Economy()

@client.event
async def on_ready():
    print("client is online.")
    change_status.start()


def is_it_me(ctx):
  return ctx.author.id == 826175329110196244, 728619566997045290

def owner(ctx):
  return ctx.author.id == 826175329110196244


@tasks.loop(seconds=3)
async def change_status(): 
      await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(status)))

@client.command(pass_context=True)
@commands.check(is_it_me)
async def broadcast(ctx, *, msg):
    for server in client.guilds:
        for channel in server.text_channels:
            try:
                await channel.send(msg)
            except Exception:
                continue
            else:
                break



# actuall economy system down here

async def is_registered(ctx):
    r = await economy.is_registered(ctx.message.author.id)
    return r


is_registered = commands.check(is_registered)




items_list = {
    "Items": {
        "crystal": {
            "available": True,
            "price": 300,
            "description": "Sacred Penguin Crystal. Sad thing it's fake."
        },
        "fishing rod": {
            "available": True,
            "price": 1200,
            "description": "Your not a human but it's handy for 2 in 1 fishing!"
          # line 69. milestone. nice. XD yes. we should leave this here LMAO
        },
        "pickaxe": {
            "available": True,
            "price": 1500,
            "description": "Look for the true Sacred Penguin Crystal!"
        },
        "sword": {
            "available": True,
            "price": 700,
            "description": "Violence is the answer. You can contribute to the penguin mafia now!"
        },
        "lockedwallet": {
          "available": True,
          "price": 10000,
          "description": "Make your wallet safe against robbers! When you lock your wallet you can not rob other people."
        },
        "PenguinMafia Pass": {
          "available": False,
          "price": "You have to put a secret message...",
          "description": "Pass to the PenguinMafia."
        }
    }}

# error handling
@client.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if isinstance(error, commands.CommandNotFound):
        embed.add_field(name="Error", value="""This command does not exists!
                                            If you want to use shop, type p!shop or if you can't find anything type p!help""")
        await ctx.send(embed=embed)

        await ctx.send(embed=embed)
    elif error.__class__ is commands.CommandOnCooldown:
        cd: int = int(error.retry_after)
        await ctx.send(f'Sorry, you are on cooldown, which ends in **{cd//86400}d {(cd//3600)%24}h {(cd//60)%60}m {cd % 60}s**.')
        return
    else:
        embed.add_field(name="Error", value=error)

@client.command(aliases=['bal'])
async def balance(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.message.author

    await economy.is_registered(member.id)
    user_account = await economy.get_user(member.id)

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"{member.display_name}'s balance", value=f"""Bank: **{user_account.bank}**
                                                                     Wallet: **{user_account.wallet}**
                                                                     Items: **{', '.join(user_account.items)}**
                                                                     Meat: **{user_account.meat}**
                                                                     Plants: **{user_account.plant}**
                                                                     Insects: **{user_account.bug}
                                                                     Penguin Crystal: **{user_account.crystal}
                                                                     Warns: **{user_account.warn}**
                                                                     Fish: **{user_account.fish}
                                                                     """)

    await ctx.send(embed=embed)

@client.command(aliases=['d'])
@commands.cooldown(1, 86400, commands.BucketType.user)
@is_registered
async def daily(ctx: commands.Context):
    random_amount = random.randint(50, 150)
    await economy.add_money(ctx.message.author.id, "wallet", random_amount)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"Reward", value=f"Successfully claimed daily!")
    await ctx.send(embed=embed)

@client.command(aliases=['m'])
@commands.cooldown(1, 2628000, commands.BucketType.user)
@is_registered
async def monthly(ctx: commands.Context):
    random_amount = random.randint(3000, 6000)
    await economy.add_money(ctx.message.author.id, "wallet", random_amount)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.add_field(name=f"Reward", value=f"Successfully claimed monthly!")

    await ctx.send(embed=embed)
@client.command(aliases=['flip','cf','coin'])
@is_registered
@commands.cooldown(1, 60, commands.BucketType.user)
async def coinflip(ctx: commands.Context, money: int, arg: str):
    arg = arg.lower()
    random_arg = random.choice(["tails", "heads"])
    multi_money = money * 2
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r.wallet >= money:
        if arg == random_arg:
            await economy.add_money(ctx.message.author.id, "wallet", multi_money)

            embed.add_field(name="Coinflip", value=f"You won coinflip! - {random_arg}")

            await ctx.send(embed=embed)
        else:
            await economy.remove_money(ctx.message.author.id, "wallet", money)

            embed.add_field(name="Coinflip", value=f"You lost coinflip! - {random_arg}")

            await ctx.send(embed=embed)

    else:
        embed.add_field(name="Coinflip", value=f"You don't have enough money!")

        await ctx.send(embed=embed)


@client.command(aliases=['slot'])
@is_registered
@commands.cooldown(1, 60, commands.BucketType.user)
async def slots(ctx: commands.Context, money: int):
    money_multi = money * 2
    random_slots_data = [None for _ in range(9)]
    i = 0
    for _ in random_slots_data:
        random_slots_data[i] = random.choice(["🍪", "🍌", "🫔",
                                              "🦞️", "🧋", "🐧"])

        i += 1
        if i == len(random_slots_data):
            break
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    if r.wallet >= money:

        embed.add_field(name="Slots", value=f"""{random_slots_data[0]} | {random_slots_data[1]} | {random_slots_data[2]}
                                                {random_slots_data[3]} | {random_slots_data[4]} | {random_slots_data[5]}
                                                {random_slots_data[6]} | {random_slots_data[7]} | {random_slots_data[8]}
                                            """)

        await ctx.send(embed=embed)

        if random_slots_data[3] == random_slots_data[4] and random_slots_data[5] == random_slots_data[3]:
            await economy.add_money(ctx.message.author.id, "wallet", money_multi)
            await ctx.send("You won!")
        else:
            await economy.remove_money(ctx.message.author.id, "wallet", money)
            await ctx.send("You lose!")

    else:
        embed.add_field(name="Slots", value=f"You don't have enough 🧊!")

        await ctx.send(embed=embed)


@client.command(aliases=['w','with'])
@is_registered
async def withdraw(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.bank >= money:
        await economy.add_money(ctx.message.author.id, "wallet", money)
        await economy.remove_money(ctx.message.author.id, "bank", money)

        embed.add_field(name="Withdraw", value=f"Successfully withdrawn 🧊{money}!")

        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Withdraw", value=f"You don't have enough 🧊 to withdraw!")

        await ctx.send(embed=embed)


@client.command(aliases=['dep'])
@is_registered
async def deposit(ctx: commands.Context, money: int):
    r = await economy.get_user(ctx.message.author.id)
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if r.wallet >= money:
        await economy.add_money(ctx.message.author.id, "bank", money)
        await economy.remove_money(ctx.message.author.id, "wallet", money)

        embed.add_field(name="Deposit", value=f"Successfully deposited 🧊{money}!")

        await ctx.send(embed=embed)

    else:

        embed.add_field(name="Deposit", value=f"You don't have enough 🧊 to deposit!")

        await ctx.send(embed=embed)


@client.group(invoke_without_command=True)
@is_registered
async def shop(ctx: commands.Context):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    embed.add_field(name="Shop", value=f"In the shop you can buy and sell items!", inline=False)
    embed.add_field(name="Available commands", value=f"""p!shop buy <item>
                                                         p!shop sell <item>
                                                         p!shop items""", inline=False)

    await ctx.send(embed=embed)


@shop.command()
@is_registered
async def items(ctx: commands.Context):
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.set_author(name="Items")

    for item in items_list["Items"].items():

        if item[1]["available"]:
            embed.add_field(name=item[0].capitalize(), value=f"""Price: **{item[1]['price']}**
                                                                 Description: **{item[1]['description']}**""")


    await ctx.send(embed=embed)


@shop.command()
@is_registered
async def buy(ctx: commands.Context, *, _item: str):
    _item = _item.lower()
    _cache = []
    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    for item in items_list["Items"].items():
        if item[0] == _item:
            _cache.append(item[0])

            r = await economy.get_user(ctx.message.author.id)

            if item[0] in r.items:
                embed.add_field(name="Error", value=f"You already have that item!")

                await ctx.send(embed=embed)

                return

            if r.wallet >= item[1]["price"]:
                await economy.add_item(ctx.message.author.id, item[0])
                await economy.remove_money(ctx.message.author.id, "wallet", item[1]["price"])

                embed.add_field(name="Success", value=f"Successfully bought **{item[0]}**!")

                await ctx.send(embed=embed)

            else:

                embed.add_field(name="Error", value=f"You don't have enought 🧊 to buy this item!")

                await ctx.send(embed=embed)
            break

    if len(_cache) <= 0:
        embed.add_field(name="Error", value="Item with that name does not exists!")
        await ctx.send(embed=embed)


@shop.command()
@is_registered
async def sell(ctx: commands.Context, *, _item: str):
    r = await economy.get_user(ctx.message.author.id)

    _item = _item.lower()

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )

    if _item in r.items:
        for item in items_list["Items"].items():
            if item[0] == _item:
                item_prc = item[1]["price"] / 2

                await economy.add_money(ctx.message.author.id, "bank", item_prc)
                await economy.remove_item(ctx.message.author.id, item[0])

                embed.add_field(name="Success", value=f"Successfully sold **{item[0]}**!")
                await ctx.send(embed=embed)
                break
    else:

        embed.add_field(name="Error", value=f"You don't have this item!")
        await ctx.send(embed=embed)


@client.command(aliases=['hr',"horse"])
@is_registered
@commands.cooldown(1, 60, commands.BucketType.user)
async def horse_racing(ctx: commands.Context, money: int):
    user = await economy.get_user(ctx.author.id)

    if not user.wallet >= money:
        return await ctx.send(content="You don't have enough 🧊 to play.")

    author_path = ["🏇", "🟦", "🟦", "🟦", "🟦",
                   "🟦",
                   "🟦", "🟦", "🟦", "🟦", "  🏁"]

    enemy_path = ["🏇", "🟥", "🟥", "🟥", "🟥", "🟥",
                  "🟥", "🟥", "🟥", "🟥", "  🏁"]

    embed = discord.Embed(
        colour=discord.Color.from_rgb(244, 182, 89)
    )
    embed.set_author(name="Horse race")
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)

    msg = await ctx.send(embed=embed)
    await asyncio.sleep(3)

    author_path[0] = "🟦"
    enemy_path[0] = "🟥"

    author_path_update = random.randint(2, 6)
    enemy_path_update = random.randint(2, 6)

    author_path[author_path_update] = "🏇"
    enemy_path[enemy_path_update] = "🏇"

    embed.clear_fields()
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)

    await msg.edit(embed=embed)
    await asyncio.sleep(3)

    author_path[author_path_update] = "🟦"
    enemy_path[enemy_path_update] = "🟥"

    author_path_update = random.randint(author_path_update, 9)
    enemy_path_update = random.randint(enemy_path_update, 9)

    author_path[author_path_update] = "🏇"
    enemy_path[enemy_path_update] = "🏇"

    embed.clear_fields()
    embed.add_field(name="You:", value="".join(author_path), inline=False)
    embed.add_field(name=f"Enemy:", value="".join(enemy_path),
                    inline=False)
    await msg.edit(embed=embed)

    if author_path_update > enemy_path_update:
        await economy.add_money(ctx.author.id, "wallet", money * 2)

        await ctx.send(content="You won!")

    else:
        await economy.remove_money(ctx.author.id, "wallet", money)

        await ctx.send(content="You lose!")

@client.command()
@is_registered
@commands.cooldown(1, 60, commands.BucketType.user)
async def roll(ctx, money: int):
  random_roll = random.randrange(1, 7)
  multi_money = money * 2
  semi_money = money * 1.5
  semi_lose = money / 1/5
  r = await economy.get_user(ctx.message.author.id)
  embed = discord.Embed(
      colour=discord.Color.from_rgb(149, 242, 255)
    )
  dice = {
    "1" : "<:dice1:968321245751939082>",
    "2" : "<:dice2:968321245781307402>",
    "3" : "<:dice3:968321245521281054>",
    "4" : "<:dice4:968321245416398868>",
    "5" : "<:dice5:968321246129438790>",
    "6" : "<:dice6:968321245210886215>"
  }
  outcome = " "
  for number in str(random_roll):
     outcome += dice.get(number, number) + " "

  if r.wallet >= money:
      if random_roll >= 5:
          await economy.add_money(ctx.message.author.id, "wallet", multi_money)

          embed.add_field(name="Roll", value=f"You got {random_roll}{outcome} and won {multi_money}")

          await ctx.send(embed=embed)
      elif random_roll == 3:
          await economy.remove_money(ctx.message.author.id, "wallet", multi_money)

          embed.add_field(name="Roll", value=f"You got {random_roll}{outcome} and lost {multi_money}")
      if random_roll == 4:
          await economy.add_money(ctx.message.author.id, "wallet", semi_money)

          embed.add_field(name="Roll", value=f"You got {random_roll}{outcome} and won {semi_money}")

          await ctx.send(embed=embed)
      elif random_roll <= 2:
          await economy.remove_money(ctx.message.author.id, "wallet", multi_money)

          embed.add_field(name="Roll", value=f"You got {random_roll}{outcome} and lost {semi_lose}")
          await ctx.send(embed=embed)

  else:
      embed.add_field(name="Roll", value=f"You don't have enough money!")

      await ctx.send(embed=embed)


# complicated robing command
@client.command()
@is_registered
async def rob(ctx, member: discord.Member):
  role = discord.utils.get(ctx.guild.roles, name="safe")
  if role not in ctx.author.roles:
    user = await economy.get_user(member.id)
    if role not in member.roles:
      if user.wallet >= 100:
        chance = random.randrange(1, 3)
        if chance == 1:
          amount = random.randrange(10, 20)
          await economy.remove_money(member.id, "wallet", amount)
          await ctx.send(f"You robbed {amount} from {member}! You really are a bad person.")
        else:
          losings = random.randrange(20, 30)
          await ctx.send(f"You failed to rob {member} and they have fined you {losings}!")
          await economy.add_money(member.id, "wallet", losings)
      else:
        await ctx.send(f"{member} does not have enough money for you to rob!!")
    else:
      await ctx.send(f"You cannot steal from {member} because they have disabled robing!")
  else:
    await ctx.send("You can not use that command! You are safe from robing but you cannot rob too! Use p!enable to enable robing for you!")
    
@client.command(aliases=['send'])
@is_registered
async def give(ctx, member: discord.Member, amount: int):
  user = await economy.get_user(ctx.author.id)
  if amount <= 0:
    await ctx.channel.send("You have to give at least 🧊1!")
  elif amount > user.wallet:
    await ctx.channel.send("You do not have that much money!")
  elif str(amount) == "all":
    await economy.add_money(member.id, "wallet", user.wallet)
    await economy.remove_money(ctx.author,id, "wallet", user.wallet)
    await ctx.channel.send(f"gave {member} all your money!")
  else:
    await economy.remove_money(ctx.author.id, "wallet", amount)
    await economy.add_money(member.id, "wallet", amount)
    await ctx.channel.send(f"Gave {member} 🧊{amount}!")
@client.command()
@is_registered
@commands.check(owner)
async def devgive(ctx, member: discord.Member, amount: int):
  user = await economy.get_user(ctx.author.id)
  if amount <= 0:
    await ctx.channel.send("You have to send positives!!")
  else:
    await economy.add_money(member.id, "wallet", amount)
    await ctx.channel.send(f"Gave {member} 🧊{amount}!")
# enable and disable robing
@client.command(aliases=["en"])
@is_registered
async def enable(ctx):
  hi = await economy.get_user(ctx.author.id)
  hi = str(hi)
  if "lockedwallet" in hi:
    role = discord.utils.get(ctx.guild.roles, name="safe")
    if role in ctx.author.roles:
       await ctx.author.remove_roles(role)
       await ctx.send("Enabled robing!")
    else:
      await ctx.send("You have already enabled robing!")
  else:
    await ctx.channel.send("You do not have Locked Wallet!")

@client.command(aliases=["dis"])
@is_registered
async def disable(ctx):
  hi = await economy.get_user(ctx.author.id)
  hi = str(hi)
  if "lockedwallet" in hi:
    role = discord.utils.get(ctx.guild.roles, name="safe")
    if role not in ctx.author.roles:
        await ctx.author.add_roles(role)
        await ctx.send("Disabled robing!")
    else:
      await ctx.send("You have already disabled robing!")
  else:
    await ctx.channel.send("You do not have Locked Wallet!")

# really complicated penguin mafia thing
@client.command()
@is_registered
async def join(ctx):
  hi = await economy.get_user(ctx.author.id)
  hi = str(hi)
  if "PenguinMafia Pass" not in hi:
    await ctx.channel.send('Join The PenguinMafia!')
    await asyncio.sleep(1)
    await ctx.channel.send('Are you sure you want to join?')
    await asyncio.sleep(1)
    await ctx.channel.send('It will cost you 🧊100 a month! (for now it is free... acutally it\'s not! :) or maybe it is! )')
    await asyncio.sleep(1)
    await ctx.channel.send('Please reply "yes" or "no".')
  
    try:
      message = await client.wait_for('message', timeout=45.0)
    except:
      await asyncio.TimeoutError
      await ctx.channel.send('You ran out of time to answer!')
    if message.content == 'yes':
      message1 = await ctx.channel.send('Joining.')
      await asyncio.sleep(1)
      await message1.edit(content="Joining..")
      await asyncio.sleep(1)
      await message1.edit(content="Joining...")
      await asyncio.sleep(1)
      await economy.add_item(ctx.author.id, "PenguinMafia Pass")
      await message1.edit(content="You joined the PenguinMafia!")
    if message.content == 'no':
      await ctx.send('Ok.')
    else:
      await ctx.send("You didn't reply with yes or no. Try again next time!")
  else:
    await ctx.send("You have already joined!")
    
@client.command(aliases=["tu"])
async def tutorial(ctx, member: discord.Member = None):
  member = member or ctx.message.author
  embed = discord.Embed(colour=discord.Color.red())
  embed.add_field(name=f"Welcome to the tutorial {member.display_name}!",
  value="First run `p!bal`")
  await ctx.channel.send(embed=embed)
  try:
    message = await client.wait_for('message', timeout=45.0)
  except:
    await asyncio.TimeoutError
    await ctx.channel.send('You ran out of time to answer!')
  if message.content == "p!bal":
    await ctx.channel.send("This shows you your balance. Here you can see how much money you, and items, you have. Your wallet contains money you can use. Your bank contains money that is safely stored untill you want to use it. You cannot use the money in your bank unless you run `p!with amount`. But for now just send `p!daily`!")
  try:
    message2 = await client.wait_for('message', timeout=45.0)
  except:
    await asyncio.TimeoutError
    await ctx.channel.send("You ran out of time to answer!")
  if message2.content == "p!daily":
    await ctx.channel.send("Coming soon!")

async def main():
  if __name__ == '__main__':
      # When running this file, if it is the 'main' file
      # I.E its not being imported from anther python file run this
      for file in os.listdir("./cogs"):
          if file.endswith(".py") and not file.startswith("_"):
              await client.load_extension(f"cogs.{file[:-3]}")
      await client.start("Not a token")
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
