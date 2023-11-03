import os
from typing import Collection, Optional

import discord
from database.database import CheeseDatabase
from lang import LangManager
from logger import LOGGER

BOT: Optional["CheeseBot"] = None


class CheeseBot(discord.Bot):
    def __init__(self, cogs: Collection[str]):
        intents = discord.Intents.default()
        super().__init__(
            description="The cheesiest Bot on the Planet!\n"
                        "Despite not having the ability to bypass earth's "
                        "boundaries, I'll try my best serving you a lot of "
                        "cheesecake.",
            intents=intents,
        )
        self.cogs_to_load = cogs

        self.lang = LangManager()

        LOGGER.info("Establishing database connection.")

        host = os.getenv("MYSQL_HOST")
        user = os.getenv("MYSQL_USERNAME")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")
        port = os.getenv("MYSQL_PORT")

        def malformed_dotenv(missing_key: str):
            raise RuntimeError(f"Malformed .env: Missing key '{missing_key}'")

        if host is None:
            malformed_dotenv("MYSQL_HOST")
        if user is None:
            malformed_dotenv("MYSQL_USERNAME")
        if password is None:
            malformed_dotenv("MYSQL_PASSWORD")
        if database is None:
            malformed_dotenv("MYSQL_DATABASE")

        self.db = CheeseDatabase(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port or "3306",
        )

    def setup(self):
        for cog in self.cogs_to_load:
            self.load_extension(f"cogs.{cog}")
