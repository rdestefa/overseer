# overseer.cogs

import glob
import logging
import logging.config
import os
import sys

from discord.ext.commands import Bot


logger = logging.getLogger()


def load_cogs(bot: Bot, cogs_dir: str = None) -> None:
    cogs_dir = cogs_dir or os.path.dirname(__file__)
    cogs_root = os.path.dirname(cogs_dir)

    # Ensures cogs_root is in the Overseer's import path.
    if cogs_root not in sys.path:
        sys.path.insert(0, cogs_root)

    for cog_path in glob.glob(f"{cogs_dir}/*.py"):
        # Don't want full path, just relative path.
        extension = cog_path.replace(
            cogs_root + "/", "").replace(
            cogs_root + "\\", "")
        extension = extension[:-3].replace(
            "/", ".").replace(
            "\\", ".")
        cog_name = extension[extension.rfind(".") + 1:]

        # Don't import private files.
        if extension.endswith("__") or extension.startswith("__"):
            continue

        # Load the cog into the Overseer.
        load_cog(bot, extension, cog_name)


def load_cog(bot: Bot, extension: str, cog_name: str) -> None:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        logger.error(
            "Failed to load extention %s: %s",
            cog_name,
            exception
        )
    else:
        logger.debug("Loaded extension %s", cog_name)
