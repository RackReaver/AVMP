"""Entry point for command line interface.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import click
import json


@click.group()
@click.option('--config', '-c', default='config.json', show_default=True, help='File location for configurations.')
def cli(config):
    """
    Command line interface used to manage a vulnerability program.
    """
    pass

# cli.add_command()
