# overseer.helpers.configs_helpers

import logging
import logging.config
import os
import sys
from typing import Any
import yaml

import discord


def load_bot_configs(config_path: str = "bot_config.yaml") -> dict[str, Any]:
    if not os.path.isfile(config_path):
        sys.exit(f"'{config_path}' not found! Please add it and try again.")
    else:
        with open(config_path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

    return config


def load_logger(config_path: str = "logging_config.yaml") -> logging.Logger:
    if not os.path.isfile(config_path):
        logging.warning(f"'{config_path}' not found! Using default logger.")
    else:
        with open(config_path) as file:
            logging.config.dictConfig(yaml.load(file, Loader=yaml.FullLoader))

    logger = logging.getLogger()
    return logger


def load_all_configs(
    bot_config_path: str = "bot_config.yaml",
    logger_config_path: str = "logging_config.yaml",
) -> tuple[dict[str, Any], logging.Logger, discord.Intents]:
    bot_configs = load_bot_configs(bot_config_path)
    logger = load_logger(logger_config_path)

    return bot_configs, logger
