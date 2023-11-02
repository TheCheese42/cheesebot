import json
import time
from typing import Optional

import data
import discord
import templates
import views
from bot import CheeseBot
from cutils import group_slash_command, slash_command
from discord import utils
from logger import LOGGER


class Utils(discord.Cog):
    """utils_help"""
    def __init__(self, bot: CheeseBot):
        self.bot = bot
        self.emoji = "🛠"

    @slash_command(
        name="ping",
        description="Test the Bot Latency.",
        help="ping_help",
    )
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        start_time = time.time()
        message = await ctx.respond(
            self.bot.lang.get("ping_message", langcode)
        )
        end_time = time.time()
        bot_latency = round(self.bot.latency * 1000)
        api_latency = round((end_time - start_time) * 1000)
        if bot_latency + api_latency >= 800:
            color = 0xDE0000
        elif bot_latency + api_latency >= 660:
            color = 0xFF6200
        else:
            color = 0x09FF00
        embed = discord.Embed(
            title=self.bot.lang.get(
                "ping_pong", langcode
            ), color=color, timestamp=utils.utcnow()
        )
        embed.add_field(
            name=self.bot.lang.get("ping_field_bot_latency", langcode),
            value=self.bot.lang.get(
                "ping_latency_template", langcode
            ).format(ms=bot_latency),
        )
        embed.add_field(
            name=self.bot.lang.get("ping_field_api_latency", langcode),
            value=self.bot.lang.get(
                "ping_latency_template", langcode
            ).format(ms=api_latency),
        )
        if color == 0xFF6200 or color == 0xDE0000:
            embed.add_field(
                name=self.bot.lang.get("ping_field_high_values", langcode),
                value=self.bot.lang.get("ping_high_values", langcode),
                inline=False,
            )

        embed.set_footer(text=self.bot.lang.get(
            "ping_footer", langcode
        ).format(name=ctx.author.name))
        await message.edit(content=None, embed=embed)

    @slash_command(
        name="about",
        description="About the Bot.",
        help="about_help",
    )
    async def about(self, ctx: discord.ApplicationContext):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        app_info = await self.bot.application_info()
        embed = templates.InfoEmbed(
            title=self.bot.lang.get("about_embed_title", langcode),
            description=self.bot.lang.get("about_embed_desc", langcode),
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
            thumbnail=(
                ctx.bot.user.avatar.url if ctx.bot.user.avatar else None
            ),
        )
        embed.add_field(
            name=self.bot.lang.get("about_embed_field_creator", langcode),
            value=self.bot.lang.get("about_embed_creator", langcode),
            inline=False,
        )
        embed.add_field(
            name=self.bot.lang.get("about_embed_field_open_source", langcode),
            value=self.bot.lang.get("about_embed_open_source", langcode),
            inline=False,
        )
        embed.add_field(
            name=self.bot.lang.get("about_embed_field_clip_art", langcode),
            value=self.bot.lang.get("about_embed_clip_art", langcode)
        )
        await ctx.respond(
            embed=embed,
            view=views.MultiLinkView(
                urls=[
                    data.get_data(
                        "global_strings", data.DataType.JSON
                    )["support_server_invite"],
                    data.get_data(
                        "global_strings", data.DataType.JSON
                    )["github_repo"],
                ],
                texts=[
                    self.bot.lang.get("about_view_dcss", langcode),
                    self.bot.lang.get("about_view_github_repo", langcode),
                ],
            )
        )

    embed_group = discord.SlashCommandGroup(
        name="embed",
        description="Send and manage embeds",
    )
    embed_group.help = "Provides a set of commands to send and edit customizable embeds."

    @group_slash_command(
        group=embed_group,
        name="post",
        description="Post an embed",
        help="Send an embed specified using [discord's official JSON format](https://discord.com/developers/docs/resources/channel#embed-object). To generate those JSON strings a visualizer like [EmbedBuilder.com](https://embedbuilder.com) can be used.",
    )
    @discord.option(
        name="json_data",
        description="JSON representation of the embed. See `/help embed.post`",
        type=str,
    )
    @discord.option(
        name="channel",
        description="The channel to send the embed to",
        type=discord.TextChannel,
    )
    @discord.default_permissions(
        manage_messages=True,
    )
    async def post(
        self,
        ctx: discord.ApplicationContext,
        json_data: str,
        channel: Optional[discord.TextChannel] = None
    ):
        try:
            embed = discord.Embed.from_dict(json.loads(json_data))
        except Exception as e:
            await ctx.respond(
                "I'm sorry but your provided json was invalid. Please check "
                "you copied everything and actually exported as JSON.",
                view=views.TextResponseButtonView(
                    label="See error",
                    response_text=f"{e.__class__.__name__}: {e}",
                )
            )
            return
        if channel is None:
            channel = ctx.channel
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as e:
            if e.code == 50033:
                await ctx.respond(
                        "I am not allowed to send the embed. Check my "
                        "permissions!"
                    )
            elif e.code == 50035:
                await ctx.respond(
                        "Your JSON seems to be malformed.",
                        view=views.TextResponseButtonView(
                            label="Get error",
                            response_text=f"{e.__class__.__name__}: {e}"
                        )
                    )
        await ctx.respond(
            f"Embed sent to {channel.mention}!",
            delete_after=5,
        )


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] utils")
    bot.add_cog(Utils(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] utils")
