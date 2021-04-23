from dataclasses import dataclass

import discord
from discord.ext import commands


@dataclass
class Message:
    """Wraps message to provide author"""

    author: discord.Member


@dataclass
class ReactionContext:
    """
    A simple dataclass to be used in
    place of ctx during reaction events
    """

    guild: discord.Guild
    bot: commands.Bot
    message: Message
    channel: discord.TextChannel
    author: discord.Member
