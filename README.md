# Overseer

The Overseer is a basic asynchronous [Discord](https://discord.com/) bot using [asyncio](https://docs.python.org/3/library/asyncio.html) that carries out simple tasks for the following:

- Calendar management
- File conversion
- Moderation
- Text formatting

## Python Version

- [Python](https://www.python.org/) [3.10+](https://www.python.org/downloads/release/python-3100/) is required to run the Overseer.

## Dependencies (Non-Standard Library)

- [discord.py](https://discordpy.readthedocs.io/en/stable/) (The Overseer's Core)
- [glom](https://glom.readthedocs.io/en/latest/index.html) (`overseer.bot`)
- [icalendar](https://icalendar.readthedocs.io/en/latest/#) (`overseer.cogs.calendar`)
- [asynctempfile](https://pypi.org/project/asynctempfile/) (`overseer.cogs.conversion`)
- [aiohttp](https://docs.aiohttp.org/en/stable/) (`overseer.cogs.fun`)
- [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) (`overseer.utils.configs`)
- [python-Levenshtein](https://www.coli.uni-saarland.de/courses/LT1/2011/slides/Python-Levenshtein.html) (`overseer.utils.error_handlers`)

## Non-Python Dependencies

- [ffmpeg](https://www.ffmpeg.org/) (`overseer.cogs.conversion`)
- [ffprobe](https://ffmpeg.org/ffprobe.html) (`overseer.cogs.conversion`)

## Configuration

The Overseer uses `.yaml` configuration files to run properly. Some are essential and the Overseer will not start without them. Others are optional and will fall back on default configurations if an associated `.yaml` file is not found. All configuration files should exist in the `~/overseer/.config` directory.

All the Overseer's configuration files are listed below:

- Required

  - `overseer.yaml` - The essential configs for the Overseer. Example formatting:

    ```
    token: <token: string>
    application_id: <id: string>
    owners:
      - <owner1_id: int>
      - <owner2_id: int>
      ...
    general_channel_id: <channel_id: int>
    bot_prefix: <prefix: string>
    intents:
      bans: <boolean>
      dm_messages: <boolean>
      guilds: <boolean>
      ...
    ```

  - `colors.yaml` - All the colors that the Overseer will use during execution. Example formatting:

    ```
    red: <hex_code: int>
    yellow: <hex_code: int>
    green: <hex_code: int>
    ...
    ```

  - `conversion.yaml` - The different kinds of supported file conversions and their associated `ffmpeg` arguments. Example formatting:

    ```
    valid_conversions:
      !!python/tuple [<from_extension: string>, <to_extension: string>]:
        [[<input_arguments: string>], [<output_arguments: string>]]
      ...
    aliases:
      <extension: string>: <aliased_extension: string>
      ...
    unsupported_embeds: !!set {<extension: string>}
    ```

- Optional

  - `logging.yaml` - The Overseer's logger configurations. Example formatting:

    ```
    version: <version_no: int>
    formatters:
      <formatter_name: string>:
        format: <format_string: string>
        datefmt: <data_format_string: string>
    handlers:
      console:
        class: logging.StreamHandler
        level: <DEBUG | INFO | WARNING | ERROR | CRITICAL>
        formatter: <formatter_name>
        stream: ext://sys.<stdout | stderr>
      file:
        class: logging.FileHandler
        level: <DEBUG | INFO | WARNING | ERROR | CRITICAL>
        formatter: <formatter_name>
        filename: <file_path: string>
    loggers:
      overseer:
        level: <DEBUG | INFO | WARNING | ERROR | CRITICAL>
        handlers: [console, file]
    root:
      level: <DEBUG | INFO | WARNING | ERROR | CRITICAL>
      handlers: [console, file]
    ```

## Running the Overseer:

The different ways to run the Overseer from the main `overseer` directory are as follows:

- Using the [Python Launcher](https://www.python.org/dev/peps/pep-0397/):

  ```
  py -<version> bot.py
  ```

- Using the regular Python executable:

  ```
  python bot.py
  ```
