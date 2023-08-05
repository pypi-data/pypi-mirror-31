"""
Usage:
    blurr validate [--debug] [<DTC> ...]
    blurr transform [--debug] [--streaming-dtc=<dtc-file>] [--window-dtc=<dtc-file>] (--source=<raw-json-files> | <raw-json-files>)
    blurr -h | --help

Commands:
    validate        Runs syntax validation on the list of DTC files provided. If
                    no files are provided then all *.dtc files in the current
                    directory are validated.
    transform       Runs blurr to process the given raw log file. This command
                    can be run with the following combinations:
                    1. No DTC provided - The current directory is searched for
                    DTCs. First streaming and the first window DTC are used.
                    2. Only streaming DTC given - Transform outputs the result of
                    applying the DTC on the raw data file.
                    3. Both streaming and window DTC are provided - Transform
                    outputs the final result of applying the streaming and window
                    DTC on the raw data file.

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    --streaming-dtc=<dtc-file>  Streaming DTC file to use.
    --window-dtc=<dtc-file>     Window DTC file to use.
    --source=<raw-json-files>   List of source files separated by comma
    --debug                     Output debug logs.
"""
import logging
import sys

import os
from docopt import docopt

from blurr.cli.cli import cli

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_PATH = os.path.join(PACKAGE_DIR, 'VERSION')


def read_version(version_file: str) -> str:
    if os.path.exists(version_file) and os.path.isfile(version_file):
        with open(version_file, 'r') as file:
            version = file.readline()
            file.close()
        return version
    else:
        return 'LOCAL'


def setup_logs(debug: bool) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(_handler)


def main():
    arguments = docopt(__doc__, version=read_version(VERSION_PATH))
    setup_logs(arguments['--debug'])
    result = cli(arguments)
    sys.exit(result)


if __name__ == '__main__':
    main()
