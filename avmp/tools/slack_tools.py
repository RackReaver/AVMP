"""Python tools for package.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import json

import requests


class SlackTools:
    def __init__(self):
        pass

    @staticmethod
    def push_alert(webhook_url, message, channel=None, custom_payload=None):
        """Push an alert to slack channel given a webhooks url and message.

        args:
            webhook_url (str): Incoming Webhook provided by slack.
            message (str): Message to push via webhook.
        kwargs:
            channel (str): Allow messages to be sent to any public channel.
            custom_payload (json): Overwrites message and channel inputs.
        """
        if custom_payload == None:
            if channel != None:
                payload = {
                    "channel": channel,
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": message}}
                    ],
                }
            else:
                payload = {
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": message}}
                    ]
                }

        r = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        return r
