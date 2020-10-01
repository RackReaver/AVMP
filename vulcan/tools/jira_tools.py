import socket
import logging
from getpass import getpass
from jira import jira


class ScriptError(Exception):
    pass


class JiraToolsAPI:
    def __init__(self, jira_server_link, username=None, password=None):
        """Initalizes the JiraTicket class. If username or password is not provided you will be prompted for it.

        args:
            jira_server_link (str): Link to the Jira server to touch API

        kwargs:
            username (str): This can be used to pass a username instead of using the default username prompt.
            password (str): This can be used to pass a password instead of using the default password prompt.
        """
        self.jira_server_link = jira_server_link
        self.jira_options = {
            "server": self.jira_server_link
        }
        if username == None:
            self.username = input('Username: ')
        else:
            self.username = username
        if password == None:
            self.password = getpass()
        else:
            self.password = password

        self._JIRA = JIRA(self.jira_options, basic_auth=(
            self.username, self.password))
        logging.info('{} used "{}" to authenticate successfully with Jira'.format(
            socket.gethostname(), self.username))

    def create_issue(self, data):
        """This creates a single Jira ticket and has no other functionality.

        args:
            data (dict): Fields required or needed to create the ticket.

        Return (str): Ticket Number
        """
        jira_ticket = self._JIRA.create_issue(fields=data)
        logging.info('{} used "{}" to create a ticket "{}" successfully in Jira'.format(
            socket.gethostname(), self.username, jira_ticket.key))

        return jira_ticket.key

    def link_two_issues(self, issue_from, issue_to, issue_link_name=None):
        """Links two issues together. Defaults to 'Relates' unless issue_link_name is specified.

        args:
            issue_from (str): Issue that will be linked from.
            issue_to (str): Issue that will be linked to.


        kwargs:
            issue_link_name (str): issue link name that should be applied.

        Return (bool): Will return 'True' if it completed successfully.
        """
        self._JIRA.create_issue_link(issue_link_name, issue_from, issue_to)
        logging.info('{} used "{}" to create a "{}" link between "{}" and "{}" successfully in Jira'.format(
            socket.gethostname(), self.username, issue_link_name, issue_from, issue_to))

        return True

    def apply_label_to_issue(self, issue, labels):
        """This will apply a label or labels to a given issue.

        args:
            issue (str): Issue that labels will be applied to.
            labels (list): list of labels that should be applied to the issue.

        Return (bool): Will return 'True' if it completed successfully.
        """
        if type(labels) == list:
            issue_instance = self._JIRA.issue(issue)
            issue_instance.update(
                fields={"labels": issue_instance.fields.labels + labels})

            return True
        else:
            raise ScriptError(
                'A list must be passed to the labels argument')

    def apply_comment_to_issue(self, issue, comment):
        """This will apply a comment to a given issue.

        args:
            issue (str): Issue that labels will be applied to.
            comment (str): comment that should be applied to the issue.

        Return (bool): Will return 'True' if it completed successfully.
        """
        self._JIRA.add_comment(issue, comment)

        return True

    def log_work_to_issue(self, issue, time_spent, comment=None):
        """This will log work to a given issue.

        args:
            issue (str): Issue that labels will be applied to.
            time_spent (str): Time that should be logged to the issue.

        param:
            comment (str): Description of what this time represents.

        Return (bool): Will return 'True' if it completed successfully.
        """
        try:
            if comment != None and type(comment) == str:
                self._JIRA.add_worklog(issue, time_spent, comment=comment)
            else:
                self._JIRA.add_worklog(issue, time_spent)
        except:
            return False
        finally:
            return True

    def search_issue(self, id):
        return self._JIRA.issue(id)

    def jira_search(self, jql_search_string, maxResults=None):
        """Returns ticket numbers for a given search string.

        args:
            jql_search_string (str): Jira JQL search string.

        kwargs:
            maxResults (num) default:None : Number of results to return.

        Return (list): List of jira issue classes.
        """
        if maxResults != None:
            results = self._JIRA.search_issues(
                jql_search_string, maxResults=maxResults)
        else:
            results = self._JIRA.search_issues(jql_search_string)

        tickets = []

        return results

    def ticket_parser(self, data, regex=None, text=None):
        # TODO: Create parser to check all ticket values for regex values or text
        pass
