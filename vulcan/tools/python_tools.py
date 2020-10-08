import os
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
