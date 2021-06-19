![Alt text](logo.png?raw=true "logo")

# Automated Vulnerability Management Program (AVMP)

A collection of tools for managing and automating vulnerability management.

Streamline the way vulnerability management programs are created and run. This project is made to be modular so automation can be put into place at any program level.

## Things to Note

1. **API keys for both Tenable IO and Jira are required.**

2. I developed this tool using Jira on-prem and assume it would work for the cloud version as well however am unable to verify that.

3. There is a bit of setup to use the tool as it is in development, I am planning on creating a quick start script but until then please see [How to use](#how-to-use).

## Installation

This tool is still being actively developed and does not have a version 1 at this time.

## Running the tests

Check code coverage

```
>>> coverage run -m pytest
>>>
>>> coverage report
```

## Deployment

At this time the tool can only be deployed locally.

## How to use

```
$ avmp --help
AVMP command-line app.

Usage:
    avmp run [--config filepath] <process_config>
    avmp update [--config filepath] <ticket_db_filepath>
    avmp -h | --help
    avmp --version

Options:
    -h --help           Show this screen.
    --version           Show version.
    --config=filepath   AVMP configuration file [default: config.json]
```

#### Folder Structure `vuln_manager`:

```
vuln_manager
|
+-- process_configs
|  |
|  +-- dynamic/     # Configurations for generating vulnerability tickets
|  +-- static/      # Configurations for generating repatitive project/task tickets
|
+-- config.json
+-- tickets.db      # This is generated automatically and is mapped to in the process_configs
```

#### Main configuration file `config.json`:

```json
{
    "creds": {
        "tenable": {
            "access_key": "",
            "secret_key": ""
        },
        "jira": {
            "server": "",
            "username": "",
            "password": ""
        }
    },
    "types": {
        "JIRA_PROJECT_ID": ["JIRA_FIELD_1", "JIRA_FIELD_2", "JIRA_FIELD_3"]
    },
    "due_dates": {
        "Critical": "DAYS_TO_PATCH",
        "High": "DAYS_TO_PATCH",
        "Medium": "DAYS_TO_PATCH",
        "Low": "DAYS_TO_PATCH",
    },
    "priorities": {
        "Critical": "JIRA_ID",
        "High": "JIRA_ID",
        "Medium": "JIRA_ID",
        "Low": "JIRA_ID"
}
```

| Field      | Required | Description                                                                                                                                                          |
| ---------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creds      | yes      | Data required from APIs to run package                                                                                                                               |
| types      | no       | List of required fields for a given Jira project (not required, but a good idea to ensure process_configs contain all required fields before making an API request). |
| due_dates  | yes      | Used to set Jira due date based on Tenable's severity rating.                                                                                                        |
| priorities | yes      | Mapping Tenable severity rating to Jira priorities (defaults to `Low` if others are unavailable).                                                                    |

#### Dynamic process config `dynamic_process_config.json`:

```json
{
  "process_type": "dynamic",
  "allow_ticket_duplication": "False",
  "scan_name": "TENABLE_SCAN_NAME",
  "max_tickets": 10,
  "assignee": "",
  "min_cvss_score": 6.0,
  "ticket_db_filepath": "tickets.db",
  "default_ticket_status": "Open",
  "time_saved_per_ticket": "10m",
  "root_ticket": "",
  "comments": [],
  "data": {
    "project": { "key": "JIRA_PROJECT_KEY" },
    "summary": "Vuln: ",
    "description": "",
    "issuetype": { "id": "JIRA_ISSUE_TYPE_ID" },
    "priority": { "id": "" },
    "duedate": ""
  }
}
```

| Field                    | Required | Description                                                                                                                        |
| ------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| process_type             | yes      | Must be `dynamic`                                                                                                                  |
| allow_ticket_duplication | no       | [default: false] Prevent multiple tickets for same plugin_id to be generated (This is based on the `ticket_db_filepath` provided). |
| scan_name                | yes      | Name of scan inside of Tenable IO                                                                                                  |
| max_tickets              | no       | Number of tickets to be created each time this configuration is used (optional - will create all if value is blank).               |
| assignee                 | no       | Username to assign all created tickets to (optional).                                                                              |
| min_cvss_score           | yes      | This is based on the CVSS Base Score provided by Tenable IO, allows for configurations based on severity.                          |
| ticket_db_filepath       | yes      | Location of SQLite database file for tracking tickets (DB will be created if ones doesn't already exist on the path provided).     |
| default_ticket_status    | yes      | First status for database entry, this will change when the auto updater is run.                                                    |
| time_saved_per_ticket    | yes      | Jira time value to log work for calculating time saved.                                                                            |
| root_ticket              | no       | If unable to log work against newly created ticket this value will provide a ticket that allows work to be logged against it.      |
| comments                 | no       | A list of strings that will generate comments.                                                                                     |
| data                     | yes      | API values required to generate a Jira ticket (issue).                                                                             |

#### Static process config `static_process_config.json`:

```json
{
  "process_type": "static",
  "time_saved_per_ticket": "5m",
  "time_saved_comment": "Time saved through automation",
  "parent_ticket": {
    "project": { "key": "JIRA_PROJECT_KEY" },
    "summary": "SUMMARY",
    "description": "DESCRIPTION",
    "issuetype": { "name": "ISSUE_TYPE_NAME" },
    "assignee": { "name": "" },
    "priority": { "id": "PRIORITY_ID" }
  },
  "sub_tasks": {
    "sub_task_1": {
      "project": { "key": "JIRA_PROJECT_KEY" },
      "summary": "SUMMARY",
      "description": "DESCRIPTION",
      "issuetype": { "name": "Sub-task" },
      "assignee": { "name": "" }
    },
    "sub_task_2": {
      "project": { "key": "JIRA_PROJECT_KEY" },
      "summary": "SUMMARY",
      "description": "DESCRIPTION",
      "issuetype": { "name": "Sub-task" },
      "assignee": { "name": "" }
    }
  }
}
```

| Field Name            | Required | Description                                                                  |
| --------------------- | -------- | ---------------------------------------------------------------------------- |
| process_name          | yes      | Must be `static`                                                             |
| time_saved_per_ticket | no       | Jira time value to log work for calculating time saved.                      |
| time_saved_comment    | no       | Comment for Jira work log for time saved.                                    |
| parent_ticket         | yes      | API values required to generate a Jira ticket (issue).                       |
| sub_tasks             | no       | JSON container for any sub tasks that should be created under parent ticket. |

## TO-DO

- ~~Build command line utility~~
- Add persistent logging to wrapper.main() as a return value
- ~~Build usage/how to use documentation for README.md~~
- ~~Add documentation for dynamic process_config's to README.md~~
- ~~Add static process_config example to README.md~~
- Add ticket reference table to database
  - Track project and process ticket numbers for automated linking
- Add support for [SecurityScorecard](https://securityscorecard.com/)
- Build tests for code base

## Authors

- **Matt Ferreira** - _Developer_ - [RackReaver](https://github.com/RackReaver)

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details
