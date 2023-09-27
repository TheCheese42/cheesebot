from typing import Collection

import discord


class CheeseBot(discord.Bot):
    def __init__(self, cogs: Collection[str]):
        super().__init__(
            description="The most cheesy bot on the Planet!\n"
                        "Despite not having the ability to bypass earth's "
                        "boundaries, I'll try my best serving you a lot of "
                        "cheesecake.",
            intents=discord.Intents.default(),
        )
        self.cogs_to_load = cogs

    def setup(self):
        for cog in self.cogs_to_load:
            self.load_extension(cog)
