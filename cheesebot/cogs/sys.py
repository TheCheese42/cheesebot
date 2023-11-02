import builtins
import contextlib
import platform
import sys
import time

import cutils
import data
import discord
import psutil
import templates
import views
from bot import BOT, CheeseBot
from cutils import slash_command
from discord import utils
from discord.ext import commands, tasks
from logger import LOGGER


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


class Sys(discord.Cog):
    """sys_desc"""
    def __init__(self, bot: CheeseBot):
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
        await self.bot.change_presence(
            activity=discord.CustomActivity(text),
            status=status
        )
        self.bot.status = status

    @slash_command(
        name="reload",
        description="Hot-reload all or selected cogs.",
        help="reload_help",
    )
    @discord.option(
        name="module",
        description="The module to be reloaded.",
        type=str,
        choices=BOT.cogs_to_load,
        required=False,
    )
    @commands.is_owner()
    async def reload(self, ctx: discord.ApplicationContext, module: str):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        cogs_to_reload: str | list[str] = module or list(self.bot.cogs.keys())

        if isinstance(cogs_to_reload, str):
            cogs_to_reload = [cogs_to_reload]

        embed = templates.InfoEmbed(
            title=self.bot.lang.get("reload_embed_title", langcode),
            description=self.bot.lang.get(
                "reload_embed_description", langcode
            ).format(modules=', '.join(cogs_to_reload).lower()),
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        message = await ctx.respond(embed=embed)
        for cog in cogs_to_reload:
            try:
                self.bot.reload_extension(f"cogs.{cog.lower()}")
            except discord.ExtensionNotLoaded:
                embed = templates.FailureEmbed(
                    title=self.bot.lang.get(
                        "reload_error_embed_title", langcode
                    ),
                    description=self.bot.lang.get(
                        "reload_error_embed_description", langcode
                    ).format(module=cog.lower()),
                    timestamp=utils.utcnow(),
                    author=embed.author
                )
            else:
                embed = templates.SuccessEmbed(
                    title=self.bot.lang.get(
                        "reload_success_embed_title", langcode
                    ),
                    description=self.bot.lang.get(
                        "reload_success_embed_description", langcode
                    ).format(modules=', '.join(cogs_to_reload).lower()),
                    timestamp=utils.utcnow(),
                    author=embed.author,
                )
        await message.edit(embed=embed)

    @slash_command(
        name="shutdown",
        description="Shut the Bot down.",
        help="shutdown_help",
    )
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        embed = templates.InfoEmbed(
            title=self.bot.lang.get("shutdown_embed_title", langcode),
            description=self.bot.lang.get(
                "shutdown_embed_description", langcode
            ),
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        message = await ctx.respond(embed=embed)
        for cog in tuple(self.bot.cogs.keys()):
            self.bot.unload_extension(f"cogs.{cog.lower()}")
        embed = templates.SuccessEmbed(
            title=self.bot.lang.get("shutdown_success_embed_title", langcode),
            description=self.bot.lang.get(
                "shutdown_success_embed_description", langcode
            ),
            timestamp=utils.utcnow(),
            author=embed.author,
        )
        await message.edit(embed=embed)
        sys.exit(0)

    @discord.Cog.listener()
    async def on_application_command_error(  # type: ignore
        self,
        ctx: discord.ApplicationContext,
        error: discord.DiscordException,
    ):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        error_string = (
            f"{error.__class__.__name__}: {error}"
            if not hasattr(error, "original")
            else f"{error.original.__class__.__name__}: {error.original}"
        )

        async def send_error_embed():
            embed = templates.FailureEmbed(
                title=self.bot.lang.get("ge_embed_title", langcode),
                description=(
                    self.bot.lang.get("ge_embed_description", langcode).format(
                        command_name=ctx.command.qualified_name,
                        error=error_string
                    )
                )
            )
            await ctx.respond(
                embed=embed, view=views.LinkView(
                    url=data.get_data(
                        "global_strings", data.DataType.JSON
                    )["support_server_invite"],
                    text=self.bot.lang.get("ge_view_dcss", langcode),
                )
            )
            LOGGER.exception(error)
            raise error

        if isinstance(error, commands.NotOwner):
            await ctx.respond(
                self.bot.lang.get("error_notowner_message", langcode),
                ephemeral=True
            )
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            if isinstance(error.original, discord.Forbidden):
                pass
            else:
                await send_error_embed()
        else:
            await send_error_embed()

    @slash_command(
        name="system",
        description="Useful system information about the Bot's server.",
        help="system_help",
    )
    async def system(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        uname = platform.uname()
        system = uname.system
        release = uname.release
        version = uname.version
        processor = uname.processor
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)
        cpu_usage = psutil.cpu_percent(percpu=True, interval=1)
        svmem = psutil.virtual_memory()
        total_ram = get_size(svmem.total)
        used_ram = get_size(svmem.used)
        available_ram = get_size(svmem.available)
        used_ram_percent = svmem.percent
        embed = templates.InfoEmbed(
            title=self.bot.lang.get("system_embed_title", langcode),
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        cpu_usage_template = self.bot.lang.get(
            "system_cpu_usage_template", langcode
        )
        cpu_usage_str = "\n".join(
            [cpu_usage_template.format(
                count=i, percent=p
            ) for i, p in enumerate(cpu_usage, 1)]
        )
        embed.add_field(name=self.bot.lang.get(
            "system_field_system", langcode
        ), value=system)
        embed.add_field(name=self.bot.lang.get(
            "system_field_release", langcode
        ), value=release)
        embed.add_field(name=self.bot.lang.get(
            "system_field_version", langcode
        ), value=version)
        embed.add_field(name=self.bot.lang.get(
            "system_field_processor", langcode
        ), value=processor)
        embed.add_field(name=self.bot.lang.get(
            "system_field_physical_cores", langcode
        ), value=physical_cores)
        embed.add_field(name=self.bot.lang.get(
            "system_field_total_cores", langcode
        ), value=total_cores)
        embed.add_field(name=self.bot.lang.get(
            "system_field_cpu_usage", langcode
        ), value=f"{cpu_usage_str}")
        embed.add_field(name=self.bot.lang.get(
            "system_field_total_ram", langcode
        ), value=total_ram)
        embed.add_field(name=self.bot.lang.get(
            "system_field_available_ram", langcode
        ), value=available_ram)
        embed.add_field(name=self.bot.lang.get(
            "system_field_used_ram", langcode
        ), value=used_ram)
        embed.add_field(name=self.bot.lang.get(
            "system_field_used_ram_percentage", langcode
        ), value=f"{used_ram_percent}%")

        await ctx.respond(embed=embed)

    @slash_command(
        name="eval",
        description="Evaluate a Python expression",
        help="eval_help",
    )
    @discord.option(
        name="expression",
        description="A valid Python expression",
        type=str,
    )
    @discord.option(
        name="exec",
        description="If True, use exec instead of eval.",
        type=bool,
        required=False,
        default=False,
    )
    @commands.is_owner()
    async def eval_(
        self,
        ctx: discord.ApplicationContext,
        expression: str,
        exec: bool = False,
    ):
        langcode = self.bot.db.get_langcode(ctx.guild_id)
        oc = cutils.OutputCollector()
        error, return_value = None, None
        with contextlib.redirect_stdout(oc):
            try:
                before = time.time()
                if exec:
                    builtins.exec(expression)
                else:
                    return_value = eval(expression)
                after = time.time()
                ms = int(round(after - before, 3) * 1000)
            except Exception as e:
                error = f"{type(e).__name__}: {e}"
        stdout_content = "".join(oc.content)
        if error:
            embed_template = templates.FailureEmbed
        else:
            embed_template = templates.SuccessEmbed
        embed = embed_template(
            title=self.bot.lang.get("eval_embed_title", langcode),
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        embed.add_field(
            name=self.bot.lang.get(
                "eval_embed_field_input_expression", langcode
            ),
            value=cutils.le_1024(cutils.codeblockify(expression), end="```"),
            inline=False,
        )
        if return_value:
            embed.add_field(
                name=self.bot.lang.get(
                    "eval_embed_field_return_value", langcode
                ),
                value=cutils.le_1024(
                    cutils.codeblockify(return_value), end="```"
                ),
                inline=False,
            )
        if stdout_content:
            embed.add_field(
                name=self.bot.lang.get(
                    "eval_embed_field_stdout", langcode
                ),
                value=cutils.le_1024(
                    cutils.codeblockify(stdout_content), end="```"
                ),
                inline=False,
            )
        if error:
            embed.add_field(
                name=self.bot.lang.get(
                    "eval_embed_field_exception", langcode
                ),
                value=cutils.le_1024(
                    cutils.codeblockify(error), end="```"
                ),
                inline=False,
            )
        try:
            footer = self.bot.lang.get(
                "eval_embed_footer_complete", langcode
            ).format(ms=ms)
        except UnboundLocalError:
            footer = self.bot.lang.get("eval_embed_footer_failure", langcode)
        embed.set_footer(text=footer)
        await ctx.respond(embed=embed)

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


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] sys")
    bot.add_cog(Sys(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] sys")
