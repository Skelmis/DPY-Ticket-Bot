import discord
from discord.ext import commands

from utils.jsonLoader import read_json
from utils.util import (
    CreateNewTicket,
    SudoCreateNewTicket,
    CloseTicket,
    IsATicket,
    ReactionCreateNewTicket,
    SetupNewTicketMessage,
    CheckIfValidReactionMessage,
    ReactionCloseTicket,
)

bot = commands.Bot(
    command_prefix="..", case_insensitive=True, owner_id=271612318947868673
)
secret_file = read_json("secrets")

bot.new_ticket_channel_id = None
bot.log_channel_id = None
bot.category_id = None
bot.staff_role_id = None

@bot.event
async def on_ready():
    print("Lesh go!")
    await bot.change_presence(activity=discord.Game(name=".new for a ticket"))


@bot.event
async def on_raw_reaction_add(payload):
    # Check if its the bot adding the reaction
    if payload.user_id == bot.user.id:
        return

    # Check if its a valid reaction
    reaction = str(payload.emoji)
    if reaction not in ["🔒", "✅"]:
        return

    # Check its a valid reaction channel
    if not payload.channel_id == bot.new_ticket_channel_id and not IsATicket(
        str(payload.channel_id)
    ):
        return

    # Check its a valid message
    if not CheckIfValidReactionMessage(payload.message_id):
        return

    # Soooo, its valid message and reaction so go do logic bois

    data = read_json("config")
    if payload.message_id == data["ticketSetupMessageId"] and reaction == "✅":
        # We want a new ticket...
        await ReactionCreateNewTicket(bot, payload)
        
        # once the ticket is created remove the user reaction
        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction("✅", member)
        
        return

    elif reaction == "🔒":
        # Simply add a tick to the message
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.add_reaction("✅")

    elif reaction == "✅":
        # Time to delete the ticket!
        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        channel = bot.get_channel(payload.channel_id)
        await ReactionCloseTicket(bot, channel, member)


@bot.event
async def on_raw_reaction_remove(payload):
    # Check if its the bot adding the reaction
    if payload.user_id == bot.user.id:
        return

    # Check if its a valid reaction
    reaction = str(payload.emoji)
    if reaction not in ["🔒"]:
        return

    # Check its a valid reaction channel
    if not payload.channel_id == bot.new_ticket_channel_id and not IsATicket(
        str(payload.channel_id)
    ):
        return

    # Check its a valid message
    if not CheckIfValidReactionMessage(payload.message_id):
        return

    if reaction == "🔒":
        # Simply remove a tick from the message
        guild = bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(bot.user.id)

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction("✅", member)


@bot.command()
async def new(ctx, *, subject=None):
    await CreateNewTicket(bot, ctx, subject)


@bot.command()
async def close(ctx, *, reason=None):
    await CloseTicket(bot, ctx, reason)

#add users to a ticket - only staff role can add users
@bot.command()
@commands.has_role(bot.staff_role_id)
async def adduser(ctx, user: discord.Member):
    channel = ctx.channel
    if not CheckIfTicket(channel.id):
        await ctx.send("This is not a ticket! Users can only be added to a ticket channel")
        return

    await channel.set_permissions(user, read_messages=True, send_messages=True)
    await ctx.message.delete()

#remove users to a ticket - only staff role can remove users
@bot.command()
@commands.has_role(bot.staff_role_id)
async def removeuser(ctx, user: discord.Member):
    channel = ctx.channel
    if not CheckIfTicket(channel.id):
        await ctx.send("This is not a ticket! Users can only be removed from a ticket channel")
    else:
        await channel.set_permissions(user, read_messages=False, send_messages=False)
        await ctx.message.delete()
        
@bot.command()
@commands.is_owner()
async def sudonew(ctx, user: discord.Member):
    await ctx.message.delete()
    await SudoCreateNewTicket(bot, ctx.guild, user, ctx.message)


@bot.command()
@commands.is_owner()
async def setup(ctx):
    await SetupNewTicketMessage(bot)


@bot.command()
@commands.is_owner()
async def echo(ctx, channel: discord.TextChannel, *, content):
    await ctx.message.delete()
    embed = discord.Embed(
        description=content, color=0x808080, timestamp=ctx.message.created_at
    )
    embed.set_author(name=ctx.guild.me.display_name, icon_url=ctx.guild.me.avatar_url)
    await channel.send(embed=embed)


if __name__ == "__main__":
    bot.run(secret_file["token"])
