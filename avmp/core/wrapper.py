"""Runtime for AVMP.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import os
import logging
from datetime import datetime, timedelta

from avmp.utils.logging_utils import logging_setup
from avmp.tools.jira_tools import JiraToolsAPI
from avmp.tools.tenable_tools import (TenableToolsAPI,
                                      TenableToolsCSV,
                                      build_jira_description)
from avmp.utils.vuln_db import TenableSqliteVulnDB


def main(config, scan_config):
    os.system('cls' if os.name == 'nt' else 'clear')
    logging_setup(os.path.basename(__file__), stdout=True)

    # Connecting to Jira and initilizing class.
    try:
        jiraAPI = JiraToolsAPI(config['creds']['jira']['server'],
                               username=config['creds']['jira']['api_username'],
                               password=config['creds']['jira']['api_password'])
    except Exception as e:
        logging.debug(
            f"{config['creds']['jira']['api_username']} failed to authenticate with Jira.\n\n{e}\n\n")

    # Connecting to Tenable and initilizing class.
    try:
        tenAPI = TenableToolsAPI(config['creds']['tenable']['access_key'],
                                 config['creds']['tenable']['secret_key'])
    except Exception as e:
        logging.debug(f"Failed to authenticate with Tenable API\n\n{e}\n\n")

    # Get raw scan data
    logging.info('Checking Tenable for new scan.')
    filepath = tenAPI.export_latest_scan(scan_config['scan_name'],
                                         os.path.join(
                                         os.getcwd(), 'data', 'scans'),
                                         overwrite=False)

    # Build vulnerability database
    db = TenableSqliteVulnDB(scan_config['ticket_db_filepath'])

    logging.info('Starting scan data import')
    items = TenableToolsCSV(
        filepath, min_cvss_score=scan_config['min_cvss_score']).group_by('Plugin ID')

    if items == None:
        logging.debug('No data was found given the min_cvss_score')
        return False

    tickets = TenableToolsCSV.organize(items)
    logging.info('Completed scan data import')

    ticket_counter = 0
    for ticket in tickets.values():
        # Looping according to the max ticket count
        if ticket_counter < scan_config['max_tickets'] or scan_config['max_tickets'] == 0:

            data = {**scan_config['data']}

            # Check to ensure all required fields are included
            if len(config['types']) > 0 and data['project']['key'] in config['types']:
                missing_fields = []
                for field in config['types'][data['project']['key']]:
                    if field not in scan_config['data']:
                        missing_fields.append(field)
                if len(missing_fields) != 0:
                    raise NameError(
                        f"The following fields were missing {missing_fields}")

            # Append variable data to data fields
            data['summary'] += ticket['Vuln Data']['Synopsis']
            data['summary'] = data['summary'].replace('\n', ' ')
            data['description'] += build_jira_description(ticket)
            if data['priority']['id'] == '':
                # Selects proper priority rating inside of Jira
                if ticket['Vuln Data']['Risk'] == 'Critical':
                    data['priority']['id'] = config['priorities']['Highest']
                elif ticket['Vuln Data']['Risk'] == 'High':
                    data['priority']['id'] = config['priorities']['High']
                elif ticket['Vuln Data']['Risk'] == 'Medium':
                    data['priority']['id'] = config['priorities']['Medium']
                elif ticket['Vuln Data']['Risk'] == 'Low':
                    data['priority']['id'] = config['priorities']['Low']
                else:
                    data['priority']['id'] = config['priorities']['Lowest']
            if data['duedate'] == '':
                # Build due date
                today = datetime.now()
                plus_days = config['due_dates'][ticket['Vuln Data']['Risk']]
                final_date = today + timedelta(days=int(plus_days))
                data['duedate'] = final_date.strftime("%Y-%m-%d")

            ip_list = set([x['IP Address'] for x in ticket['Hosts'].values()])

            # Check for already open tickets
            dups = db.get_all_tickets_by_plugin_id(
                ticket['Vuln Data']['Plugin ID'])

            # TODO: Add abiilty to open ticket for new IP's and link to existing vuln ticket.
            if len(dups) == 0:
                current = jiraAPI.create(data)
                ticket_counter += 1
                db.add_ticket(current, ticket['Vuln Data']
                              ['Plugin ID'], scan_config['default_ticket_status'], list(ip_list))

                # Attempt adding comment(s) to ticket
                if scan_config['comments'] != '':
                    for comment in scan_config['comments']:
                        try:
                            jiraAPI.comment(current, comment)
                            logging.info(
                                'Successfully applied comment on {}'.format(current))
                        except:
                            loggin.error(
                                'Failed to apply comment on {}'.format(current))

                # Attempt to log time saved to ticket
                    logged_work = jiraAPI.log_work(
                        current, scan_config['time_saved_per_ticket'], comment=scan_config['time_saved_comment'])

                # Attempt logging time to root ticket if provided
                if scan_config['root_ticket'] != "" and logged_work == False:
                    root_comment = '{} - {}'.format(
                        current, scan_config['time_saved_comment'])
                    jiraAPI.log_work(
                        scan_config['root_ticket'], scan_config['time_saved_per_ticket'], comment=root_comment)

                # Link ticket back to root ticket
                if scan_config['root_ticket'] != "":
                    try:
                        jiraAPI.link(scan_config['root_ticket'], current,
                                     issue_link_name='depends on')
                        logging.info('Linked {} to {}'.format(
                            scan_config['root_ticket'], current))
                    except:
                        logging.error('Failed to link {} to root ticket {}'.format(
                            current, scan_config['root_ticket']))
            else:
                logging.info('Plugin ID ({}) has an open ticket. Skipping...'.format(
                    ticket['Vuln Data']['Plugin ID']))


if __name__ == '__main__':
    pass
