import os
from pathlib import Path
from typing import Union

import aiosqlite

from .base import Base


# noinspection SqlNoDataSourceInspection
class SqlLiteStore(Base):
    """
    Its on you to clear the database if you want

    Tables
    ------
    tickets:
    - channel_id: int
    - reaction_message_id: int
    - ticket_id: int

    config:
    - ticket_setup_message_id: int
    - ticket_count: int
    """

    def __init__(self, storage_path: str = None, database_name: str = None):
        storage_path = storage_path.strip("/")

        self.db_file = database_name or "storage.db"
        if not self.db_file.endswith(".db"):
            self.db_file = self.db_file + ".db"

        self.db_file = os.path.join(storage_path, self.db_file)

        self.cwd = str(Path(__file__).parents[2])

        self.db = os.path.join(self.cwd, self.db_file)

        self.is_initialized = False

    async def initialize(self):
        if self.is_initialized:
            return

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'"
            ) as cursor:
                if not await cursor.fetchone():
                    await db.execute(
                        "CREATE TABLE tickets (channel_id number, ticket_id number, reaction_message_id number)"
                    )
                    await db.commit()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='config'"
            ) as cursor:
                if not await cursor.fetchone():
                    await db.execute(
                        "CREATE TABLE config (ticket_setup_message_id number, ticket_count number)"
                    )
                    await db.execute("INSERT INTO config VALUES (0, 0)")
                    await db.commit()

        self.is_initialized = True

    async def check_is_ticket(self, channel_id: Union[str, int]):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT * FROM tickets WHERE channel_id=:channel_id",
                {"channel_id": channel_id},
            ) as cursor:
                if await cursor.fetchone():
                    return True
                return False

    async def check_message_is_reaction_message(self, message_id: Union[str, int]):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT * FROM config WHERE ticket_setup_message_id=:message_id",
                {"message_id": message_id},
            ) as cursor:
                if await cursor.fetchone():
                    return True

            async with db.execute(
                "SELECT * FROM tickets WHERE reaction_message_id=:message_id",
                {"message_id": message_id},
            ) as cursor:
                if await cursor.fetchone():
                    return True

            return False

    async def get_next_ticket_id(self):
        await self.initialize()

        await self.increment_ticket_count()
        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT ticket_count FROM config") as cursor:
                value = await cursor.fetchone()
                return value[0]

    async def create_ticket(
        self,
        channel_id: Union[str, int],
        ticket_id: int,
        reaction_message_id: Union[str, int],
    ):
        await self.initialize()

        channel_id = int(channel_id)
        reaction_message_id = int(reaction_message_id)

        async with aiosqlite.connect(self.db) as db:
            await db.execute(
                "INSERT INTO tickets VALUES (:channel_id, :ticket_id, :reaction_message_id)",
                {
                    "channel_id": channel_id,
                    "ticket_id": ticket_id,
                    "reaction_message_id": reaction_message_id,
                },
            )
            await db.commit()

    async def decrement_ticket_count(self):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            await db.execute("UPDATE config SET ticket_count = ticket_count - 1")
            await db.commit()

    async def get_config(self):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT * FROM config") as cursor:
                value = await cursor.fetchone()
                return value[0]

    async def get_ticket_count(self):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT ticket_count FROM config") as cursor:
                value = await cursor.fetchone()
                return value[0]

    async def get_ticket_id(self, channel_id: Union[str, int]):
        await self.initialize()

        channel_id = int(channel_id)

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT ticket_id FROM tickets WHERE channel_id=:channel_id",
                {"channel_id": channel_id},
            ) as cursor:
                value = await cursor.fetchone()
                return value[0]

    async def get_ticket_setup_message_id(self):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            async with db.execute(
                "SELECT ticket_setup_message_id FROM config",
            ) as cursor:
                value = await cursor.fetchone()
                return value[0]

    async def increment_ticket_count(self):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            await db.execute("UPDATE config SET ticket_count = ticket_count + 1")
            await db.commit()

    async def remove_ticket(self, channel_id: Union[str, int]):
        await self.initialize()

        channel_id = int(channel_id)

        async with aiosqlite.connect(self.db) as db:
            await db.execute(
                "DELETE FROM tickets WHERE channel_id=:channel_id",
                {"channel_id": channel_id},
            )
            await db.commit()

    async def save_new_ticket_message(self, message_id: int):
        await self.initialize()

        async with aiosqlite.connect(self.db) as db:
            await db.execute(
                "UPDATE config SET ticket_setup_message_id=:ticket_setup_message_id",
                {"ticket_setup_message_id": message_id},
            )
            await db.commit()
