import asyncio
import logging
import sys
from pathlib import Path

from bot import CheeseBot
import bot
from logger import LOGGER


def load_token() -> str:
    with open(
        Path(__file__).parent.parent / ".token", "r", encoding="utf-8"
    ) as fp:
        return fp.read().strip()


async def main():
    # Setup logging
    LOGGER.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename='latest.log', encoding='utf-8', mode='w'
    )
    fmt_str = "[%(asctime)s] [%(levelname)s] %(message)s"
    datefmt_str = "%Y-%m-%d %H:%M:%S"
    handler.setFormatter(logging.Formatter(fmt_str, datefmt_str))
    LOGGER.addHandler(handler)
    if __debug__:
        debug_handler = logging.StreamHandler(sys.stdout)
        fmt_str = "[%(asctime)s] [%(levelname)s] %(message)s"
        datefmt_str = "%Y-%m-%d %H:%M:%S"
        debug_handler.setFormatter(logging.Formatter(fmt_str, datefmt_str))
        LOGGER.addHandler(debug_handler)

    # Construct the bot
    cogs = (
        "sys",
        "songs",
    )
    if len(sys.argv) >= 2:
        cogs = sys.argv[1].split(",")
        cogs = [i.strip() for i in cogs if i]

    cheese_bot = CheeseBot(cogs)
    bot.BOT = cheese_bot
    cheese_bot.setup()
    await cheese_bot.start(load_token())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("[SHUTDOWN] Shutting down after KeyboardInterrupt.")
        if bot.BOT is not None:
            for cog in tuple(bot.BOT.cogs.keys()):
                bot.BOT.unload_extension(f"cogs.{cog.lower()}")
        LOGGER.info("[SHUTDOWN] Successfully shut down.")
        sys.exit(0)
    except Exception:
        LOGGER.exception("Uncatched Exception occurred.")
        raise
