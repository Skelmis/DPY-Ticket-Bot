import json
from pathlib import Path

import discord
from discord.ext import commands

from utils import MyContext, JsonStore


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="-",
            case_insensitive=True,
            intents=discord.Intents.all(),
            activity=discord.Game(name=".new for a ticket"),
        )

        self.cwd = str(Path(__file__).parents[0])

        self.new_ticket_channel_id = None
        self.log_channel_id = None
        self.category_id = None
        self.staff_role_id = None

        self.ticket_db = JsonStore()

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f"{self.user.display_name} is up and ready to go!")


@bot.command(name="close", description="Close this ticket.", usage="[reason]")
@commands.guild_only()
async def close(ctx, *, reason=None):
    await CloseTicket(bot, ctx.channel, ctx.author, reason)


if __name__ == "__main__":
    bot = Bot()

    @bot.command(name="new", description="Create a new ticket.", usage="[subject]")
    @commands.guild_only()
    async def new(ctx, *, subject=None):
        await ctx.ticket.create_ticket(subject=subject)

    @bot.command(
        name="sudonew",
        description="Create a ticket on behalf of a user",
        usage="<user>",
    )
    @commands.guild_only()
    @commands.is_owner()
    async def sudonew(ctx, user: discord.Member):
        await ctx.ticket.create_ticket(subject="Sudo Ticket Creation", sudo_author=user)

    @bot.command(name="setup", description="Initial setup of the bot.")
    @commands.guild_only()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.ticket.setup_new_ticket_message()

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
        embed.set_author(
            name=ctx.guild.me.display_name, icon_url=ctx.guild.me.avatar_url
        )
        await channel.send(embed=embed)

    @bot.command(
        name="removeuser",
        description="Removes a user from this ticket.",
        usage="<user>",
    )
    @commands.guild_only()
    @commands.has_role(bot.staff_role_id)
    async def removeuser(ctx, user: discord.Member):
        await ctx.ticket.remove_user(user)

    @bot.command(
        name="adduser", description="Add a user to this ticket", usage="<user>"
    )
    @commands.guild_only()
    @commands.has_role(bot.staff_role_id)
    async def adduser(ctx, user: discord.Member):
        await ctx.ticket.add_user(user)

    @bot.command(name="close", description="Close this ticket.", usage="[reason]")
    @commands.guild_only()
    async def close(ctx, *, reason=None):
        await ctx.ticket.close_ticket(reason=reason)

    # <-- Start the bot -->
    with open(bot.cwd + "/bot_config/secrets.json", "r") as file:
        secret_file = json.load(file)

    bot.run(secret_file["token"])
