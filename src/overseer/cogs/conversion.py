# overseer.cogs.conversion

import asynctempfile
import logging
import os
import subprocess
import uuid

from helpers.config_helpers import load_bot_configs, load_colors

import discord
from discord.ext import commands

# Bot, color, and logger configs.
config = load_bot_configs()
colors = load_colors()
logger = logging.getLogger()

# TODO: Put conversions in YAML config file.


class Conversion(commands.Cog, name="conversion"):
    """
    Cog for converting files from one type to another, both automatically
    and on command.
    """

    def __init__(self, bot):
        self.bot = bot
        self.unsupported_embeds = {"mov", "avi", "flv"}
        # M4V and GIF need special options.
        self.valid_conversions = {
            ("mp4", "mov"),
            ("mp4", "avi"),
            ("mp4", "flv"),
            ("mp4", "m4v"),
            ("mov", "avi"),
            ("mov", 'flv'),
            ("mov", "m4v"),
            ("avi", "flv"),
            ("avi", "m4v"),
            ("flv", "m4v")
        }
        self.special_conversions = {
            "gif": {
                "to": ["-pix_fmt", "yuv420p"]
            }
        }

    # TODO: Restrucuture options to support FLV.
    async def convert_files(
        self,
        temp_dir: str,
        from_type: str,
        to_type: str,
        attachment: discord.Attachment,
        special_args: list[str] = []
    ) -> tuple[str, int]:
        # Create pseudo-random input and output file names.
        input = os.path.join(temp_dir, f"{uuid.uuid4()}.{from_type}")
        output = os.path.join(temp_dir, f"{uuid.uuid4()}.{to_type}")

        # Download file from Discord.
        await attachment.save(fp=input)

        """
        Breakdown of options passed into ffmpeg:

          -i <input_path>: Path to file being converted.
          -vcodec copy: Copy or add playback metadata to the file.
          -acodec copy: Copy or add audio metadata to the file.
          -y <output_path>: Path for output file (overwrite existing file).
        """
        args = (["ffmpeg", "-i", input, "-vcodec", "copy", "-acodec", "copy"]
                + special_args
                + ["-y", output])
        result = subprocess.call(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return output, result

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Discord (as of late 2021) doesn't support embedded mov, avi, or flv
        files. To save the user the hassle of downloading throw away files,
        convert them to a format with supported embedding and re-upload them.

        There exists a Python abstraction for using ffmpeg, linked below:

          - https://kkroening.github.io/ffmpeg-python/#

        This library is not very robust, however, and its async execution will
        deadlock if the `quiet` option (suppress output) is set to True. Due to
        these limitations, this cog calls ffmpeg directly through `subprocess`.
        """
        # Ignore all commands and messages from the Overseer or another bot.
        if (message.author == self.bot.user or message.author.bot or
                message.content.startswith(config["bot_prefix"])):
            return

        for attachment in message.attachments:
            # If any of the files aren't supported, convert them.
            if (attachment.filename.rpartition(".")[2].lower()
                    in self.unsupported_embeds):
                break
        else:
            # No point in converting files if they're all supported.
            return

        # Create then cleanup temp directory for ffmpeg input / output files.
        async with asynctempfile.TemporaryDirectory() as temp:
            converted_files, supported_files = [], []

            for attachment in message.attachments:
                filename, _, filetype = attachment.filename.rpartition(".")

                # Convert all unsupported files.
                if filetype.lower() in self.unsupported_embeds:
                    output, result = await self.convert_files(
                        temp,
                        filetype,
                        "mp4",
                        attachment
                    )

                    # Explicitly check for 0 in case `result` is `None`.
                    if result == 0:
                        converted_files.append(discord.File(
                            output,
                            filename=f"{filename}.mp4"
                        ))
                        logger.debug(
                            "Converted %s.%s sent by %s (ID: %s) to %s.mp4",
                            filename,
                            filetype,
                            message.author,
                            message.author.id,
                            filename
                        )
                    else:
                        logger.error(
                            "Failed to convert %s.%s sent by %s (ID: %s)",
                            filename,
                            filetype,
                            message.author,
                            message.author.id
                        )
                else:
                    supported_files.append(await attachment.to_file())

            unsupported = len(message.attachments) - len(supported_files)
            converted = len(converted_files)

            # Construct response for the user.
            description = (f"Hey **{message.author.name}**, [Discord]"
                           + "(https://discord.com/) currently doesn't "
                           + "support some of the files you uploaded. ")
            if converted == unsupported:
                description += "I went ahead and converted them for you."
                color = "green"
            elif 0 < converted < unsupported:
                description += ("I wasn't able to convert all of them, but I "
                                + f"managed to get **{converted}** out of "
                                + f"**{unsupported}**.")
                color = "yellow"
            else:
                description += ("Unfortunately, I wasn't able to convert them "
                                + "for you. I'll try harder next time though!")
                color = "red"

            embed = discord.Embed(
                title="File Conversion",
                description=description,
                color=colors[color]
            )
            if converted == unsupported:
                try:
                    await message.delete()
                except discord.Forbidden:
                    await message.channel.send(
                        embed=embed, files=converted_files)
                else:
                    await message.channel.send(
                        content=message.content,
                        embed=embed,
                        files=supported_files + converted_files
                    )
            else:
                await message.channel.send(embed=embed, files=converted_files)

            logger.info(
                "Converted and re-uploaded %s file%s sent by %s (ID: %s)",
                converted,
                "" if converted == 1 else "s",
                message.author,
                message.author.id
            )

    # TODO: Convert video to image.
    # TODO: Convert GIFs.
    @commands.command(
        name="convert",
        usage="convert <extension>",
        brief="Convert a file to a different type."
    )
    async def convert(self, context, extension: str):
        """
        The Overseer will convert a file you upload to a different type.
        """
        if not context.message.attachments:
            await context.send(embed=discord.Embed(
                title="No Files Attached!",
                description="You didn't attach a file to your command.",
                color=colors["red"]
            ))
            return

        filename, _, filetype = (context.message.attachments[0].filename
                                 .rpartition("."))

        if (filetype := filetype.lower()) == (extension := extension.lower()):
            await context.send(embed=discord.Embed(
                title="Same Extension!",
                description=("Why would I convert a file that's already a "
                             + "`{extension}`?"),
                color=colors["red"]
            ))
            return

        if ((filetype, extension) in self.valid_conversions or
                (extension, filetype) in self.valid_conversions):
            async with asynctempfile.TemporaryDirectory() as temp:
                output, result = await self.convert_files(
                    temp,
                    filetype,
                    extension,
                    context.message.attachments[0]
                )

                # Explicitly check for 0 in case `result` is `None`.
                if result == 0:
                    await context.send(
                        embed=discord.Embed(
                            title="File Converted",
                            description=f"Here's your `{extension}` file.",
                            color=colors["green"]
                        ),
                        file=discord.File(
                            output,
                            filename=f"{filename}.{extension}"
                        )
                    )
                    logger.info(
                        "Converted %s.%s sent by %s (ID: %s) to %s.%s",
                        filename,
                        filetype,
                        context.message.author,
                        context.message.author.id,
                        filename,
                        extension
                    )
                else:
                    await context.send(embed=discord.Embed(
                        title="Failed to Convert File!",
                        description=(f"Hmm, I can't seem to convert this file "
                                     + f"to a `{extension}`...maybe I'm not "
                                     + "cut out for this line of work :("),
                        color=colors["red"]
                    ))
                    logger.error(
                        "Failed to convert %s.%s sent by %s (ID: %s)",
                        filename,
                        filetype,
                        context.message.author,
                        context.message.author.id
                    )
        else:
            await context.send(embed=discord.Embed(
                title="Invalid Conversion!",
                description=f"I can't convert `{filetype}` to `{extension}`.",
                color=colors["red"]
            ))


def setup(bot):
    bot.add_cog(Conversion(bot))
