"""Tools for accessing and importing Tenable data.
"""
__copyright__ = "Copyright (C) 2020  Matt Ferreira"
__license__ = "Apache License"

import os
from datetime import date
import logging
from tenable.io import TenableIO


class TenableToolsAPI:
    def __init__(self, access_key, secret_key):
    """Capture access and secret key for Tenable.IO API

    args:
        access_key (str): Access key for Tenable.IO.
        secret_key (str): Secret key for Tenable.IO.
    
    Return: None
    """
    self.access_key = access_key
    self.secret_key = secret_key

    self.tio = TenableIO(self.access_key, self.secret_key)

    def get_scan_data(scan_name):
        # TODO
        pass
