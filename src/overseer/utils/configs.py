# overseer.utils.configs

from glom import glom
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
        sys.exit(f"'{bot_config_path}' not found")

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
    required: bool = True,
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
        if not required:
            logging.warning(f"'{config_path}' not found! Default values used.")
            config = default
        else:
            sys.exit(f"'{config_path}' not found")

    return config


def load_config_attr(
    filename: str,
    attr: Any,
    safe: bool = True,
    config_dir: str = None,
    default: Any = None
) -> Any:
    configs = load_config(filename, safe, False, config_dir=config_dir)

    if configs and isinstance(configs, dict):
        return glom(configs, attr, default=default)
    else:
        return None
