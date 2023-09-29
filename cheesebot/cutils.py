from pathlib import Path

import discord
import templates
from discord import utils
import views


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
    return discord.FFmpegPCMAudio(
        str(expand_audio_path(title)),
        executable=str(Path(__file__).parent.parent / "lib" / "ffmpeg")
    )


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
