import discord
from discord.ext import commands

from utils.json_loader import read_json
from utils.util import (
    CreateNewTicket,
    CloseTicket,
    IsATicket,
    ReactionCreateNewTicket,
    SetupNewTicketMessage,
    CheckIfValidReactionMessage,
)

bot = commands.Bot(
    command_prefix="-",
    case_insensitive=True,
    intents=discord.Intents.all(),
    activity=discord.Game(name=".new for a ticket"),
)
secret_file = read_json("secrets")

bot.new_ticket_channel_id = None
bot.log_channel_id = None
bot.category_id = None
bot.staff_role_id = None


@bot.event
async def on_ready():
    print("Lesh go!")


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

        # once the ticket is created remove the users reaction
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
        await CloseTicket(bot, channel, member)


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


@bot.command(name="new", description="Create a new ticket.", usage="[subject]")
@commands.guild_only()
async def new(ctx, *, subject=None):
    await CreateNewTicket(bot, ctx.guild, ctx.message.author, subject=subject)


@bot.command(name="close", description="Close this ticket.", usage="[reason]")
@commands.guild_only()
async def close(ctx, *, reason=None):
    await CloseTicket(bot, ctx.channel, ctx.author, reason)


@bot.command(name="adduser", description="Add a user to this ticket", usage="<user>")
@commands.guild_only()
@commands.has_role(bot.staff_role_id)
async def adduser(ctx, user: discord.Member):
    """
    add users to a ticket - only staff role can add users.
    """
    channel = ctx.channel
    if not IsATicket(channel.id):
        await ctx.send(
            "This is not a ticket! Users can only be added to a ticket channel"
        )
        return

    await channel.set_permissions(user, read_messages=True, send_messages=True)
    await ctx.message.delete()


@bot.command(
    name="removeuser", description="Removes a user from this ticket.", usage="<user>"
)
@commands.guild_only()
@commands.has_role(bot.staff_role_id)
async def removeuser(ctx, user: discord.Member):
    """
    removes users from a ticket - only staff role can remove users.
    """
    channel = ctx.channel
    if not IsATicket(channel.id):
        await ctx.send(
            "This is not a ticket! Users can only be removed from a ticket channel"
        )
        return

    await channel.set_permissions(user, read_messages=False, send_messages=False)
    await ctx.message.delete()


@bot.command(
    name="sudonew", description="Create a ticket on behalf of a user", usage="<user>"
)
@commands.guild_only()
@commands.is_owner()
async def sudonew(ctx, user: discord.Member):
    await CreateNewTicket(
        bot, ctx.guild, user, subject="Sudo Ticket Creation", message=ctx.message
    )


@bot.command(name="setup", description="Initial setup of the bot.")
@commands.guild_only()
@commands.is_owner()
async def setup(ctx):
    await SetupNewTicketMessage(bot)


@bot.command(
    name="echo",
    description="Repeat some text back using the bot.",
    usage="<channel> <message>",
)
@commands.guild_only()
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
