import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import bot
from bot import CheeseBot
from dotenv import load_dotenv
from logger import LOGGER


def load_token() -> Optional[str]:
    return os.getenv("BOT_TOKEN")


async def main() -> None:
    # Load .env
    try:
        load_dotenv(Path(__file__).parent.parent / ".env")
    except FileNotFoundError:
        raise FileNotFoundError(
            "Can't find .env file. Information on adding this can be found in "
            "the README of the bot's GitHub repo."
        )

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
        "fun",
        "server",
        "songs",
        "sys",
        "utils",
    )
    if len(sys.argv) >= 2:
        cogs = sys.argv[1].split(",")  # type: ignore
        cogs = [i.strip() for i in cogs if i]  # type: ignore

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
        bot.BOT.db.close()
        sys.exit(0)
    except Exception:
        LOGGER.exception("Uncatched Exception occurred.")
        raise
    finally:
        bot.BOT.db.close()
