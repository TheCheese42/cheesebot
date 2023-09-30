import sys

import data
import discord
import templates
import views
from bot import BOT
from discord import utils
from discord.ext import commands, tasks
from logger import LOGGER
import platform
import time
import psutil


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
        await self.bot.change_presence(
            activity=discord.CustomActivity(text),
            status=status
        )
        self.bot.status = status

    @discord.slash_command(
        name="reload",
        description="Hot-reload all or selected cogs.",
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
        cogs_to_reload: str | list[str] = module or list(self.bot.cogs.keys())

        if isinstance(cogs_to_reload, str):
            cogs_to_reload = [cogs_to_reload]

        embed = templates.InfoEmbed(
            title="Reloading...",
            description="Reloading modules: "
                        f"{', '.join(cogs_to_reload).lower()}",
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
                    title="Error Reloading!",
                    description=f"The requested module `{cog.lower()}` does "
                                "not exist.",
                    timestamp=utils.utcnow(),
                    author=embed.author
                )
            else:
                embed = templates.SuccessEmbed(
                    title="Reloaded!",
                    description="Reloaded modules: "
                                f"{', '.join(cogs_to_reload).lower()}",
                    timestamp=utils.utcnow(),
                    author=embed.author,
                )
        await message.edit(embed=embed)

    @discord.slash_command(
        name="shutdown",
        description="Shut the Bot down.",
    )
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext):
        embed = templates.InfoEmbed(
            title="Shutting down...",
            description="Unloading modules...",
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
            title="Shut down",
            description=f"{self.bot.user.name} has been shut down "  # type: ignore  # noqa
                        "successfully.",
            timestamp=utils.utcnow(),
            author=embed.author,
        )
        await message.edit(embed=embed)
        sys.exit(0)

    @BOT.event
    async def on_application_command_error(  # type: ignore
        ctx: discord.ApplicationContext,
        error: discord.DiscordException,
    ):
        if isinstance(error, commands.NotOwner):
            await ctx.respond(
                "Only my dear creator can do that.", ephemeral=True
            )
        else:
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

    @discord.slash_command(
        name="ping",
        description="Test the Bot Latency.",
    )
    async def ping(self, ctx: discord.ApplicationContext):
        start_time = time.time()
        message = await ctx.respond("Testing Ping...")
        end_time = time.time()
        bot_latency = round(self.bot.latency * 1000)
        api_latency = round((end_time - start_time) * 1000)
        if bot_latency + api_latency >= 660:
            color = 0x09FF00
        elif bot_latency + api_latency >= 800:
            color = 0xFF6200
        else:
            color = 0xDE0000
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
        name="system",
        description="Useful system information about the Bot's server."
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
