from discord.ext import commands

from .ticket import Ticket


class MyContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ticket = Ticket(self, self.bot.ticket_db)
