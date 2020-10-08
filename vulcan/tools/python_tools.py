import logging


def logging_setup(filename):
    """Standard logging setup.

    args:
        filename (str): Script filename.
    """
    isinstance(filename, str)
    # Logging configuration
    fmtstr = '%(asctime)s:%(levelname)s:%(module)s:%(message)s'
    logging.basicConfig(
        filename='{}.log'.format(filename),
        level=logging.INFO,
        filemode='a',
        format=fmtstr
    )
