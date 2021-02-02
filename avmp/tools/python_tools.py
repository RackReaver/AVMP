"""Python tools for package.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import os
import json
import logging


class DataSetup:
    def __init__(self, filename):
        """Standard data file setup.

        args:
            filename (str): Script filename.

        Return: None
        """
        assert isinstance(filename, str)
        self.filename = filename[:-3]+".json"
        self.filepath = 'data/' + self.filename

        # Check/Create data folder
        if os.path.isdir('data') == False:
            os.mkdir('data')
            logging.info('Creating data folder.')
        if not os.path.isfile(self.filepath):
            with open(self.filepath, 'w') as openFile:
                openFile.write('{}')

    def get_data(self):
        """Pull data from file

        Return (dict): Data found in data file.
        """
        with open(self.filepath, 'r') as openFile:
            data = json.load(openFile)
            logging.info('Loaded JSON data file.')
        return data

    def put_data(self, data):
        """Re-write data to file

        args:
            data (dict): Data to be converted to json and written to file

        Return (bool): If successful True, else False
        """
        assert isinstance(data, dict)
        try:
            with open(self.filepath, 'w') as openFile:
                openFile.write(json.dumps(data))

            logging.info('JSON exported to data file.')

            return True
        except Exception as e:
            logging.warning(e)
            return False
