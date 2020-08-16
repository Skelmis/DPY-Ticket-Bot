import random
import discord

from utils.jsonLoader import read_json, write_json


def GetTicketCount():
    data = read_json("config")
    return data["ticketCount"]


def IncrementTicketCount():
    data = read_json("config")
    data["ticketCount"] += 1
    write_json(data, "config")


def GetTicketSetupMessageId():
    data = read_json("config")
    return data["ticketSetupMessageId"]


async def SendLog(
    bot,
    ctx,
    channel,
    contentOne="Default Message",
    contentTwo="\uFEFF",
    color=0x808080,
    file=None,
):
    embed = discord.Embed(
        title=f"{contentOne}",
        description=f"{contentTwo}",
        colour=color,
        timestamp=ctx.message.created_at,
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed)
    if file:
        await channel.send(file=file)


async def ReactionSendLog(
    bot,
    author,
    channel,
    contentOne="Default Message",
    contentTwo="\uFEFF",
    color=0x808080,
    file=None,
):
    embed = discord.Embed(
        title=f"{contentOne}", description=f"{contentTwo}", colour=color,
    )
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    await channel.send(embed=embed)
    if file:
        await channel.send(file=file)


async def SudoSendLog(
    bot,
    author,
    message,
    channel,
    contentOne="Default Message",
    contentTwo="\uFEFF",
    color=0x808080,
    file=None,
):
    embed = discord.Embed(
        title=f"{contentOne}",
        description=f"{contentTwo}",
        colour=color,
        timestamp=message.created_at,
    )
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    await channel.send(embed=embed)
    if file:
        await channel.send(file=file)


def LogNewTicketChannel(channelId, ticketId):
    data = read_json("config")
    data[str(channelId)] = {}
    data[str(channelId)]["id"] = ticketId
    data[str(channelId)]["reactionMsgId"] = None
    write_json(data, "config")


def IsATicket(channelId):
    data = read_json("config")
    return str(channelId) in data


def GetTicketId(channelId):
    data = read_json("config")
    return data[str(channelId)]["id"]


def RemoveTicket(channelId):
    data = read_json("config")
    data.pop(str(channelId))
    write_json(data, "config")


async def NewTicketSubjectSender(ctx, channel, subject):
    if subject == "No subject specified.":
        return
    embed = discord.Embed(
        title="Provided subject for ticket:",
        description=subject,
        color=0x808080,
        timestamp=ctx.message.created_at,
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed)


async def NewTicketEmbedSender(bot, author, channel):
    content = f"""
    **Hello {author.display_name}**

    This is your support ticket, how can we help you?

    `Our team will be with you shortly.`
    """
    embed = discord.Embed(description=content, color=0x808080)
    m = await channel.send(f"{author.mention} | <@&{bot.staff_role_id}>", embed=embed)
    await m.add_reaction("🔒")

    data = read_json("config")
    data[str(channel.id)]["reactionMsgId"] = m.id
    write_json(data, "config")


async def ReactionCreateNewTicket(bot, payload):
    subject = "No subject specified."
    ticketId = GetTicketCount() + 1

    guild = bot.get_guild(int(payload.guild_id))
    author = guild.get_member(int(payload.user_id))
    staffRole = guild.get_role(bot.staff_role_id)
    logChannel = bot.get_channel(bot.log_channel_id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        staffRole: discord.PermissionOverwrite(read_messages=True),
        author: discord.PermissionOverwrite(read_messages=True),
    }

    channel = await guild.create_text_channel(
        name=f"Support Ticket #{ticketId}",
        overwrites=overwrites,
        category=bot.get_channel(bot.category_id),
    )

    LogNewTicketChannel(channel.id, ticketId)
    await ReactionSendLog(
        bot,
        author,
        logChannel,
        f"Created ticket with ID {ticketId}",
        f"Ticket Creator: {author.mention}(`{author.id}`)\nChannel: {channel.mention}({channel.name})\nSubject: {subject}",
        0xB4DA55,
    )

    await NewTicketEmbedSender(bot, author, channel)
    IncrementTicketCount()


async def CreateNewTicket(bot, ctx, subject=None):
    subject = subject or "No subject specified."
    ticketId = GetTicketCount() + 1
    staffRole = ctx.guild.get_role(bot.staff_role_id)
    logChannel = bot.get_channel(bot.log_channel_id)

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        staffRole: discord.PermissionOverwrite(read_messages=True),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
    }

    channel = await ctx.guild.create_text_channel(
        name=f"Support Ticket #{ticketId}",
        overwrites=overwrites,
        category=bot.get_channel(bot.category_id),
    )

    LogNewTicketChannel(channel.id, ticketId)
    await SendLog(
        bot,
        ctx,
        logChannel,
        f"Created ticket with ID {ticketId}",
        f"Ticket Creator: {ctx.author.mention}(`{ctx.author.id}`)\nChannel: {channel.mention}({channel.name})\nSubject: {subject}",
        0xB4DA55,
    )

    await NewTicketEmbedSender(bot, ctx.message.author, channel)
    await NewTicketSubjectSender(ctx, channel, subject)
    await ctx.message.delete()
    IncrementTicketCount()


