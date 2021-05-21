"""When ticket is closed, this script will run an adhoc scan to check if vulnerability was remediated.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import re
import json

from avmp.core.models import App
from avmp.tools.python_tools import extract_ips


def main(issue, config):
    """Entry point for rescan script.

    args:
        issue (str): Issue to check against.
        config (dict): Tenant data
    """
    app = App(config, None)
    app.tenAPIcon()
    app.jiraAPIcon()

    current = app.jiraAPI._JIRA.issue(issue)

    ips = extract_ips(current.fields.description)
    plugin_id = extract_plugin_id(current.fields.description)
    input(plugin_id)

    # Remove duplicate ips
    ips = [ip for num, ip in enumerate(ips) if ip not in ips[:num]]

    from pprint import pprint
    pprint(app.tenAPI.tio.plugins.plugin_details(
        '56209')['attributes'][1]['attribute_value'])

    folder_id = app.tenAPI.create_folder(app.RESCAN_FOLDER_NAME)
    # scan = app.tenAPI.tio.scans.create(name='{} - Rescan'.format(issue),
    #                                    folder_id=folder_id,
    #                                    enabled=True,
    #                                    launch='ON_DEMAND',
    #                                    text_targets=','.join(ips))


def extract_plugin_id(text):
    """Given text extract the plugin_id

    args:
        text (str): String to extract the plugin_id from

    return (list): List of IP Addresses
    """
    # TODO: Create plugin id extractor


if __name__ == '__main__':
    filepath = 'C:/Users/mferreira/Desktop/vuln_manager/config.json'
    with open(filepath, 'r') as openFile:
        config = json.load(openFile)

        main('TO-28483', config)
