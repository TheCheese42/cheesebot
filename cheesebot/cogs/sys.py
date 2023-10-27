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
        async def send_error_embed():
            embed = templates.FailureEmbed(
                title="Error running command...",
                description=(
                    "An unexpected error occurred when running command "
                    f"{ctx.command.qualified_name}: `{error}`\n"
                    "This has been logged and will be fixed soon. If you're "
                    "experiencing further issues please reach out to us at "
                    "CheeseBot's support Server. Thank you for understanding!"
                )
            )
            await ctx.respond(
                embed=embed, view=views.LinkView(
                    url="https://example.com",
                    text="Discord Support Server"
                )
            )
            LOGGER.exception(error)
            raise error

        if isinstance(error, commands.NotOwner):
            await ctx.respond(
                "Only my dear creator can do that.", ephemeral=True
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
        help="Fetch current system informations about the machine the bot is running on. This includes system version and release, processor information and usage and memory information and usage.",
    )
    async def system(self, ctx: discord.ApplicationContext):
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
            title="System Information",
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        cpu_usage_str = "\n".join(
            [f"CPU {i}: {p}%" for i, p in enumerate(cpu_usage, 1)]
        )
        embed.add_field(name="System", value=system)
        embed.add_field(name="Release", value=release)
        embed.add_field(name="Version", value=version)
        embed.add_field(name="Processor", value=processor)
        embed.add_field(name="Physical Cores", value=physical_cores)
        embed.add_field(name="Total Cores", value=total_cores)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage_str}")
        embed.add_field(name="Total RAM", value=total_ram)
        embed.add_field(name="Available RAM", value=available_ram)
        embed.add_field(name="Used RAM", value=used_ram)
        embed.add_field(
            name="Used RAM Percentage", value=f"{used_ram_percent}%"
        )
        await ctx.respond(embed=embed)

    @slash_command(
        name="eval",
        description="Evaluate a Python expression",
        help="Evaluate any valid Python expression using the command's "
             "lexical scope. This includes a `self: discord.Cog`, a "
             "`ctx: discord.ApplicationContext` and all imported modules. "
             "Any stdlib modules as well as anything specified in the bot's "
             "dependency tree can be installed can be imported as well.\n\nIf "
             "the `exec` parameter is `True` the expression will be evaluated "
             "using the `exec()` function instead of `eval()`. This allows "
             "multi-line evaluations and more complex constructs.",
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
            title="Eval result",
            timestamp=utils.utcnow(),
            author=discord.EmbedAuthor(
                name=ctx.author.name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            ),
        )
        embed.add_field(
            name="Input Expression",
            value=cutils.le_1024(cutils.codeblockify(expression)),
            inline=False,
        )
        if return_value:
            embed.add_field(
                name="Return value",
                value=cutils.le_1024(cutils.codeblockify(return_value)),
                inline=False,
            )
        if stdout_content:
            embed.add_field(
                name="Stdout",
                value=cutils.le_1024(cutils.codeblockify(stdout_content)),
                inline=False,
            )
        if error:
            embed.add_field(
                name="Exception",
                value=cutils.le_1024(cutils.codeblockify(error)),
                inline=False,
            )
        try:
            footer = f"Eval took {ms}ms"
        except UnboundLocalError:
            footer = "Eval did not complete"
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
