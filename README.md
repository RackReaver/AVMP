![logo](/logo.png?raw=true "logo")

# Vulcan

A collection of tools for managing and automating vulnerability management.

## Installation

Use the follow commands to get the application installed:

```
$ pip install https://github.com/RackReaver/Vulcan.git
```

## Deployment

Download the package using the above pip command then see documentation for implementation instructions

## How to use
```
>>> from vulcan.dbs.tenable_vuln_db import TenableVulnDB
>>> 
>>> tvd = TenableVulnDB('database.db')
>>> 
>>> tvd.add_ticket('INC-0001', '85023', 'In Progress', ['10.0.0.1', '10.0.0.2', '10.0.0.3'])
>>> True
>>> 
>>> tvd.update_ticket('INC-0001', 'Done')
>>> True
```

## TO-DO
* Write tests
* Build versioning system
* Connect to PyPi (dev and prod)

## Authors

* **Matt Ferreira** - *Developer* - [RackReaver](https://github.com/RackReaver)

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details
