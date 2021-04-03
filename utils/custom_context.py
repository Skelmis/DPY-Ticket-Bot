from discord.ext import commands


class MyContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
