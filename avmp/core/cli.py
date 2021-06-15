"""
AVMP command-line app.

Usage:
    avmp run [--config filepath] <process_config>
    avmp -h | --help
    avmp --version

Options:
    -h --help           Show this screen.
    --version           Show version.
    --config=filepath   AVMP configuration file [default: config.json]
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

from docopt import docopt
import json

from avmp.core import wrapper


def main():
    args = docopt(__doc__, version='0.0.1')

    if args['run'] == True:

        with open(args['--config'], 'r') as openFile:
            config = json.load(openFile)
        with open(args['<process_config>'], 'r') as openFile:
            process_config = json.load(openFile)

        wrapper.main(config, process_config)
