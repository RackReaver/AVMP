"""Tools for accessing and importing Tenable data.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import csv
import logging
import os
from datetime import datetime

from tenable.io import TenableIO


class DataError(Exception):
    """raised error"""


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
        self.scans = self.get_all_scan_names()
        logging.info("Authenticated successfully with Tenable")

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

    def get_scan_info(self, scan_name):
        """Gets scan info for a provided scan_name.

        args:
            scan_name (str): Name of scan found in Tenable.

        Return (dict): Scan meta data.
        """
        # Get list of all scans in Tenable
        scan_list = self.tio.scans.list()

        for scan in scan_list:
            if scan['name'] == scan_name:
                latest_scan_uuid = next(self.tio.scans.history(scan['id']))[
                    'scan_uuid']
                return self.tio.scans.info(scan['id'], latest_scan_uuid)

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
            logging.info('subFolder not found... Creating now.')
            os.makedirs(SAVE_FOLDER)

        scan_meta_data = self.get_scan_meta_data(SCAN_NAME)

        # Get latest scan history id
        history_id, scan_date = self._get_latest_history_id(
            str(scan_meta_data['id']))
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
            logging.info('Downloading scan to supplied folder')
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
        assert isinstance(scan_id, str)

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

    def check_scan_in_progress(self, scan_name):
        scan_meta_data = self.get_scan_info(scan_name)

        if scan_meta_data['status'] == 'running':
            return True
        else:
            return False


class TenableToolsCSV:
    def __init__(self,  filepath, min_cvss_score=None):
        assert isinstance(filepath, str)

        self.filepath = filepath
        self.min_cvss_score = min_cvss_score
        self.columns, self.rows = self._importer()

    def _importer(self):
        """Import Tenable csv file.

        Return: column names (tuple), rows (tuple)
                returns 'None' if no data is available.
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

        if len(final_list) == 0:
            return None

        return tuple(title_info), tuple(final_list)

    def group_by(self, column_name):
        """Group data by a given column name.

        args:
            column_name (str): Column name to group by.

        return (dict): Grouped dictionary
                       return 'None' if no data to group.
        """

        # Check if data was imported
        if len(self.rows) != 0:
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
        else:
            return None

    @staticmethod
    def organize(grouped_dict):
        """Given data from grouped_dict function seperate the
        vulnerability and host information.

        args:
            grouped_dict (dict): Data from grouped_dict function.

        return (dict): Organized dictionary [i.e. {'Vuln Data': {...}, 'Hosts': {...}]

        """
        static_data_keys = ['CVE',
                            'CVSS',
                            'CVSS Base Score',
                            'CVSS Temporal Score',
                            'CVSS Temporal Vector',
                            'CVSS Vector',
                            'CVSS3 Base Score',
                            'CVSS3 Temporal Score',
                            'CVSS3 Temporal Vector',
                            'CVSS3 Vector',
                            'Description',
                            'Name',
                            'Plugin Family',
                            'Plugin ID',
                            'Risk',
                            'Solution',
                            'See Also',
                            'Synopsis']

        organized_data = {}

        # Loop through grouping
        for group_name, group_value in grouped_dict.items():
            new_grouped_dict = {}
            static_data = {}
            host_data = {}

            first = True
            # Loop through items
            for key, item in group_value.items():
                temp_host_items = {}

                # Loop through value pairs
                for title, value in item.items():

                    # Extract vulnerability information
                    if first and title in static_data_keys:
                        static_data[title] = value

                    # Extract host information
                    elif title not in static_data_keys:
                        temp_host_items[title] = value

                if first:
                    new_grouped_dict['Vuln Data'] = static_data
                    first = False
                host_data[key] = temp_host_items

                new_grouped_dict['Hosts'] = host_data
            organized_data[group_name] = new_grouped_dict

        return organized_data


def build_jira_description(ticket):
    """Given a ticket after running TenableToolsCSV.organize this will build a formatted jira description.

    args:
        ticket (dict): This must br from TenableToolsCSV.organize

    return (str): Description string.
    """
    jira_description = 'h3. (!) *PLEASE BE SURE TO PROVIDE EVIDENCE!* *Screenshots, a config output, etc.* (!)\n'
    jira_description += '----\n'
    jira_description += 'h2. *{}* '.format(ticket['Vuln Data']['Name'].strip())
    jira_description += '*({})*\n'.format(
        ticket['Vuln Data']['Plugin ID'].strip())
    jira_description += '{panel:title=Overview}\n'
    jira_description += 'h3. +Synopsis+\n'
    jira_description += ticket['Vuln Data']['Synopsis'].strip() + '\n'
    jira_description += 'h3. +Description+\n'
    jira_description += ticket['Vuln Data']['Description'].strip() + '\n'
    jira_description += 'h3. +Solution+\n'
    jira_description += ticket['Vuln Data']['Solution'].strip() + '\n'
    jira_description += 'h3. +See Also+\n'
    jira_description += ticket['Vuln Data']['See Also'].strip() + '\n'
    jira_description += '{panel}\n'
    jira_description += '{panel:title=Supplement Information}\n'

    # Loop through static data
    for key, value in ticket['Vuln Data'].items():
        if key not in ['Name', 'Synopsis', 'Description', 'Solution', 'See Also']:
            jira_description += '* *{}:* {}\n'.format(key, value)

    # Build host section and table header
    jira_description += '{panel}\n'
    jira_description += '{panel:title=Hosts}\n'
    jira_description += '||IP Address||Port||Host||OS||MAC Address||Scan Start||Scan End||Plugin Output||\n'

    # Loop through hosts
    for host in ticket['Hosts'].values():
        jira_description += '|'
        jira_description += '{} |'.format(host['IP Address'])
        jira_description += '{} |'.format(host['Port'])
        jira_description += '{} |'.format(host['Host'])
        jira_description += '{} |'.format(host['OS'])
        jira_description += '{} |'.format(host['MAC Address'])
        jira_description += '{} |'.format(zulu_to_mdy(host['Host Start']))
        jira_description += '{} |'.format(zulu_to_mdy(host['Host End']))
        code_str = '{code}'
        jira_description += '{}{}{} |'.format(code_str,
                                              host['Plugin Output'], code_str)
        jira_description += '\n'

    jira_description += '{panel}\n'
    jira_description += '----\n'
    jira_description += 'h3. (!) *PLEASE BE SURE TO PROVIDE EVIDENCE!* *Screenshots, a config output, etc.* (!)\n'

    return jira_description


def zulu_to_mdy(zulu_date):
    """Converts Tenables time format (Zulu) to MDY (Month, Day, Year)

    args:
        zulu_date (str): Tenable given time format

    return (str): MDY (Month, Day, Year)
    """
    return datetime.strptime(zulu_date[:19], "%Y-%m-%dT%H:%M:%S").strftime('%m-%d-%Y %I:%M %p')
