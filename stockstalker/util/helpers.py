import json
import os
from json import JSONDecodeError
from typing import Text, List

from stockstalker.common.exceptions import InvalidConfigDirectory
from stockstalker.common.logging import log
from stockstalker.models.parser_config import ParserConfig


def load_configs_from_dir(config_dir: Text) -> List[ParserConfig]:
    """
    Take a given directory and attempt to load all .json files
    :rtype: List[ParserConfig]
    """
    configs = []
    if not os.path.isdir(config_dir):
        raise InvalidConfigDirectory(f'Invalid config directory: {config_dir}')
    for root, dirs, files in os.walk(config_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.json':
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        config_data = json.loads(f.read())
                except JSONDecodeError as e:
                    log.error('Invalid json in %s. %s', file, str(e))
                    continue
                configs.append(ParserConfig(**config_data))
    return configs
