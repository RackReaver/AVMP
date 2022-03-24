"""Functions for setting up logging accross this project.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"


import json
import logging
import os
import sys


def logging_setup(filename: str, stdout: bool = False) -> None:
    """Standard logging setup.

    args:
        filename (str): Script filename.

    kwargs:
        stdout (bool): Switch logging to stdout for testing

    return: None
    """
    isinstance(filename, str)

    if os.path.isdir("logs") == False:
        os.mkdir("logs")
        logging.info("Creating logs folder.")

    # Logging configuration
    if stdout == False:
        fmtstr = "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
        logging.basicConfig(
            filename="logs/{}.log".format(filename[:-3]),
            level=logging.DEBUG,
            filemode="a",
            format=fmtstr,
        )
    else:
        fmtstr = "[%(levelname)s]\t%(message)s"
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=fmtstr)
