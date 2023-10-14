import time

import discord
import templates
import views
from discord import utils
from logger import LOGGER


class Utils(discord.Cog):
    """
    Module for system tasks that won't be seen by the end user and
    administrators.
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.emoji = "🛠"

    @discord.slash_command(
        name="ping",
        description="Test the Bot Latency.",
    )
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        start_time = time.time()
        message = await ctx.respond("Testing Ping...")
        end_time = time.time()
        bot_latency = round(self.bot.latency * 1000)
        api_latency = round((end_time - start_time) * 1000)
        if bot_latency + api_latency >= 660:
            color = 0xFF6200
        elif bot_latency + api_latency >= 800:
            color = 0xDE0000
        else:
            color = 0x09FF00
        embed = discord.Embed(
            title="Pong!", color=color, timestamp=utils.utcnow()
        )
        embed.add_field(name="Bot Latency", value=f"{bot_latency}ms")
        embed.add_field(
            name="API/Message Latency",
            value=f"{api_latency}ms",
        )
        if color == 0xFF6200 or color == 0xDE0000:
            embed.add_field(
                name="High Values",
                value="If the Bot latency is high the Bot is probably "
                      "overloaded.\nIf the API Latency is high, Discord most "
                      "likely got some problems.\nIf you don't feel that the "
                      "Bot is slow don't worry about high numbers, 1000ms is "
                      "also just a second.",
                inline=False,
            )

        embed.set_footer(text=f"Pong requested by {ctx.author.name}")
        await message.edit(content=None, embed=embed)

    @discord.slash_command(
        name="about",
        description="About the Bot.",
    )
    async def about(self, ctx: discord.ApplicationContext):
        app_info = await self.bot.application_info()
        embed = templates.InfoEmbed(
            title=f"About {self.bot.user.name}",  # type: ignore
            description=app_info.summary,
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
            thumbnail=ctx.author.avatar.url if ctx.author.avatar else None,
        )
        embed.description += (
            "\n\nThats right, my main mission is to serve you with as much "
            "cheesecake as I can. Check out my amazing /help command to find "
            "out what I can do for you!"
        )
        embed.add_field(
            name="Creator",
            value=f"I have been developed by {app_info.owner}.",
            inline=False,
        )
        embed.add_field(
            name="Open Source",
            value="I was made using Pycord, a Discord API Wrapper for Python. "
                  "My code is publicly available on GitHub. Feel free to "
                  "review and contribute! 🙂",
                  inline=False,
        )
        embed.add_field(
            name="Clip Art",
            value="Some clip art you find in this Bot is provided by "
                  "[clipground.com](https://clipground.com). This includes my "
                  "profile picture!"
        )
        await ctx.respond(
            embed=embed,
            view=views.MultiLinkView(
                urls=[
                    "https://example.com",
                    "https://github.com/NotYou404/cheesebot",
                ],
                texts=["Discord Support Server", "GitHub Repo"],
            )
        )


def setup(bot: discord.Bot):
    LOGGER.info("[SETUP] utils")
    bot.add_cog(Utils(bot))


def teardown(bot: discord.Bot):
    LOGGER.info("[TEARDOWN] utils")
