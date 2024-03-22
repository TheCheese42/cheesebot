import discord
from bot import CheeseBot
from cutils import slash_command
from logger import LOGGER
from typing import Optional
import templates
from discord import utils

CommandsHierarchieType = dict[
    str, tuple[
        discord.Cog,
        dict[
            str, discord.SlashCommand | discord.SlashCommandGroup
        ]
    ]
]


class Help(discord.Cog):
    """help_desc"""
    def __init__(self, bot: CheeseBot):
        self.bot = bot
        self.emoji = "⁉"
        self.hidden = True

    def get_all_help_items(self) -> list[str]:
        return self.s

    def get_modules(self) -> dict[str, discord.Cog]:
        return self.bot.cogs

    def get_commands(self) -> dict[str, discord.SlashCommand]:
        dict = {}
        for command in self.bot.application_commands:
            if not isinstance(command, discord.SlashCommand):
                continue
            dict[command.qualified_name] = command
        return dict

    def get_groups(self) -> dict[str, discord.SlashCommandGroup]:
        dict = {}
        for command in self.bot.walk_commands():
            if isinstance(command, discord.SlashCommandGroup):
                dict[command.qualified_name] = command
        return dict

    def get_commands_hierarchie(self) -> CommandsHierarchieType:
        dict = {}
        for name, module in self.get_modules().items():
            sub_dict = {}
            for command in module.walk_commands():
                sub_dict[command.qualified_name] = command
            dict[name] = (module, sub_dict)
        return dict

    def get_command_depth_level(self, command: discord.SlashCommand) -> int:
        depth = 0
        while True:
            if not command.parent:
                break
            depth += 1
            command = command.parent
        return depth

    def build_hierarchie_embed(
        self,
        langcode: Optional[str] = None,
        module: Optional[str] = None,
        page: int = 1,
        page_len: int = 10,
    ):
        if langcode is None:
            langcode = self.bot.db.get_langcode()

        embed = templates.InfoEmbed(
            timestamp=utils.utcnow(),
        )

        hierarchie = self.get_commands_hierarchie()

        if not module:
            # all help
            embed.title = self.bot.lang.get("help_embed_title_all", langcode)
            for name, (module, _) in hierarchie:
                if hasattr(module, "hidden") and module.hidden:
                    continue
                embed.add_field(
                    name=f"{module.emoji} {name.capitalize()}",
                    value=module.__doc__ or self.bot.lang.get(
                        "help_no_desc_provided", langcode
                    ),
                    inline=False,
                )

    @slash_command(
        name="help",
        description="You might need help little Discord user.",
        help="help_help",
    )
    @discord.option(
        name="item",
        description="A module or command to get help on.",
        type=str,
    )
    async def help(
        self,
        ctx: discord.ApplicationContext,
        item: str = None,
    ):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        if item not in self.get_all_help_items():
            await ctx.respond(self.bot.lang.get(
                "help_invalid_item", langcode
            ).format(item=item, help_command_mention=ctx.command.mention))

        if item in self.get_modules():
            pass

        else:  # item is a command
            pass


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] help")
    bot.add_cog(Help(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] help")
