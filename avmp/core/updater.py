"""
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import logging

from avmp.tools.jira_tools import JiraToolsAPI
from avmp.utils.vuln_db import TenableSqliteVulnDB


def updater(vuln_db_filepath, config):
    db = TenableSqliteVulnDB(vuln_db_filepath)
    tickets = db.get_all_tickets()

    try:
        jiraAPI = JiraToolsAPI(config['creds']['jira']['server'],
                               username=config['creds']['jira']['api_username'],
                               password=config['creds']['jira']['api_password'])
    except Exception as e:
        logging.debug(
            f"{config['creds']['jira']['api_username']} failed to authenticate with Jira.\n\n{e}\n\n")

    for num, ticket in enumerate(tickets):
        print(f'Updating {ticket[0]} ({num+1} of {len(tickets)})')
        data = jiraAPI._JIRA.issue(ticket[0])
        db.update_status_by_ticket_number(ticket[0], str(data.fields.status))


if __name__ == '__main__':
    import json
    with open('config.json', 'r') as openFile:
        config = json.load(openFile)

    vuln_db_filepath = 'tickets.db'
    updater(vuln_db_filepath, config)
