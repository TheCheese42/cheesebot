from typing import Collection, Optional

import discord

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

    def setup(self):
        for cog in self.cogs_to_load:
            self.load_extension(f"cogs.{cog}")
