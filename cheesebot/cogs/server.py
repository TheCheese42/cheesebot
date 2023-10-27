import discord
from bot import CheeseBot
from logger import LOGGER
from cutils import group_slash_command
from lang import get_available_langcodes, DEFAULT_LANGUAGE


class Server(discord.Cog):
    """server_desc"""
    def __init__(self, bot: CheeseBot):
        self.bot = bot
        self.emoji = "💻"

    language_group = discord.SlashCommandGroup(
        name="language",
        description="Manage the bot's language used for this server.",
        guild_only=True,
    )
    language_group.help = "language_group_help"

    @group_slash_command(
        group=language_group,
        name="set",
        description="Set the bot's language used for this server.",
        help="language_set_help",
    )
    @discord.option(
        name="language",
        type=str,
        choices=get_available_langcodes(),
    )
    @discord.default_permissions(manage_guild=True)
    async def language_set(
        self,
        ctx: discord.ApplicationContext,
        language: str,
    ):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        if language not in get_available_langcodes():
            await ctx.respond(self.bot.lang.get(
                "language_set_not_available", langcode
            ).format(language=language))
            return

        self.bot.db.update_or_create(
            table="server_config",
            id=ctx.guild_id,
            field="lang_code",
            value=language,
        )
        # Send confirm in new language
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        await ctx.respond(self.bot.lang.get(
            "language_set_success", langcode
        ).format(language=language))

    @group_slash_command(
        group=language_group,
        name="get",
        description="Get the currently active language.",
        help="language_get_help",
    )
    async def language_get(self, ctx: discord.ApplicationContext):
        lang_code = self.bot.db.get_langcode(ctx.guild_id)
        await ctx.respond(
            self.bot.lang.get("language_get_message", lang_code).format(
                lang_code=(lang_code or DEFAULT_LANGUAGE)
            )
        )

    @group_slash_command(
        group=language_group,
        name="reset",
        description="Reset the current language to default "
                    f"(`{DEFAULT_LANGUAGE}`).",
        help="language_reset_help",
    )
    @discord.default_permissions(manage_guild=True)
    async def language_reset(self, ctx: discord.ApplicationContext):
        self.bot.db.update_or_create(
            table="server_config",
            id=ctx.guild_id,
            field="lang_code",
            value=DEFAULT_LANGUAGE,
        )
        # Send confirm in new language
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        await ctx.respond(self.bot.lang.get(
            "language_reset_message", langcode
        ).format(language=DEFAULT_LANGUAGE))


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] server")
    bot.add_cog(Server(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] server")
