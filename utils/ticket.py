import discord

from utils.json_loader import read_json, write_json


class Ticket:
    def __init__(self, message: discord.Message):
        pass

    @staticmethod
    def get_config():
        return read_json("config")

    @staticmethod
    def is_ticket(channel_id):
        return str(channel_id) in Ticket.get_config()

    @staticmethod
    def get_ticket_count():
        data = Ticket.get_config()
        return data["ticket_count"]

    @staticmethod
    def increment_ticket_count():
        data = Ticket.get_config()
        data["ticket_count"] += 1
        write_json(data, "config")

    @staticmethod
    def build(message: discord.Message):
        if not Ticket.is_ticket(message.channel.id):
            return None

        ticket = Ticket(message)
        return ticket
