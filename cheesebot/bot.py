import os
from typing import Collection, Optional

import discord
from database.database import CheeseDatabase
from lang import LangManager

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

        self.db = CheeseDatabase(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=os.getenv("MYSQL_PORT")
        )

    def setup(self):
        for cog in self.cogs_to_load:
            self.load_extension(f"cogs.{cog}")
