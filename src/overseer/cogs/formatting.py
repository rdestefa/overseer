# overseer.cogs.formatting

import hashlib
import logging
import random
import string
from typing import Literal

from utils.configs import load_config
from utils.parsers import parse_mentions

import discord
from discord.ext import commands

# Color and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Formatting(commands.Cog, name="formatting (`text` or `embed` mode)"):
    """
    Overseer commands for formatting and outputting text.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Set of vowels for b-ify.
        self.vowels = {"a", "e", "i", "o", "u"}

        # Leetspeak translations.
        self._A = ("4", "@")
        self._C = ("(", "<")
        self._E = ("3")
        self._L = ("1", "|")
        self._O = ("0", "()")
        self._S = ("5", "$", "z")
        self._T = ("7", "+")

        # Hashlib function mappings.
        self.hash_funcs = {
            "cksum": lambda arg: hashlib.md5(arg.encode()).hexdigest(),
            "md5": lambda arg: hashlib.md5(arg.encode()).hexdigest(),
            "sha1": lambda arg: hashlib.sha1(arg.encode()).hexdigest(),
            "sha224": lambda arg: hashlib.sha224(arg.encode()).hexdigest(),
            "sha256": lambda arg: hashlib.sha256(arg.encode()).hexdigest(),
            "sha384": lambda arg: hashlib.sha384(arg.encode()).hexdigest(),
            "sha512": lambda arg: hashlib.sha512(arg.encode()).hexdigest(),
            "blake2b": lambda arg: hashlib.blake2b(arg.encode()).hexdigest(),
            "blake2s": lambda arg: hashlib.blake2s(arg.encode()).hexdigest(),
        }

    @commands.hybrid_command(
        name="bify",
        usage="bify <mode> <letter> <message>",
        brief="B-ify a message."
    )
    async def bify(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        letter: str,
        *,
        message
    ) -> None:
        """
        The Overseer will b-ify each word in your message.
        Choose a custom letter to `<letter>`-ify each word (defaults to :b:).

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        letter: str
            The letter to use for b-ification.
        message: str
            The message to b-ify.
        """
        final_message, letter_emoji = "", ":b:"

        # Workaround for optional args since Discord.py doesn't support flags.
        if len(letter) == 1 and letter.isalpha():
            letter_emoji = f":regional_indicator_{letter.lower()}:"
        else:
            message = f"{letter} {message}"

        for word in parse_mentions(message, self.bot, context.guild).split():
            if word[0] in self.vowels:
                final_message += f"{letter_emoji}{word} "
            else:
                final_message += f"{letter_emoji}{word[1:]} "

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=final_message)

    @commands.hybrid_command(
        name="calc",
        aliases=["eval"],
        usage="calc <mode> <expression>",
        brief="Do a simple calculation."
    )
    async def calc(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        expression
    ) -> None:
        try:
            await context.invoke(
                self.bot.get_command("say"), mode=mode, msg=eval(expression))
        except SyntaxError:
            await context.send(embed=discord.Embed(
                title="Invalid Syntax!",
                description="I can't read the expression you entered.",
                color=colors["red"]
            ))

    @commands.hybrid_command(
        name="cipher",
        usage="cipher <mode> <distance> <message>",
        brief="Caesar cipher."
    )
    async def cipher(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        distance: int,
        *,
        message
    ) -> None:
        """
        I will encode your message with a Caesar cipher.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        distance: int
            How many letters to shift each character by.
        message: str
            The message to encode.
        """
        # Initialize character mapping.
        source = string.ascii_lowercase
        mapping = source[(distance % 26):] + source[:(distance % 26)]

        # Add uppercase letters to mapping.
        source += source.upper()
        mapping += mapping.upper()

        # Apply cipher to message.
        message = message.translate(str.maketrans(source, mapping))

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="clap",
        usage="clap <mode> <message>",
        brief="Insert claps between each word."
    )
    async def clap(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        I will insert claps between each word in your message.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        message = " :clap: ".join(message.strip().split())

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="expand",
        usage="expand <mode> <message>",
        brief="Space out a message."
    )
    async def expand(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        I will add space between each character in your message.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        message = " ".join(list(message))

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="leetspeak",
        usage="leetspeak <mode> <message>",
        brief="Translate text into leetspeak."
    )
    async def leetspeak(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        I will translate your message into leetspeak.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        message = (message.lower().strip()
                   .replace("a", random.choice(self._A))
                   .replace("c", random.choice(self._C))
                   .replace("e", random.choice(self._E))
                   .replace("l", random.choice(self._L))
                   .replace("o", random.choice(self._O))
                   .replace("s", random.choice(self._S))
                   .replace("t", random.choice(self._T))
                   )

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="cksum",
        aliases=["md5", "sha1", "sha224", "sha256", "sha384",
                 "sha512", "blake2b", "blake2s"],
        usage="cksum <mode> <message>",
        brief="Compute checksum of a message."
    )
    async def cksum(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        Compute the checksum of a message using a selected hashing algorithm.
        Choose an algorithm by replacing `cksum` with one of the following:
        ```
        md5, sha1, sha224, sha256, sha384, sha512, blake2b, blake2s
        ```

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        parsed_message = parse_mentions(message, self.bot, context.guild)
        message = self.hash_funcs[context.invoked_with](parsed_message)

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="mock",
        usage="mock <mode> <message>",
        brief="Mocks a message."
    )
    async def mock(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        I will mock the message you sent.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        mocked_message = ""

        for index, character in enumerate(message.lower().strip()):
            if index % 2:
                character = character.upper()

            mocked_message += character

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=mocked_message)

    @commands.hybrid_command(
        name="reverse",
        aliases=["backwards"],
        usage="reverse <mode> <message>",
        brief="Send a backwards message."
    )
    async def _reverse(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        message
    ) -> None:
        """
        I will reverse the message you sent.

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        message = parse_mentions(message, self.bot, context.guild)[::-1]

        await context.invoke(
            self.bot.get_command("say"), mode=mode, msg=message)

    @commands.hybrid_command(
        name="say",
        aliases=["echo"],
        usage="say <mode> <message>",
        brief="Say what you're thinking."
    )
    async def say(
        self,
        context: commands.Context,
        mode: Literal['embed', 'text'],
        *,
        msg
    ) -> None:
        """
        I will say what you're thinking so you don't have to (you still have
        to type it, though).

        Parameters
        -----------
        mode: typing.Literal
            Whether to embed the response in a container or use plain text.
        message: str
            The message to modify.
        """
        if mode == "embed":
            await context.send(embed=discord.Embed(
                description=msg,
                color=colors["green"]
            ))
        elif mode == "text":
            await context.send(msg)
        else:
            logger.warning("%s is not a supported mode", mode)
            await context.send(embed=discord.Embed(
                title="Invalid Mode!",
                description=(f"I don't currently support `{mode}`. You can " +
                             f"use either `text` or `embed` mode."),
                color=colors["red"]
            ))


async def setup(bot: commands.Bot):
    await bot.add_cog(Formatting(bot))
