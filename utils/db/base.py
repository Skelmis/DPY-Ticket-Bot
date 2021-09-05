from typing import Protocol, Union


class Base(Protocol):
    """An implicit interface for a ticket's underlying database"""

    async def check_is_ticket(self, channel_id: Union[str, int]):
        raise NotImplementedError

    async def check_message_is_reaction_message(self, message_id: Union[str, int]):
        raise NotImplementedError

    async def get_next_ticket_id(self):
        raise NotImplementedError

    async def create_ticket(
        self,
        channel_id: Union[str, int],
        ticket_id: int,
        reaction_message_id: Union[str, int],
    ):
        raise NotImplementedError

    async def decrement_ticket_count(self):
        raise NotImplementedError

    async def get_config(self):
        raise NotImplementedError

    async def get_ticket_count(self):
        raise NotImplementedError

    async def get_ticket_id(self, channel_id: Union[str, int]):
        raise NotImplementedError

    async def get_ticket_setup_message_id(self):
        raise NotImplementedError

    async def increment_ticket_count(self):
        raise NotImplementedError

    async def remove_ticket(self, channel_id: Union[str, int]):
        raise NotImplementedError

    async def save_new_ticket_message(self, message_id: int):
        raise NotImplementedError
