from typing import Protocol, Union


class Base(Protocol):
    """An implicit interface for a ticket's underlying database"""

    async def check_is_ticket(self, channel_id: Union[str, int]):
        pass

    async def check_message_is_reaction_message(self, message_id: Union[str, int]):
        pass

    async def get_next_ticket_id(self):
        pass

    async def create_ticket(
        self,
        channel_id: Union[str, int],
        ticket_id: int,
        reaction_message_id: Union[str, int],
    ):
        pass

    async def decrement_ticket_count(self):
        pass

    async def get_config(self):
        pass

    async def get_ticket_count(self):
        pass

    async def get_ticket_id(self, channel_id: Union[str, int]):
        pass

    async def get_ticket_setup_message_id(self):
        pass

    async def increment_ticket_count(self):
        pass

    async def remove_ticket(self, channel_id: Union[str, int]):
        pass

    async def save_new_ticket_message(self, message_id: int):
        pass
