# overseer.cogs.formatting

import logging
import random

from helpers.config_helpers import load_config

import discord
from discord.ext import commands

# Color, and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Formatting(commands.Cog, name="formatting (`text` or `embed` mode)"):
    """
    Overseer commands for formatting and outputting text.
    """

    def __init__(self, bot):
        self.bot = bot

        # Set of vowels for b-ify.
        self.vowels = {'a', 'e', 'i', 'o', 'u'}

        # Leetspeak translations.
        self._A = ('4', '@')
        self._C = ('(', '<')
        self._E = ('3')
        self._L = ('1', '|')
        self._O = ('0', '()')
        self._S = ('5', '$', 'z')
        self._T = ('7', '+')

    @commands.command(
        name="bify",
        usage="bify <mode> <message>",
        brief="B-ify each word in a message."
    )
    async def bify(self, context, mode: str, *, args):
        """
        The Overseer will b-ify each word in your message.
        """
        message = ""

        for word in args.strip().split():
            if word[0] in self.vowels:
                message += f":b:{word} "
            else:
                message += f":b:{word[1:]} "

        await context.invoke(
            self.bot.get_command('say'), mode=mode, args=message)

    @commands.command(
        name="clap",
        usage="clap <mode> <message>",
        brief="Insert claps between each word."
    )
    async def clap(self, context, mode: str, *, args):
        """
        The Overseer will insert claps between each word in your message.
        """
        message = " :clap: ".join(args.strip().split())

        await context.invoke(
            self.bot.get_command('say'), mode=mode, args=message)

    @commands.command(
        name="expand",
        usage="expand <mode> <message>",
        brief="Space out a message."
    )
    async def expand(self, context, mode: str, *, args):
        """
        The Overseer will add space between each character in your message.
        """
        message = ' '.join(list(args))

        await context.invoke(
            self.bot.get_command('say'), mode=mode, args=message)

    @commands.command(
        name="leetspeak",
        usage="leetspeak <mode> <message>",
        brief="Translate text into leetspeak."
    )
    async def leetspeak(self, context, mode: str, *, args):
        """
        The Overseer will translate your message into leetspeak.
        """
        message = (args.lower().strip()
                   .replace('a', random.choice(self._A))
                   .replace('c', random.choice(self._C))
                   .replace('e', random.choice(self._E))
                   .replace('l', random.choice(self._L))
                   .replace('o', random.choice(self._O))
                   .replace('s', random.choice(self._S))
                   .replace('t', random.choice(self._T))
                   )

        await context.invoke(
            self.bot.get_command('say'), mode=mode, args=message)

    @commands.command(
        name="mock",
        usage="mock <mode> <message>",
        brief="Mocks a message."
    )
    async def mock(self, context, mode: str, *, args):
        """
        The Overseer will mock the phrase you sent.
        """
        args = args.lower().strip()
        message = ''

        for index, character in enumerate(args):
            if index % 2:
                character = character.upper()

            message += character

        await context.invoke(
            self.bot.get_command('say'), mode=mode, args=message)

    @commands.command(
        name="say",
        aliases=["echo"],
        usage="say <mode> <message>",
        brief="Say what you're thinking."
    )
    async def say(self, context, mode: str, *, args):
        """
        The Overseer will say what you're thinking so you don't have to.
        """
        if mode == "embed":
            await context.send(embed=discord.Embed(
                description=args,
                color=colors["green"]
            ))
        elif mode == "text":
            await context.send(args)
        else:
            logger.warning("%s is not a supported mode", mode)
            await context.send(embed=discord.Embed(
                title="Invalid Mode!",
                description=(f"I don't currently support `{mode}`. You can " +
                             f"use either `text` or `embed` mode."),
                color=colors["red"]
            ))


def setup(bot):
    bot.add_cog(Formatting(bot))
