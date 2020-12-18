import argparse
import os
import sys

from stockstalker.common.logging import log
from stockstalker.parsers.parser_helpers import parser_factory
from stockstalker.util.helpers import load_configs_from_dir

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A tool to check stock of products")
    parser.add_argument('--config-dir', default=os.path.join(os.getcwd(), 'configs'), dest='config_dir')
    args = parser.parse_args()

    configs = load_configs_from_dir(args.config_dir)
    if not configs:
        log.error('No configs loaded')
        sys.exit(1)

    parsers = []
    for config in configs:
        parsers.append(parser_factory(config))

    print('')