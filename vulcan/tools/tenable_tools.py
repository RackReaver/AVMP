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

    def get_all_scan_names(self):
        scan_list = self.tio.scans.list()

        scans = []
        for scan in scan_list:
            scans.append(scan['name'])

        return scans

    def get_scan_meta_data(self, scan_name):
        """Gets scan meta data for a provided scan_name.

        args:
            scan_name (str): Name of scan found in Tenable.

        Return (dict): Scan meta data.
        """
        # Get list of all scans in Tenable
        scan_list = self.tio.scans.list()

        for scan in scan_list:
            if scan['name'] == scan_name:
                return scan
