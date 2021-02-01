![Alt text](logo.png?raw=true "logo")

# Automated Vulnerability Management Program (AVMP)

A collection of tools for managing and automating vulnerability management.

## Getting Started

Streamline the way vulnerability management programs are created and run. This project is made to be modular so automation can be put into place at any program level.

## Installation TBA

This package is available on [PyPi](https://pypi.org) and can be installed with the following command:

```
$ pip install <project_name>
```

## Running the tests

TBA

### Break down into end to end tests

TBA

```
TBA
```

## Deployment

At this time the tool can only be deployed locally.

## How to use
```
>>> from avmp.core import wrapper
>>> 
>>> config = {
>>>     "creds": {
>>>         "tenable": {
>>>             "access_key": "",
>>>             "secret_key": ""
>>>         },
>>>         "jira": {
>>>             "server": "",
>>>             "api_username": "",
>>>             "api_password": ""
>>>         }
>>>     },
>>>     "types": {
>>>         "JIRA_PROJECT_ID": ["JIRA_FIELD_1", "JIRA_FIELD_2", "JIRA_FIELD_3"]
>>>     },
>>>     "due_dates": {
>>>         "Critical": "DAYS_TO_PATCH",
>>>         "High": "DAYS_TO_PATCH",
>>>         "Medium": "DAYS_TO_PATCH",
>>>         "Low": "DAYS_TO_PATCH",
>>>     },
>>>     "priorities": {
>>>         "Critical": "JIRA_ID",
>>>         "Highest": "JIRA_ID",
>>>         "High": "JIRA_ID",
>>>         "Medium": "JIRA_ID",
>>>         "Low": "JIRA_ID",
>>>         "Lowest": "JIRA_ID",
>>>     }
>>> 
>>> scan_config = {
>>>     "scan_name": "TENABLE_SCAN_NAME",
>>>     "max_tickets": 10,
>>>     "assignee": "",
>>>     "min_cvss_score": 6.0,
>>>     "ticket_db_filepath": "tickets.db",
>>>     "default_ticket_status": "Open",
>>>     "time_saved_per_ticket": "10m",
>>>     "root_ticket": "",
>>>     "comments": [],
>>>     "data": {
>>>         "project": {"key": "JIRA_PROJECT_KEY"},
>>>         "summary": "Vuln: ",
>>>         "description": "",
>>>         "issuetype": {"id": "JIRA_ISSUE_TYPE_ID"},
>>>         "priority": {"id": ""},
>>>         "duedate": ""
>>>     }
>>>     
>>> }
>>> 
>>> wrapper.main(config, scan_config)
>>> 
```

## TO-DO
* Fix IP duplication in vuln_db
* Build command line utility

## Authors

* **Matt Ferreira** - *Developer* - [RackReaver](https://github.com/RackReaver)

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details