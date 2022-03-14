"""Runtime for AVMP.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import logging
import os
import socket
from datetime import datetime, timedelta

from avmp.core.exceptions import MissingConfiguration
from avmp.core.models import App
from avmp.tools.tenable_tools import TenableToolsCSV, build_jira_description
from avmp.utils.logging_utils import logging_setup
from avmp.utils.vuln_db import TenableSqliteVulnDB


def main(config, process_config):
    os.system('cls' if os.name == 'nt' else 'clear')
    logging_setup(os.path.basename(__file__), stdout=True)

    app = App(config, process_config)
    app.jiraAPIcon()

    # Check for process_type variable in scan config
    if "process_type" in app.process_config:
        # Determine scan type and run function for said type
        if 'static' in app.process_config['process_type']:
            static(app)
        elif 'dynamic' in app.process_config['process_type']:
            dynamic(app)
        else:
            message = '"process_type" (static or dynamic) is required. See documentation for examples.'
            logging.error(message)
            raise MissingConfiguration(message)
    else:
        message = 'No "process_type" variable provided in scan config. See documentation for examples.'
        logging.error(message)
        raise MissingConfiguration(message)


def static(app):
    """Generate static tickets found in config file.
    """
    # Create parent ticket
    logging.info('Creating tickets...')
    parent_ticket = app.jiraAPI.create(app.process_config['parent_ticket'])
    logging.info('{} used "{}" to create parent ticket "{}" successfully in Jira'.format(
        socket.gethostname(), app.config['creds']['jira']['username'], parent_ticket))

    # Log time saved
    jira_log_time(app, parent_ticket)

    logging.info(
        'Successfully created parent ticket ({})'.format(parent_ticket))

    # Create sub-tasks
    for key in app.process_config['sub_tasks']:

        # Set parent ticket in config if it doesn't exist
        if "parent" not in app.process_config['sub_tasks'][key]:
            app.process_config['sub_tasks'][key]['parent'] = {
                "key": parent_ticket}

        child = app.jiraAPI.create(app.process_config['sub_tasks'][key])
        logging.info('{} used "{}" to create child ticket "{}" under "{}" successfully in Jira'.format(
            socket.gethostname(), app.config['creds']['jira']['username'], child, parent_ticket))

        # Log time saved
        jira_log_time(app, child)

        logging.info('Successfully created sub_task ticket ({})'.format(child))

    logging.info('Tickets created successfully')


def dynamic(app):
    """Generate tickets for Tenable vulnerabilities.
    """
    # Setup connection to Tenable IO
    app.tenAPIcon()

    # Get raw scan data
    logging.info('Checking Tenable for new scan.')

    if app.tenAPI.check_scan_in_progress(app.process_config['scan_name']) == True:
        logging.info('Latest scan is still running, try again later.')
        return False
    else:
        filepath = app.tenAPI.export_latest_scan(app.process_config['scan_name'],
                                                 os.path.join(
            os.getcwd(), 'data', 'scans'),
            overwrite=False)

        # Build vulnerability database
        db = TenableSqliteVulnDB(app.process_config['ticket_db_filepath'])

        logging.info('Starting scan data import')
        items = TenableToolsCSV(
            filepath, min_cvss_score=app.process_config['min_cvss_score']).group_by('Plugin ID')

        if items == None:
            logging.debug('No data was found given the min_cvss_score')
            return False

        tickets = TenableToolsCSV.organize(items)
        logging.info('Completed scan data import')
        logging.info('Creating tickets for "{}"'.format(
            app.process_config['scan_name']))

        ticket_counter = 0
        for ticket in tickets.values():
            # Looping according to the max ticket count
            if ticket_counter < app.process_config['max_tickets'] or app.process_config['max_tickets'] == 0:

                data = {**app.process_config['data']}

                # Check to ensure all required fields are included
                if len(app.config['types']) > 0 and data['project']['key'] in app.config['types']:
                    missing_fields = []
                    for field in app.config['types'][data['project']['key']]:
                        if field not in app.process_config['data']:
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
                        data['priority']['id'] = app.config['priorities']['Critical']
                    elif ticket['Vuln Data']['Risk'] == 'High':
                        data['priority']['id'] = app.config['priorities']['High']
                    elif ticket['Vuln Data']['Risk'] == 'Medium':
                        data['priority']['id'] = app.config['priorities']['Medium']
                    else:
                        data['priority']['id'] = app.config['priorities']['Low']

                if data['duedate'] == '':
                    # Build due date
                    today = datetime.now()
                    if ticket['Vuln Data']['Risk'] in app.config['due_dates']:
                        plus_days = app.config['due_dates'][ticket['Vuln Data']['Risk']]
                    else:
                        plus_days = app.config['due_dates']['Low']

                    final_date = today + timedelta(days=int(plus_days))
                    data['duedate'] = final_date.strftime("%Y-%m-%d")

                ip_list = set([x['IP Address']
                               for x in ticket['Hosts'].values()])

                # Check for already open tickets
                dups = db.get_all_tickets_by_plugin_id(
                    ticket['Vuln Data']['Plugin ID'])

                # TODO: Add abilty to open ticket for new IP's and link to existing vuln ticket.

                if len(dups) == 0 or app.process_config['allow_ticket_duplication'] == True:
                    if len(dups) != 0:
                        logging.info('Plugin ID ({}) has an open ticket. Creating duplicate...'.format(
                            ticket['Vuln Data']['Plugin ID']))

                    current = app.jiraAPI.create(data)
                    ticket_counter += 1
                    db.add_ticket(current, ticket['Vuln Data']
                                  ['Plugin ID'], app.process_config['default_ticket_status'], list(ip_list))

                    # Attempt adding comment(s) to ticket
                    if app.process_config['comments'] != '':
                        for comment in app.process_config['comments']:
                            try:
                                app.jiraAPI.comment(current, comment)
                                logging.info(
                                    'Successfully applied comment on {}'.format(current))
                            except:
                                logging.error(
                                    'Failed to apply comment on {}'.format(current))

                    # Log time saved
                    jira_log_time(app, current)

                    # Link ticket back to root ticket
                    if app.process_config['root_ticket'] != "":
                        try:
                            app.jiraAPI.link(app.process_config['root_ticket'], current,
                                             issue_link_name='depends on')
                            logging.info('Linked {} to {}'.format(
                                app.process_config['root_ticket'], current))
                        except:
                            logging.error('Failed to link {} to root ticket {}'.format(
                                current, app.process_config['root_ticket']))
                else:
                    logging.info('Plugin ID ({}) has an open ticket. Skipping...'.format(
                        ticket['Vuln Data']['Plugin ID']))


def jira_log_time(app, ticket):
    """Log time to newly created ticket, if fails log against root ticket if exists.

    app (class): Instance of the current runtime
    ticket (str): Ticket that was just created

    return (bool): Confirmation if time was logged.
    """
    logged_work = app.jiraAPI.log_work(
        ticket, app.process_config['time_saved_per_ticket'], comment=app.process_config['time_saved_comment'])

    if "root_ticket" in app.process_config and app.process_config['root_ticket'] != "" and logged_work == False:
        root_comment = '{} - {}'.format(
            ticket, app.process_config['time_saved_comment'])
        root_ticket_logged_work = app.jiraAPI.log_work(
            app.process_config['root_ticket'], app.process_config['time_saved_per_ticket'], comment=root_comment)

    if logged_work == True or root_ticket_logged_work == True:
        return True
    else:
        return False


if __name__ == '__main__':
    import json
    config_location = 'avmp/test_data/config.json'
    config = json.load(open(config_location, 'r'))

    config_location = 'avmp/test_data/process_configs/asv_process_config.json'
    process_config = json.load(open(config_location, 'r'))

    main(config, process_config)
