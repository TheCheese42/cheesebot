import asyncio
from typing import Any

import cutils
import data
import discord
from bot import CheeseBot
from cutils import group_slash_command
from discord import utils
from lang import LangManager
from logger import LOGGER


async def send_lyrics(
    ctx: discord.ApplicationContext,
    text: str,
    time: float | int
) -> discord.Message:
    async with ctx.typing():
        await asyncio.sleep(time)
    message = await ctx.send(text)
    return message


async def join_user_voice_channel(
    ctx: discord.ApplicationContext,
    lang_manager: LangManager,
    lang_code: str,
) -> bool:
    """
    Check wether or not the Bot is able to join a voice channel.
    This depends on several conditions, i.e. the voice status of the user and
    wether or not the Bot is already playing somewhere. This automatically
    sends an informative message to the author, assuming something went wrong.

    :param ctx: The application context.
    :type ctx: discord.ApplicationContext
    :returns: If the Bot is ready.
    :rtype: bool
    """
    bot = ctx.bot
    user = ctx.author
    lang = lang_manager
    code = lang_code

    # Check DM
    if not ctx.guild:
        await ctx.respond(lang.get("juvc_server_only", code))
        return False

    # Check user state
    if not user.voice:  # type: ignore
        await ctx.respond(lang.get("juvc_user_not_in_voice_channel", code))
        return False
    elif user.voice.deaf or user.voice.self_deaf:  # type: ignore
        await ctx.respond(lang.get("juvc_user_deaf", code))
        return False

    # Check bot state
    voice = utils.get(bot.voice_clients, guild=ctx.guild)  # type: ignore
    if voice:
        if voice.is_playing():  # type: ignore
            await ctx.respond(lang.get(
                "juvc_already_playing", code
            ).format(voice_channel_mention=voice.channel.mention))  # type: ignore  # noqa
            return False

    # Connect if necessary
    if user.voice:  # type: ignore
        if voice and voice.channel == user.voice.channel:  # type: ignore
            await ctx.respond(lang.get(
                "juvc_already_in_channel", code
            ), delete_after=2)
            return True
        else:
            if voice:
                await voice.move_to(user.voice.channel)  # type: ignore
                return True
            else:
                voice = await user.voice.channel.connect(timeout=10)  # type: ignore  # noqa
                return True
    await ctx.respond(lang.get(
        "juvc_joined_channel", code
    ), delete_after=2)
    return False


class Songs(discord.Cog):
    """songs_desc"""
    def __init__(self, bot: CheeseBot):
        self.bot = bot
        self.emoji = "🎵"

    song_group = discord.SlashCommandGroup(
        name="song",
        description="Play a Song while the lyrics is being typed in a text "
                    "channel.",
        guild_only=True,
    )
    song_group.help = "song_group_help"

    @group_slash_command(
        group=song_group,
        name="stillalive",
        description="Stillalive from the Portal Game Series.",
        help="song_stillalive_help"
    )
    async def stillalive(self, ctx: discord.ApplicationContext):
        song = "stillalive"
        if not await join_user_voice_channel(ctx):
            return
        source = cutils.get_source(f"{song}.mp3")
        lyrics: list[tuple[str, int | float]] = data.get_data(
            "song_lyrics", data.DataType.JSON
        )[song]
        messages: list[Any] = []
        messages.append(await ctx.respond(
            "### StillAlive by Ellen McLain and Jonathan Coulton"
        ))
        for i, (text, time) in enumerate(lyrics):
            if i == 1:  # Start playing before second line
                ctx.voice_client.play(  # type: ignore
                    source,
                    after=lambda e: cutils.send_voice_playback_error(
                        ctx, e
                    ) if e else None,
                )
            messages.append(await send_lyrics(ctx, text, time))
        await asyncio.sleep(10)
        await ctx.channel.delete_messages(
            messages,
            reason=f"Cleanup after playing song '{song}'",
        )


def setup(bot: CheeseBot):
    LOGGER.info("[SETUP] songs")
    bot.add_cog(Songs(bot))


def teardown(bot: CheeseBot):
    LOGGER.info("[TEARDOWN] songs")
