"""Class models for AVMP.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

import os
import logging

from avmp.utils.logging_utils import logging_setup
from avmp.tools.tenable_tools import TenableToolsAPI
from avmp.tools.jira_tools import JiraToolsAPI
from avmp.core.exceptions import MissingConfiguration


class App():
    """Data associated with running AVMP.
    """

    def __init__(self, config, process_config):
        """Build AVMP app given the config file.

        args:
            config (dict): Imported json data from config
            scan_config (dict): Imported json data from scan_config

        return: None
        """
        assert isinstance(config, dict)
        assert isinstance(process_config, dict)

        self.config = self.config_setup(config)
        self.process_config = self.process_config_setup(process_config)

    def config_setup(self, config):
        """Setup function for config file. Used to process/add missing information.

        args:
            config (dict): AVMP configuration file

        return (dict): Modified python config dictionary
        """

        return config

    def process_config_setup(self, process_config):
        """Setup function for process config file. Used to process/add missing information.

        args:
            config (dict): Process configuration file

        return (dict): Modified python process config dictionary
        """

        if "allow_ticket_duplication" not in process_config:
            process_config['allow_ticket_duplication'] = False

        return process_config

    def tenAPIcon(self):
        """Check for credentials in config and connect to Tenable IO.
        """
        if 'access_key' in self.config['creds']['tenable'] and 'secret_key' in self.config['creds']['tenable']:

            self.tenAPI = TenableToolsAPI(self.config['creds']['tenable']['access_key'],
                                          self.config['creds']['tenable']['secret_key'])
        else:
            message = 'Tenable access_key and secret_key are required and must be provided in the config file.'
            logging.critical(message)
            raise MissingConfiguration(message)

    def jiraAPIcon(self):
        """Check for credentials in config and connect to Jira.
        """

        if 'server' in self.config['creds']['jira'] and 'username' in self.config['creds']['jira'] and 'password' in self.config['creds']['jira']:

            self.jiraAPI = JiraToolsAPI(self.config['creds']['jira']['server'],
                                        username=self.config['creds']['jira']['username'],
                                        password=self.config['creds']['jira']['password'])
        else:
            message = 'Jira server, username and password are required and must be provided in the config file.'
            logging.critical(message)
            raise MissingConfiguration(message)


if __name__ == '__main__':
    import json
    config_location = 'avmp/test_data/config.json'
    config = json.load(open(config_location, 'r'))

    app = App(config).jiraAPI()
