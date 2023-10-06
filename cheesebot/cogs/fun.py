import discord
from discord import utils
from logger import LOGGER


class Fun(discord.Cog):
    """
    Play Songs while typing the lyrics in a text channel!
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.emoji = "🎉"

    @discord.slash_command(
        name="nitro",
        description="Claim your free Discord Nitro! Sponsored by CheeseBot "
                    "for new and loyal users.",
    )
    @discord.


def setup(bot: discord.Bot):
    LOGGER.info("[SETUP] fun")
    bot.add_cog(Fun(bot))


def teardown(bot: discord.Bot):
    LOGGER.info("[TEARDOWN] fun")
