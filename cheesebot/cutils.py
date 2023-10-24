from pathlib import Path
from typing import Generator, Optional, Callable

import discord
import templates
import views
from discord import utils


def slash_command(
    name: Optional[str] = None,
    description: Optional[str] = None,
    help: Optional[str] = None,
    **kwargs,
):
    if name:
        kwargs["name"] = name
    if description:
        kwargs["description"] = description
    if help:
        kwargs["help"] = help
    return application_command(
        cls=discord.SlashCommand,
        **kwargs,
    )


def application_command(cls=discord.SlashCommand, **attrs):
    def decorator(func: Callable) -> cls:
        if isinstance(func, discord.ApplicationCommand):
            func = func.callback
        elif not callable(func):
            raise TypeError(
                "func needs to be a callable or a subclass of "
                "ApplicationCommand."
            )
        if "help" in attrs:
            help = attrs["help"]
            del attrs["help"]
        else:
            help = None
        cmd = cls(func, **attrs)
        cmd.help = help
        return cmd

    return decorator


def group_slash_command(
    group: discord.SlashCommandGroup,
    name: str = None,
    description: str = None,
    help: str = None,
    **kwargs,
):
    if name:
        kwargs["name"] = name
    if description:
        kwargs["description"] = description

    def decorator(func: Callable) -> discord.SlashCommand:
        command = discord.SlashCommand(func, parent=group, **kwargs)
        command.help = help
        group.add_command(command)
        return command

    return decorator


def expand_audio_path(title: str | Path) -> Path:
    return Path(__file__).parent.parent / "audio" / title


def get_source(title: str) -> discord.FFmpegPCMAudio:
    """
    Get an audio source as discord.FFmpegPCMAudio object.

    :param title: File path to the audio source.
    :type title: str
    :returns: The audio source object.
    :rtype: discord.FFmpegPCMAudio
    """
    return discord.FFmpegPCMAudio(str(expand_audio_path(title)))


async def send_voice_playback_error(
    ctx: discord.ApplicationContext,
    error: discord.DiscordException,
) -> None:
    embed = templates.FailureEmbed(
        title="Error during voice playback...",
        description=f"```{type(error)}: {error}```\nIf this errors happens "
                    "frequently, please reach out to us at our official "
                    "support server.",
        timestamp=utils.utcnow(),
    )
    await ctx.send(
        embed=embed, view=views.LinkView(
            "https://example.com", "Discord Support Server"
        )
    )


def codeblockify(code: str, lang: Optional[str] = None) -> str:
    """
    Turn a code string into a markdown codeblock.

    :param code: The code string.
    :type code: str
    :param lang: The lang used for syntax highlighting. If None, no syntax
    highlighting will be available, defaults to None
    :type lang: str, optional
    :return: The code string as code block.
    :rtype: str
    """
    return f"```{lang or ''}\n{code}\n```"


def le_1024(text: str, replace: Optional[str] = None) -> str:
    if replace is None:
        replace = "*Too long to display*"
    return text if len(text) <= 1024 else replace


class OutputCollector:
    def __init__(self) -> None:
        self.content: list[str] = []

    def write(self, text: str) -> None:
        self.content.append(str(text))

    def flush(self) -> None:
        return

    def __iter__(self) -> Generator:
        yield from self.content
