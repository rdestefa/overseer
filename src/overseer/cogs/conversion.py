# overseer.cogs.conversion

import asynctempfile
import logging
import os
import subprocess
import uuid

from helpers.config_helpers import load_config

import discord
from discord.ext import commands

# Color, and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Conversion(commands.Cog, name="conversion"):
    """
    Cog for converting files from one type to another, both automatically
    and on command.

    There exists a Python abstraction for using ffmpeg, linked below:

      - https://kkroening.github.io/ffmpeg-python/#

    This library is not very robust, however, and its async execution will
    deadlock if the `quiet` option (suppress output) is set to True. Due to
    these limitations, this cog calls ffmpeg directly through `subprocess`.
    """

    def __init__(self, bot):
        self.bot = bot
        self.configs = load_config("conversion", safe=False)
        # M4V and GIF need special options.
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
        args: list[list[str]] = [[], []]
    ) -> tuple[str, int]:
        """
        Helper function to convert files from one type to another.
        """
        # Create pseudo-random input and output file names.
        input = os.path.join(temp_dir, f"{uuid.uuid4()}.{from_type}")
        output = os.path.join(temp_dir, f"{uuid.uuid4()}.{to_type}")

        # Download file from Discord.
        await attachment.save(fp=input)

        """
        Summary of common options passed into ffmpeg:

          -i <input_path>: Path to file being converted.
          -<codec:v>|<-c:v> copy: Copy or add playback metadata to the file.
          -<codec:a>|<-c:a> copy: Copy or add audio metadata to the file.
          -frames:v <n>: Take only the first `n` frames of a video.
          -vf format=<format>: Pixel format for the image / video.
          -y <output_path>: Path for output file (overwrite existing file).
        """
        args = (["ffmpeg"]
                + args[0]
                + ["-i", input]
                + args[1]
                + ["-y", output])
        result = subprocess.call(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return output, result

    async def convert_to_gif(
        self,
        temp_dir: str,
        from_type: str,
        to_type: str,
        attachment: discord.Attachment
    ):
        """
        Proper conversion from video to GIF requires three separate ffmpeg
        subprocesses, so the conversion requires this special helper function.
        """
        # Create pseudo-random input and output file names.
        input = os.path.join(temp_dir, f"{uuid.uuid4()}.{from_type}")

        # Download file from Discord.
        await attachment.save(fp=input)

        # Extract the frame rate of the input video.
        ffmpeg_output = subprocess.check_output([
            "ffprobe", input,
            "-v", "0",                                # First video.
            "-of", "csv=p=0",                         # Truncate all noise.
            "-select-streams", "v",                   # Video input.
            "-show_entries", "stream=avg_frame_rate"  # Avg framerate as frac.
        ])
        top, bottom = ffmpeg_output.decode("utf-8").strip().split("/")
        framerate = round(int(top) / int(bottom), 2)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Discord (as of late 2021) doesn't support embedded mov, avi, or flv
        files. To save the user the hassle of downloading throw away files,
        convert them to a format with supported embedding and re-upload them.
        """
        # Ignore all commands and messages from the Overseer or another bot.
        if (message.author == self.bot.user or message.author.bot or
                message.content.startswith(self.bot.command_prefix)):
            return

        for attachment in message.attachments:
            # If any of the files aren't supported, convert them.
            filetype = attachment.filename.rpartition(".")[2]
            filetype = self.configs["aliases"].get(
                filetype.lower(), filetype.lower())

            if (filetype in self.configs["unsupported_embeds"]):
                break
        else:
            # No point in converting files if they're all supported.
            return

        # Create then cleanup temp directory for ffmpeg input / output files.
        async with asynctempfile.TemporaryDirectory() as temp:
            converted_files, supported_files = [], []

            for attachment in message.attachments:
                filename, _, filetype = attachment.filename.rpartition(".")
                filetype = self.configs["aliases"].get(
                    filetype.lower(), filetype.lower())

                # Convert all unsupported files.
                if (filetype in self.configs["unsupported_embeds"]):
                    output, result = await self.convert_files(
                        temp,
                        filetype,
                        "mp4",
                        attachment,
                        self.configs["valid_conversions"][(filetype, "mp4")]
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
        usage="convert <to_type>",
        brief="Convert a file to a different type."
    )
    async def convert(self, context, to_type: str):
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

        filename, _, from_type = (context.message.attachments[0].filename
                                  .rpartition("."))

        # Convert any aliased file types.
        to_type = self.configs["aliases"].get(to_type.lower(), to_type.lower())
        from_type = self.configs["aliases"].get(
            from_type.lower(), from_type.lower())

        # Don't convert the same file types.
        if from_type == to_type:
            await context.send(embed=discord.Embed(
                title="Same Extension!",
                description=("Why would I convert a file that's already a "
                             + f"`{to_type}`?"),
                color=colors["red"]
            ))
            return

        if ((from_type, to_type) in self.configs["valid_conversions"] or
                (to_type, from_type) in self.configs["valid_conversions"]):
            async with asynctempfile.TemporaryDirectory() as temp:
                output, result = await self.convert_files(
                    temp,
                    from_type,
                    to_type,
                    context.message.attachments[0],
                    self.configs["valid_conversions"][(from_type, to_type)]
                )

                # Explicitly check for 0 in case `result` is `None`.
                if result == 0:
                    await context.send(
                        embed=discord.Embed(
                            title="File Converted",
                            description=(f"Here's your `{to_type}` file. " +
                                         "Tips are appreciated, but not " +
                                         "required."),
                            color=colors["green"]
                        ),
                        file=discord.File(
                            output,
                            filename=f"{filename}.{to_type}"
                        )
                    )
                    logger.info(
                        "Converted %s.%s sent by %s (ID: %s) to %s.%s",
                        filename,
                        from_type,
                        context.message.author,
                        context.message.author.id,
                        filename,
                        to_type
                    )
                else:
                    await context.send(embed=discord.Embed(
                        title="Failed to Convert File!",
                        description=(f"Hmm, I can't seem to convert this file "
                                     + f"to a `{to_type}`...maybe I'm not cut "
                                     + "out for this line of work "
                                     + ":face_exhaling:"),
                        color=colors["red"]
                    ))
                    logger.error(
                        "Failed to convert %s.%s sent by %s (ID: %s)",
                        filename,
                        from_type,
                        context.message.author,
                        context.message.author.id
                    )
        else:
            await context.send(embed=discord.Embed(
                title="Invalid Conversion!",
                description=f"I can't convert `{from_type}` to `{to_type}`.",
                color=colors["red"]
            ))


def setup(bot):
    bot.add_cog(Conversion(bot))
