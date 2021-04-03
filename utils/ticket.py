from typing import Union

from custom_context import MyContext
from utils.json_loader import read_json, write_json


class Ticket:
    def __init__(self, ctx: MyContext):
        self.ctx = ctx

    def is_ticket(self):
        return Ticket.check_is_ticket(self.ctx.message.channel.id)

    def save_new_ticket(self):
        pass

    @staticmethod
    def get_config():
        return read_json("config")

    @staticmethod
    def check_is_ticket(channel_id: Union[str, int]):
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
    def get_setup_message_id():
        data = Ticket.get_config()
        return data["ticket_setup_message_id"]

    @staticmethod
    def remove_ticket(channel_id: Union[str, int]):
        data = Ticket.get_config()
        data.pop(str(channel_id))
        write_json(data, "config")
