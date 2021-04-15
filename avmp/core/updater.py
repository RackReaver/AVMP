"""
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import logging

from avmp.tools.jira_tools import JiraToolsAPI
from avmp.utils.vuln_db import TenableSqliteVulnDB


def main(vuln_db_filepath, config):
    root_ticket = input('Root ticket for logging time: ')
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
        logged_work = jiraAPI.log_work(
            ticket[0], '5m', comment='Updating vulnerability database.')

        # Attempt logging time to root ticket if provided
        if root_ticket != "" and logged_work == False:
            root_comment = '{} - {}'.format(
                ticket[0], COMMENT)
            jiraAPI.log_work(
                root_ticket, '5m', comment='Updating vulnerability database.')

        db.update_status_by_ticket_number(ticket[0], str(data.fields.status))
