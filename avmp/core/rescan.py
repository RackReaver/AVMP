"""When ticket is closed, this script will run an adhoc scan to check if vulnerability was remediated.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import json
from avmp.core.models import App


def main(issue, config):
    """Entry point for rescan script.

    args:
        issue (str): Issue to check against.
        config (dict): Tenant data
    """
    app = App(config, None)
    app.tenAPIcon()
    app.jiraAPIcon()


if __name__ == '__main__':
    filepath = 'C:/Users/mferreira/Desktop/vuln_manager/config.json'
    with open(filepath, 'r') as openFile:
        config = json.load(openFile)

        main('TO-28483', config)