async def SudoCreateNewTicket(bot, guild, author, message):
    ticketId = GetTicketCount() + 1
    staffRole = guild.get_role(bot.staff_role_id)
    logChannel = bot.get_channel(bot.log_channel_id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        staffRole: discord.PermissionOverwrite(read_messages=True),
        author: discord.PermissionOverwrite(read_messages=True),
    }

    channel = await guild.create_text_channel(
        name=f"Support Ticket #{ticketId}",
        overwrites=overwrites,
        category=bot.get_channel(bot.category_id),
    )

    LogNewTicketChannel(channel.id, ticketId)
    await SudoSendLog(
        bot,
        author,
        message,
        logChannel,
        f"Created ticket with ID {ticketId}",
        f"Ticket Creator: {author.mention}(`{author.id}`)\nChannel: {channel.mention}({channel.name})",
        0xB4DA55,
    )
    await NewTicketEmbedSender(bot, author, channel)
    IncrementTicketCount()


async def CloseTicket(bot, ctx, reason=None):
    if not IsATicket(ctx.channel.id):
        await ctx.send("I cannot close this as it is not a ticket.")
        await ctx.message.delete()
        return

    # If u get here it means its a valid ticket
    reason = reason or "No closing reason specified."
    ticketId = GetTicketId(ctx.channel.id)
    messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()
    ticketContent = " ".join(
        [f"{message.content} | {message.author.name}\n" for message in messages]
    )
    with open(f"tickets/{ticketId}.txt", "w", encoding="utf8") as f:
        f.write(f"Here is the message log for ticket ID {ticketId}\n----------\n\n")
        f.write(ticketContent)

    fileObject = discord.File(f"tickets/{ticketId}.txt")
    logChannel = bot.get_channel(bot.log_channel_id)
    await SendLog(
        bot,
        ctx,
        logChannel,
        f"Closed Ticked ID {ticketId}",
        f"Close Reason: {reason}",
        0xF42069,
        fileObject,
    )
    await ctx.channel.delete()


async def ReactionCloseTicket(bot, channel, author):
    if not IsATicket(channel.id):
        await channel.send("I cannot close this as it is not a ticket.")
        return

    # If u get here it means its a valid ticket
    reason = "No closing reason specified."
    ticketId = GetTicketId(channel.id)
    messages = await channel.history(limit=None, oldest_first=True).flatten()
    ticketContent = " ".join(
        [f"{message.content} | {message.author.name}\n" for message in messages]
    )
    with open(f"tickets/{ticketId}.txt", "w", encoding="utf8") as f:
        f.write(f"Here is the message log for ticket ID {ticketId}\n----------\n\n")
        f.write(ticketContent)

    fileObject = discord.File(f"tickets/{ticketId}.txt")
    logChannel = bot.get_channel(bot.log_channel_id)
    await ReactionSendLog(
        bot,
        author,
        logChannel,
        f"Closed Ticked ID {ticketId}",
        f"Close Reason: {reason}",
        0xF42069,
        fileObject,
    )

    try:
        file = discord.File(f"tickets/{ticketId}.txt")
        embed = discord.Embed(description="Here is your support ticket log file")
        await author.send(embed=embed)
        await author.send(file=file)
    except:
        await ReactionSendLog(
            bot,
            author,
            logChannel,
            contentTwo=f"Failed to dm {author.name} for this ticket",
        )

    await channel.delete()


def CheckIfValidReactionMessage(msgId):
    data = read_json("config")

    if data["ticketSetupMessageId"] == msgId:
        return True

    data.pop("ticketSetupMessageId")
    data.pop("ticketCount")
    for value in data.values():
        if value["reactionMsgId"] == msgId:
            return True

    return False


async def SetupNewTicketMessage(bot):
    data = read_json("config")
    channel = bot.get_channel(bot.new_ticket_channel_id)

    embed = discord.Embed(
        title="Hand Trained Services",
        description="To purchase a service or enquire about one you must react with a tick",
        color=0xB4DA55,
    )
    m = await channel.send(embed=embed)
    await m.add_reaction("✅")
    data["ticketSetupMessageId"] = m.id

    write_json(data, "config")
