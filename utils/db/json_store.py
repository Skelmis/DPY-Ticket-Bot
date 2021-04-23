import json
from pathlib import Path
from typing import Union


# noinspection DuplicatedCode
class JsonStore:
    """A database class that implements the Base class interface"""

    __slots__ = ("cwd", "storage_path")

    def __init__(self, storage_path="/"):
        self.cwd = str(Path(__file__).parents[2])

        if not storage_path.startswith("/") and not storage_path.endswith("/"):
            raise RuntimeError(
                "Expected a valid storage path string (Start and end with /)"
            )
        self.storage_path = storage_path

    async def check_is_ticket(self, channel_id: Union[str, int]):
        return str(channel_id) in await self.get_config()

    async def check_message_is_reaction_message(self, message_id: Union[str, int]):
        data = await self.get_config()
        if data["ticket_setup_message_id"] == message_id:
            return True

        data.pop("ticket_count")
        data.pop("ticket_setup_message_id")

        for v in data.values():
            if message_id == v.get("reaction_message_id"):
                return True

        return False

    async def create_ticket(
        self,
        channel_id: Union[str, int],
        ticket_id: int,
        reaction_message_id: Union[str, int],
    ):
        data = await self.get_config()
        data[str(channel_id)] = {
            "id": ticket_id,
            "reaction_message_id": reaction_message_id,
        }
        self.__write(data, "config")

    async def decrement_ticket_count(self):
        data = await self.get_config()
        if "ticket_count" not in data:
            return

        data["ticket_count"] -= 1
        self.__write(data, "config")

    async def get_config(self):
        return self.__read("config")

    async def get_next_ticket_id(self):
        await self.increment_ticket_count()
        return await self.get_ticket_count()

    async def get_ticket_count(self):
        data = await self.get_config()
        return data.get("ticket_count", 0)

    async def get_ticket_id(self, channel_id: Union[str, int]):
        data = await self.get_config()
        if str(channel_id) not in data:
            return None

        return data[str(channel_id)].get("id")

    async def get_ticket_setup_message_id(self):
        data = await self.get_config()
        return data.get("ticket_setup_message_id")

    async def increment_ticket_count(self):
        data = await self.get_config()
        if "ticket_count" not in data:
            data["ticket_count"] = 0

        data["ticket_count"] += 1
        self.__write(data, "config")

    async def remove_ticket(self, channel_id: Union[str, int]):
        data = await self.get_config()
        data.pop(str(channel_id))
        self.__write(data, "config")

    async def save_new_ticket_message(self, message_id: int):
        data = await self.get_config()
        data["ticket_setup_message_id"] = message_id
        self.__write(data, "config")

    def __read(self, filename: str) -> dict:
        try:
            with open(self.cwd + self.storage_path + filename + ".json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        return data

    def __write(self, data: dict, filename: str) -> None:
        with open(self.cwd + self.storage_path + filename + ".json", "w") as file:
            json.dump(data, file, indent=4)
