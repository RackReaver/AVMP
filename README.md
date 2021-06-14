![Alt text](logo.png?raw=true "logo")

# Automated Vulnerability Management Program (AVMP)

A collection of tools for managing and automating vulnerability management.

Streamline the way vulnerability management programs are created and run. This project is made to be modular so automation can be put into place at any program level.

---

## Things to Note

1. **API keys for both Tenable IO and Jira are required.**

2. I developed this tool using Jira on-prem and assume it would work for the cloud version as well however am unable to verify that.

3. There is a bit of setup to use the tool as it is in development, I am planning on creating a quick start script but until then please see [How to use](#how-to-use).

---

## Installation

This tool is still being actively developed and does not have a version 1 at this time.

---

## Running the tests

Check code coverage

```
>>> coverage run -m pytest
>>>
>>> coverage report
```

---

## Deployment

At this time the tool can only be deployed locally.

---

## How to use

Folder Structure `vuln_manager`:

```
vuln_manager
|
+-- process_configs
|  |
|  +-- dynamic/     # Configurations for generating vulnerability tickets
|  +-- static/      # Configurations for generating repatitive project/task tickets
|
+-- config.json
+-- run.py
```

Main configuration file `config.json`:

- "creds": Data required from APIs to run package
- "types": List of required fields for a given Jira project (not required, but a good idea to ensure process_configs contain all required fields before making an API request).
- "due_dates": Used to set Jira due date based on Tenable's severity rating.
- "priorities": Mapping Tenable severity rating to Jira priorities (defaults to `Low` if others are unavailable).

```
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

Dynamic process config `tenable_scan.config`:

```
>>>
>>> # process_type dynamic generates tickets directly from Tenable.
>>> process_config = {
>>>     "process_type": "dynamic",
>>>     "allow_ticket_duplication": "False",
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
```

Runtime `run.py`:

```
from avmp.core import wrapper

if len(sys.argv) == 2:
    with open('config.json', 'r') as openFile:
        config = json.load(openFile)
    with open(sys.argv[1], 'r') as openFile:
        process_config = json.load(openFile)

    wrapper.main(config, process_config)

else:
    print('Please provide filepath for process config file.')
```

## TO-DO

- Build command line utility
- Add persistent logging to wrapper.main() as a return value
- Build usage/how to use documentation for README.md
- Add documentation for dynamic process_config's to README.md
- Add static process_config example to README.md

## Authors

- **Matt Ferreira** - _Developer_ - [RackReaver](https://github.com/RackReaver)

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details
