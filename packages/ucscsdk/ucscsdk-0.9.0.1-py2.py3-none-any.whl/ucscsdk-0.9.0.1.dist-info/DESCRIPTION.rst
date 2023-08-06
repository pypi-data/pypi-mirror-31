[![](https://ucspython.herokuapp.com/badge.svg)](https://ucspython.herokuapp.com)

# Python SDK for Cisco UCS Central

* Apache License, Version 2.0 (the "License")

## Installation

### From github:

Installs the latest top of the tree development version,

```
    # Install pip (skip if pip is already available):
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py

    git clone https://github.com/CiscoUcs/ucscsdk.git
    cd ucscsdk
    make install
```

### From pip

```
    pip install ucscsdk
```

## Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)




History
-------

0.9.0.1 (2018-04-26)
---------------------

* Support UCS Central release 2.0(1d)
* Adding test infra with parameters from config file to be used for sanity
* Fix for the issue where None values are compared for validation of property


0.9.0.0 (2016-11-14)
---------------------

* Python SDK for UCS Central management and related automation
* Supports every Managed Object exposed by UCS Central
* APIs for CRUD operations
* Support for UCS Central and domain backup, export/import configuration
* Support for firmware management and tech-support
* Support for UCS Domain management
* Support for server side filters
* Support for UCS Central eventhandlers
* Logging support
* Nosetests for unit testing
* Integrating the sphinx framework for documentation
* PEP8 Compliance


