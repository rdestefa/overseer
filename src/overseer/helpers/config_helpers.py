# overseer.helpers.config_helpers

import logging
import logging.config
import os
import sys
from typing import Any
import yaml


def load_bot_configs(
    config_dir: str = None
) -> tuple[dict[str, Any], logging.Logger]:
    config_dir = os.path.expanduser(config_dir or "~/overseer/.config")
    bot_config_path = os.path.join(config_dir, "overseer.yaml")
    logger_config_path = os.path.join(config_dir, "logging.yaml")

    # Load Overseer configs.
    if os.path.isfile(bot_config_path):
        with open(bot_config_path) as file:
            config = yaml.safe_load(file)
    else:
        sys.exit(f"'{bot_config_path}' not found!")

    # Initialize Overseer logger.
    if os.path.isfile(logger_config_path):
        with open(logger_config_path) as file:
            logging.config.dictConfig(yaml.safe_load(file))
    else:
        logging.warning(f"'{logger_config_path}' not found! Using default.")

    logger = logging.getLogger()
    return config, logger


def load_config(
    filename: str,
    safe: bool = True,
    default: dict[Any, Any] | list[Any] = {},
    config_dir: str = None
) -> dict[Any, Any] | list[Any]:
    config_dir = os.path.expanduser(config_dir or "~/overseer/.config")
    config_path = os.path.join(config_dir, filename + '.yaml')

    if os.path.isfile(config_path):
        with open(config_path) as file:
            if safe:
                config = yaml.safe_load(file)
            else:
                config = yaml.full_load(file)
    else:
        logging.warning(f"'{config_path}' not found! Using default values.")
        config = default

    return config
