# overseer.utils.parsers

import re

from discord import Guild
from discord.ext.commands import Bot


def parse_mentions(message: str, bot: Bot, guild: Guild = None) -> str:
    new_message, start_index = '', 0

    for match in re.finditer(r"<[@#][!&]?\d*>", message):
        # Slice message at start and end indices of the match.
        end_index, new_start_index = match.span()
        new_message += message[start_index:end_index]

        # Extract user, role, or channel ID from match.
        id = match[0].replace("<", "").replace(">", "")

        if id[0] == "@":
            if id[1] == "!":  # Nickname
                obj_from_id = bot.get_user(int(id[2:]))
            elif id[1] == "&":  # Role
                obj_from_id = (guild.get_role(int(id[2:]))
                               if guild else None)
            else:  # Regular username
                obj_from_id = bot.get_user(int(id[1:]))
        elif id[0] == "#":  # Channel
            obj_from_id = bot.get_channel(int(id[1:]))
        else:
            continue

        # If ID couldn't be converted, don't replace matched string.
        if not obj_from_id:
            continue

        # Update message string and start index.
        new_message += obj_from_id.name
        start_index = new_start_index

    return new_message + message[start_index:]
