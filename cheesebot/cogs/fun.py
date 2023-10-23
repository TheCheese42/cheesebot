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
    async def nitro(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="Claim your free nitro **now**!",
            description=f"Congratulations {ctx.author.mention}! You have the ultimate chance to claim your free nitro, sponsored by {ctx.bot.user.name}!",
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            )
            timestamp=utils.utcnow(),
        )
        view = views.xyz # TODO
        await ctx.reply(embed=embed, view=view)


def setup(bot: discord.Bot):
    LOGGER.info("[SETUP] fun")
    bot.add_cog(Fun(bot))


def teardown(bot: discord.Bot):
    LOGGER.info("[TEARDOWN] fun")
