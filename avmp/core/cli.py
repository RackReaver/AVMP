"""
      __      ____  __ _____  
     /\ \    / /  \/  |  __ \ 
    /  \ \  / /| \  / | |__) |
   / /\ \ \/ / | |\/| |  ___/ 
  / ____ \  /  | |  | | |     
 /_/    \_\/   |_|  |_|_|     
                              
A collection of tools for managing and automating vulnerability management.

Usage:
    avmp run [--config filepath] <process_config>
    avmp update [--config filepath] <ticket_db_filepath> 
    avmp -h | --help
    avmp --version

Options:
    -h --help           Show this screen.
    --version           Show version.
    --config=filepath   AVMP configuration file [default: config.json]
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import json

from docopt import docopt

from avmp.core import updater, wrapper


def main():
    args = docopt(__doc__, version="0.0.2")

    if args["run"] == True:

        with open(args["--config"], "r") as openFile:
            config = json.load(openFile)
        with open(args["<process_config>"], "r") as openFile:
            process_config = json.load(openFile)

        wrapper.main(config, process_config)

    elif args["update"] == True:

        with open(args["--config"], "r") as openFile:
            config = json.load(openFile)

        updater.main(args["<ticket_db_filepath>"], config)
