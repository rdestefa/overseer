# overseer.helpers.configs_helpers

import logging
import logging.config
import os
import sys
from typing import Any
import yaml

import discord


def load_bot_configs(
    config_dir: str = "configs",
    config_path: str = "bot_config.yaml"
) -> dict[str, Any]:
    config_dir = config_dir or os.path.dirname(__file__)
    config_path = f"{config_dir}/{config_path}"

    if not os.path.isfile(config_path):
        sys.exit(f"'{config_path}' not found! Please add it and try again.")
    else:
        with open(config_path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

    return config


def load_logger(
    config_dir: str = "configs",
    config_path: str = "logging_config.yaml"
) -> logging.Logger:
    config_dir = config_dir or os.path.dirname(__file__)
    config_path = f"{config_dir}/{config_path}"

    if not os.path.isfile(config_path):
        logging.warning(f"'{config_path}' not found! Using default logger.")
    else:
        with open(config_path) as file:
            logging.config.dictConfig(yaml.load(file, Loader=yaml.FullLoader))

    logger = logging.getLogger()
    return logger


def load_colors(
    config_dir: str = "configs",
    config_path: str = "color_config.yaml"
) -> dict[str, int]:
    config_dir = config_dir or os.path.dirname(__file__)
    config_path = f"{config_dir}/{config_path}"

    colors = {
        "red": discord.Color.red(),
        "blue": discord.Color.blue(),
        "yellow": discord.Color.gold(),
        "orange": discord.Color.orange(),
        "green": discord.Color.green(),
        "purple": discord.Color.purple(),
        "gray": discord.Color.darker_grey(),
        "black": 0x000000,
        "white": 0xFFFFFF
    }

    if not os.path.isfile(config_path):
        logging.warning(f"'{config_path}' not found! Using default colors.")
    else:
        with open(config_path) as file:
            colors = yaml.load(file, Loader=yaml.FullLoader)

    return colors


def load_all_configs(
    config_dir: str = "configs",
    bot_config_path: str = "bot_config.yaml",
    logger_config_path: str = "logging_config.yaml",
    color_config_path: str = "color_config.yaml"
) -> tuple[dict[str, Any], logging.Logger, discord.Intents]:
    bot_configs = load_bot_configs(config_dir, bot_config_path)
    logger = load_logger(config_dir, logger_config_path)
    colors = load_colors(config_dir, color_config_path)

    return bot_configs, logger, colors
