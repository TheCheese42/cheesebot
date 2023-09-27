import data
import discord
from discord.ext import tasks
from logger import LOGGER


class Sys(discord.Cog):
    """
    Module for system tasks that won't be seen by the end user and
    administrators.
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.emoji = "🔌"
        self.hidden = True

        self.presences: list[dict[str, str]] = data.get_data(
            "presences", data.DataType.JSON
        )

        self.change_presence_task.start(self.presences_gen())

    @discord.Cog.listener(name="on_ready")
    async def on_ready(self):
        LOGGER.info(f"{self.bot.user.name} connected to Discord.")

    @tasks.loop(seconds=15)
    async def change_presence_task(self, presences):
        await self.bot.wait_until_ready()
        presence = next(presences)
        replaces = presence["replace"]
        formats = [
            await self.eval_presence_format_option(replace)
            for replace in replaces
        ]
        text = presence["text"].format(*formats)
        status = discord.Status(presence["status"])
        LOGGER.info(f"Changing presence to {text}")
        await self.bot.change_presence(
            activity=discord.CustomActivity(text),
            status=status
        )
        self.bot.status = status

    def presences_gen(self):
        while True:
            for presence in self.presences:
                yield presence

    async def eval_presence_format_option(self, option: str):
        if option == "guild_count":
            return len(self.bot.guilds)
        if option == "user_count":
            count = 0
            async for guild in self.bot.fetch_guilds(limit=10000):
                count += guild.member_count
            return count
        else:
            raise NotImplementedError(option)


def setup(bot: discord.Bot):
    LOGGER.info("[SETUP] sys")
    bot.add_cog(Sys(bot))


def teardown(bot: discord.Bot):
    LOGGER.info("[TEARDOWN] sys")
