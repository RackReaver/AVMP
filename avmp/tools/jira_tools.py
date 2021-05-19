"""Classes and functions for communicating with Jira.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import logging
from jira import JIRA
from getpass import getpass

from avmp.core.exceptions import InputError


class JiraToolsAPI:
    def __init__(self, jira_server_link, username=None, password=None):
        """Initalizes the Jira API connector. If a username or password is not provided you will be prompted for it.

        args:
            jira_server_link (str): Link to the Jira server to touch API

        kwargs:
            username (str): Overwrites jira username prompt
            password (str): Overwrites jira password prompt

        return: None
        """
        self.jira_server_link = jira_server_link
        self.jira_options = {"server": self.jira_server_link}

        if username == None:
            username = input("Username: ")
        if password == None:
            password = getpass()

        self.username = username
        self.password = password

        self._JIRA = JIRA(self.jira_options, basic_auth=(
            self.username, self.password))
        logging.info(
            f"Authenticated successfully with Jira with {self.username}")

    def create(self, data):
        """Create a single Jira ticket.

        args:
            data (dict): Fields required or needed to create the ticket.

        return (str): Ticket number / 'False' if fails
        """
        try:
            jira_ticket = self._JIRA.create_issue(fields=data)
            logging.info(
                f"Successfully created Jira issue '{jira_ticket.key}'")
            return jira_ticket.key

        except Exception as error:
            logging.debug(
                f"Failed to create Jira issue '{jira_ticket.key}'\n\n{error}\n\n")
            return False

    def link(self, issue_from, issue_to, issue_link_name=None):
        """Link two issues together. Defaults to 'Relates' unless issue_link_name is specified.

        args:
            issue_from (str): Issue that will be linked from.
            issue_to (str): Issue that will be linked to.


        kwargs:
            issue_link_name (str): issue link name that should be applied.

        return (bool): Will return 'True' if it completed successfully.
        """
        try:
            self._JIRA.create_issue_link(issue_link_name, issue_from, issue_to)
            logging.info(
                f"Successfully created a '{issue_link_name}' link between '{issue_from}' and '{issue_to}'.")
            return True

        except Exception as error:
            logging.debug(
                f"Failed to create a link between '{issue_from}' and '{issue_to}'\n\n{error}\n\n")
            return False

    def label(self, issue, labels):
        """Apply labels to a given issue.

        args:
            issue (str): Issue that labels will be applied to.
            labels (list): list of labels that should be applied to the issue.

        Return (bool): Will return 'True' if it completed successfully.
        """
        if type(labels) == list:
            try:
                issue_instance = self._JIRA.issue(issue)
                issue_instance.update(
                    fields={"labels": issue_instance.fields.labels + labels})
                logging.info(
                    f"Successfully added labels '{labels}' to '{issue}'")
                return True

            except Exception as error:
                logging.debug(
                    f"Failed to add labels '{labels}' to '{issue}'\n\n{error}\n\n")
                return False

        else:
            raise InputError('A list must be passed to the labels argument')

    def comment(self, issue, comment):
        """Apply a comment to a given issue.

         args:
             issue (str): Issue that comment will be applied to.
             comment (str): comment that should be applied to the issue.

         return (bool): Will return 'True' if it completed successfully.
         """
        try:
            self._JIRA.add_comment(issue, comment)
            logging.info(
                f"Successfully added comment '{comment}' to '{issue}'")
            return True
        except Exception as error:
            logging.debug(
                f"Failed to add comment '{comment}' to '{issue}'\n\n{error}\n\n")
            return False

    def log_work(self, issue, time_spent, comment=None):
        """Log work to a given issue.

        args:
            issue (str): Issue to log work.
            time_spent (str): Time that should be logged to the issue.

        kwargs:
            comment (str): Description of what this time represents.

        return (bool): Will return 'True' if it completed successfully.
        """
        try:
            if comment != None and type(comment) == str:
                self._JIRA.add_worklog(issue, time_spent, comment=comment)
            else:
                self._JIRA.add_worklog(issue, time_spent)
            logging.info(f"Successfully logged time to '{issue}'")
            return True

        except Exception as error:
            logging.info(
                f"Failed to log work to '{issue}' See debug logs for more.")
            logging.debug(f"\n{error}\n")
            return False

    def add_attachment(self, issue, attachment):
        """Attach file to Jira issue.

        args:
            issue (str): Issue name
            attachment (str): Location of file that should be attached.

        Return (bool): Will return 'True' if completed successfully
        """
        assert isinstance(issue, str)
        assert isinstance(attachment, str)

        try:
            self._JIRA.add_attachment(issue=issue, attachment=attachment)
            logging.info(f'Successfully attached document to "{issue}"')
            return True

        except Exception as error:
            logging.debug(
                f"Failed to attach document to '{issue}'\n\n{error}\n\n")
            return False

    def update_status(self, id, end_status, transfer_statuses=[], timeout_attempts=10):
        """Change issue to desired status.

        Due to the workflow features of Jira it might not be possible to transition
        directly to the wanted status, intermediary statuses might be required and
        this funcation allows for that using 'transfer_statuses'.

        args:
            id (str): Issue id for status update
            end_status (str): Name of status to update ticket to.

        kwargs:
            transfer_statuses (list): Ordered list of intermediary statuses
            timeout_attempts (num): Number of times before while loop times out.

        return (bool): Will return 'True' if completed successfully
        """
        while timeout_attempts != 0:
            transitions = self._JIRA.transitions(id)
            for transition in transitions:
                if transition['name'] == end_status:
                    jira_ticket = self._JIRA.transition_issue(
                        id, transition['id'])
                    logging.info(
                        f"Updated status of '{id}' to '{end_status}'")
                    return True
                elif transition['name'] in transfer_statuses:
                    jira_ticket = self._JIRA.transition_issue(
                        id, transition['id'])
            timeout_attempts -= 1
        logging.debug(
            f"Failed to update status of '{id}' to end_status ({end_status})")
        return False
