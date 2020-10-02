"""Tools for accessing and importing Tenable data.
"""
__copyright__ = "Copyright (C) 2020  Matt Ferreira"
__license__ = "Apache License"

import os
import csv
from datetime import datetime
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

    def export_latest_scan(self, scan_name, folder, overwrite=None, export_format='csv'):
        """Export the latest scan given a scan name and folder filepath.

        args:
            scan_name (str): Name of scan found in Tenable.
            folder (str): Root folder where scan data should be saved.

        kwargs:
            overwrite (bool): [default: None] Programatic way to determine if existing files should be overwriten.
            export_format (str): [default: csv] Format data should be saved as (this aligns with the TenableIO documentation).

        Return (str): Filepath of scan
        """
        assert isinstance(scan_name, str)
        assert isinstance(folder, str)
        assert isinstance(export_format, str)

        SCAN_NAME = scan_name
        SAVE_FOLDER = os.path.join(folder, SCAN_NAME)

        # Creates sub-folder if one does not exist
        if os.path.isdir(SAVE_FOLDER) is not True:
            logging.info('Sub-folder not found... Creating now.')
            os.makedirs(SAVE_FOLDER)

        scan_meta_data = self.get_scan_meta_data(SCAN_NAME)

        # Get latest scan history id
        history_id, scan_date = self._get_latest_history_id(
            scan_meta_data['id'])
        scan_date = datetime.fromtimestamp(scan_date).strftime('%Y-%m-%d')

        filename = f'{scan_date} - {SCAN_NAME}'
        filepath = f'{SAVE_FOLDER}/{filename}.{export_format}'

        # Check if file exists
        if os.path.exists(f'{filepath}'):
            if overwrite == False or overwrite == True:
                pass
            else:
                user_input = input(
                    f'"{filename}" exists, would you like to overwrite it? (n): ')
                if user_input.lower() == 'y' or user_input.lower() == 'yes':
                    overwrite = True
                else:
                    overwrite = False
        else:
            overwrite = True

        # Checking if overwriting is permitted
        if overwrite != False:
            # Save to supplied folder
            logging.info(f'{filepath}')
            with open(filepath, 'wb') as openFile:
                self.tio.scans.export(
                    scan_meta_data['id'], history_id=history_id, fobj=openFile, format=export_format)
        else:
            logging.info('Existing file found, overwriting not permitted.')

        return filepath

    def _get_latest_history_id(self, scan_id):
        """Class function to identify latest history id.

        args:
            scan_id (str): Scan id to capture latest history id.

        Return: history_id (str), scan_date (datetime).
        """
        isinstance(scan_id, str)

        first = True
        for history in self.tio.scans.history(scan_id):

            history_time_start = history['time_start']

            if first:
                scan_date = history_time_start
                history_id = history['id']
                first = False
            else:
                if scan_date < history_time_start:
                    scan_date = history_time_start
                    history_id = history['id']

        return history_id, scan_date


class TenableToolsCSV:
    def __init__(self,  filepath, min_cvss_score=None):
        isinstance(filepath, str)

        self.filepath = filepath
        self.min_cvss_score = min_cvss_score
        self.columns, self.rows = self._importer()

    def _importer(self):
        """Import Tenable csv file.

        Return: column names (tuple), rows (tuple)
        """
        with open(self.filepath, 'r', encoding='utf-8-sig') as import_file:
            reader = csv.reader(import_file)
            first = True
            final_list = []
            for num, row in enumerate(reader):
                temp_dict = {}
                if first == True:
                    title_info = (tuple(row))
                    first = False
                else:
                    for sub_num, item in enumerate(row):
                        temp_dict[title_info[sub_num]] = item
                    if self.min_cvss_score != None:
                        if float(temp_dict['CVSS']) >= float(self.min_cvss_score):
                            final_list.append(temp_dict)

        return tuple(title_info), tuple(final_list)

    def group_by(self, column_name):

        data = self.rows

        # Check if column name exists
        column_exists = False
        for row in data:
            for key in row.keys():
                if key == column_name:
                    column_exists = True
        # Error out if column does not exist
        if column_exists == False:
            raise DataError('group_by column not found.')

        # Group by column name
        grouped_dict = {}
        for row in data:
            if row[column_name] not in grouped_dict:
                grouped_dict[row[column_name]] = {}

            next_num = len(grouped_dict[row[column_name]]) + 1

            grouped_dict[row[column_name]][next_num] = row

        return grouped_dict
