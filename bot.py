import traceback

import discord
from discord.ext import commands

from utils.util import (
    CreateNewTicket,
    SudoCreateNewTicket,
    CloseTicket,
    GetTicketSetupMessageId,
    CheckIfTicket,
    ReactionCreateNewTicket,
    SetupNewTicketMessage,
    CheckIfValidReactionMessage,
    ReactionCloseTicket,
)
from utils.json import read_json

bot = commands.Bot(
    command_prefix="..", case_insensitive=True, owner_id=271612318947868673
)
secret_file = read_json("secrets")

bot.new_ticket_channel_id = None
bot.log_channel_id = None
bot.category_id = None
bot.staff_role_id = None

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.colorList = [c for c in bot.colors.values()]


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
    if not payload.channel_id == bot.new_ticket_channel_id and not CheckIfTicket(
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
    if not payload.channel_id == bot.new_ticket_channel_id and not CheckIfTicket(
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
