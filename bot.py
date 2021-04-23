import json
from pathlib import Path

import discord
from discord.ext import commands

from utils import MyContext, JsonStore, Ticket


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="-",
            case_insensitive=True,
            intents=discord.Intents.all(),
            activity=discord.Game(name=".new for a ticket"),
        )

        self.cwd = str(Path(__file__).parents[0])

        # The category to make tickets in
        self.category_id = 835056105872818176
        # The channel to send logs to
        self.log_channel_id = 835056152156176394
        # Where to setup the on_reaction -> create new ticket
        self.new_ticket_channel_id = 835056189795467274
        # The staff role to add to tickets
        self.staff_role_id = 503037272313036802
        # The data storage medium to use (MUST implement utils.db.base.Base)
        self.ticket_db = JsonStore(storage_path="/bot_config/")

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f"{self.user.display_name} is up and ready to go!")

    async def on_raw_reaction_add(self, payload):
        if not await Ticket.validate_reaction_event(self, payload, ["🔒", "✅"]):
            return

        reaction = str(payload.emoji)
        if (
            payload.message_id == await self.ticket_db.get_ticket_setup_message_id()
            and reaction == "✅"
        ):
            await Ticket.reaction_create_ticket(self, payload)

        elif reaction == "🔒":
            # Simply add a tick to the message
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.add_reaction("✅")

        elif reaction == "✅":
            # Time to delete the ticket!
            await Ticket.reaction_close_ticket(self, payload)

    async def on_raw_reaction_remove(self, payload):
        if not await Ticket.validate_reaction_event(self, payload, ["🔒"]):
            return

        reaction = str(payload.emoji)
        if reaction == "🔒":
            # Simply remove a tick from the message
            guild = bot.get_guild(payload.guild_id)
            member = await guild.fetch_member(bot.user.id)

            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction("✅", member)


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
