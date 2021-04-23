import discord

from utils.db import Base


class Ticket:
    """An added context attr designed with simplicity in mind.

    This class lazily evaluates itself and attaches itself
    to all command contexts. By doing this, we are able to
    very easily create/modify/delete/update any tickets.

    Note, we do add @staticmethods to allow for usage
    with events that don't have an attached context.
    """

    def __init__(self, ctx, db: Base):
        self.ctx = ctx
        self.db = db

    async def close_ticket(self, reason=None):
        ctx = self.ctx
        channel = self.ctx.channel
        if not await self.db.check_is_ticket(channel.id):
            return await ctx.send("I can only close channels that are actual tickets.")

        reason = reason or "No closing reason specified."
        ticket_id = await self.db.get_ticket_id(channel.id)
        messages = await channel.history(limit=None, oldest_first=True).flatten()
        ticket_content = " ".join(
            [
                f"{message.created_at.strftime('%d/%m/%Y')} {message.author.name:<15} | {message.content}\n"
                for message in messages
            ]
        )
        with open(f"tickets/{ticket_id}.txt", "w", encoding="utf8") as f:
            f.write(
                f"Here is the message log for ticket ID {ticket_id}\n----------\n\n"
            )
            f.write(ticket_content)

        file_object = discord.File(f"tickets/{ticket_id}.txt")
        await self.__send_log(
            f"Closed Ticked: Id {ticket_id}",
            f"Close Reason: {reason}",
            0xF42069,
            file=file_object,
        )
        await channel.delete()

    async def create_ticket(self, subject=None, *, sudo_author=None):
        guild = self.ctx.guild
        bot = self.ctx.bot
        ctx = self.ctx

        author = sudo_author or ctx.message.author

        new_ticket_id = await self.db.get_next_ticket_id()
        staff_role = guild.get_role(bot.staff_role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True),
            author: discord.PermissionOverwrite(read_messages=True),
        }

        channel = await guild.create_text_channel(
            name=f"Support Ticket #{new_ticket_id}",
            overwrites=overwrites,
            category=bot.get_channel(bot.category_id),
        )

        content = f"""
        ** Hello {author.display_name} **
        
        This is your ticket, how can we help you?

        `Our team will be with you shortly.`
        """
        embed = discord.Embed(description=content, color=0x808080)
        m = await channel.send(
            f"{author.mention} | <@&{bot.staff_role_id}>", embed=embed
        )
        await m.add_reaction("🔒")

        if subject:
            embed = discord.Embed(
                title="Provided subject for ticket:",
                description=subject,
                color=0x808080,
            )
            embed.set_author(name=author.name, icon_url=author.avatar_url)
            await channel.send(embed=embed)

        await self.db.create_ticket(channel.id, new_ticket_id, m.id)
        await self.__send_log(
            f"Created ticket with ID {new_ticket_id}",
            f"Ticket Creator: {author.mention}(`{author.id}`)\nChannel: "
            "{channel.mention}({channel.name})\nSubject: {subject}",
            0xB4DA55,
        )

    async def remove_user(self, user: discord.Member):
        channel = self.ctx.channel
        if not await self.db.check_is_ticket(channel.id):
            return await self.ctx.send(
                "This is not a ticket! Users can only be removed from a ticket channel."
            )

        await channel.set_permissions(user, read_messages=False, send_messages=False)

    async def add_user(self, user: discord.Member):
        channel = self.ctx.channel
        if not await self.db.check_is_ticket(channel.id):
            return await self.ctx.send(
                "This is not a ticket! Users can only be added to a ticket channel."
            )

        await channel.set_permissions(user, read_messages=True, send_messages=True)

    async def setup_new_ticket_message(self):
        bot = self.ctx.bot
        channel = bot.get_channel(bot.new_ticket_channel_id)

        embed = discord.Embed(
            title="Our Services",
            description="To purchase a service or enquire about one you must react with a tick",
            color=0xB4DA55,
        )
        m = await channel.send(embed=embed)
        await m.add_reaction("✅")

        await self.db.save_new_ticket_message(m.id)

    async def __send_log(
        self,
        title: str,
        description: str,
        color: hex = 0x808080,
        file: discord.File = None,
    ):
        bot = self.ctx.bot
        ctx = self.ctx

        log_channel = bot.get_channel(bot.log_channel_id)

        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await log_channel.send(embed=embed)

        if file:
            await log_channel.send(file=file)
