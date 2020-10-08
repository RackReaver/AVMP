import os
import json
import logging


def logging_setup(filename):
    """Standard logging setup.

    args:
        filename (str): Script filename.
    """
    isinstance(filename, str)

    if os.path.isdir('logs') == False:
        os.mkdir('logs')
        logging.info('Creating logs folder.')

    # Logging configuration
    fmtstr = '%(asctime)s:%(levelname)s:%(module)s:%(message)s'
    logging.basicConfig(
        filename='logs/{}.log'.format(filename[:-3]),
        level=logging.INFO,
        filemode='a',
        format=fmtstr
    )


def data_setup(filename):
    """Standard data file setup.

    args:
        filename (str): Script filename.
        data (str): data that should be written to file.

    Return: If file exists return json, else create file and return None.
    """
    isinstance(filename, str)
    FILENAME = filename[:-3]+".json"

    if os.path.isdir('data') == False:
        os.mkdir('data')
        logging.info('Creating data folder.')

    if os.path.isfile(f'data/{FILENAME}'):
        with open(FILENAME, 'r') as openFile:
            data = json.load(openFile)
            logging.info('Loaded JSON data file.')
        return data
    else:
        with open(FILENAME, 'w'):
            pass
        return None
