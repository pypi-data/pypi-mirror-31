from typing import Dict, Any

from blurr.cli.transform import transform
from blurr.cli.validate import validate_command


def cli(arguments: Dict[str, Any]) -> int:
    if arguments['validate']:
        return validate_command(arguments['<DTC>'])
    elif arguments['transform']:
        source = []
        if arguments['--source'] is not None:
            source = arguments['--source'].split(',')
        elif arguments['<raw-json-files>'] is not None:
            source = arguments['<raw-json-files>'].split(',')
        return transform(arguments['--streaming-dtc'], arguments['--window-dtc'], source)
