# overseer.utils.custom_exceptions

import discord
from discord.ext import commands


class MemberBlacklisted(commands.CheckFailure):
    """
    Custom exception to be thrown when a blacklisted user tries to issue
    a command to the Overseer.
    """

    def __init__(
        self,
        member: discord.Member,
        message: str = "The Overseer ignores blacklisted users"
    ):
        self.member = member
        self.message = message

        super().__init__(self.message)

    def __str__(self):
        return f"{self.member.name} is blacklisted. {self.message}"
