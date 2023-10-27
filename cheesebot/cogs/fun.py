import discord
import templates
from bot import CheeseBot
from cutils import slash_command
from database.database import CheeseDatabase
from discord import utils
from logger import LOGGER


class Fun(discord.Cog):
    """fun_desc"""
    def __init__(self, bot: CheeseBot):
        self.bot = bot
        self.emoji = "🎉"

    @slash_command(
        name="nitro",
        description="Claim your free Discord Nitro! Sponsored by CheeseBot "
                    "for new and loyal users.",
        help="nitro_help"
    )
    async def nitro(self, ctx: discord.ApplicationContext):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        nitro = "<a:nitro:1166782246175379476>"
        embed = templates.SuccessEmbed(
            title=self.bot.lang.get("nitro_embed_title", langcode),
            description=(
                self.bot.lang.get("nitro_embed_description", langcode)
            ),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
            timestamp=utils.utcnow(),
        )

        class NitroView(discord.ui.View):
            def __init__(self, db: CheeseDatabase, bot: CheeseBot):
                super().__init__(disable_on_timeout=True)
                self.db = db
                self.bot = bot

            @discord.ui.button(
                label=self.bot.lang.get("nitro_view_button_claim", langcode),
                style=discord.ButtonStyle.success,
                emoji=nitro,
            )
            async def callback(
                self,
                button: discord.ui.Button,
                interaction: discord.Interaction,
            ):
                if interaction.user != ctx.interaction.user:
                    await interaction.response.send_message(
                        self.bot.lang.get("nitro_view_wrong_user", langcode),
                        ephemeral=True,
                    )
                    return

                self.stop()
                button.disabled = True
                await interaction.response.send_message(
                    content="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjE"
                            "xYmxmaGs4Y2F2N2ltNjF6OWt2MTRvd254NG1wajI1cDA1cGl"
                            "vNDAwNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/"
                            "N3tRG2Vg9y3TwUWKu7/giphy.gif",
                    ephemeral=True,
                )
                # HAHAHAHAHHAHAHAHAAHA I GOTCHU
                self.db.update_or_create(
                    table="userdata_global",
                    id=interaction.user.id,
                    field="rickrolled",
                    value=1,
                )

        await ctx.respond(embed=embed, view=NitroView(self.bot.db, self.bot))


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] fun")
    bot.add_cog(Fun(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] fun")
