## Set-top Box Health Monitor

STB Health Monitor is an automated system to monitor the health of STB's installed in the field in the least intrusive way. It can generate an automatic alert system, which can detect anomalies in the logs and anticipate failures, remedies resulting great reduction in the feedback loop between field and Engineering teams.


### Watchdog Monitor

Monitor component is a part of STB Health Monitor which is responsible for interfacing with Prime Home, Alerter or any other Error-Reporting system to find any unusual activities per CPE. The Monitor shall interface with Rule Engine to retrieve the CPE ID to be monitored and make a connection with Prime Home or Alerter to get the OSD raised since the last request made. All the required data is sterilized in a json object and is passed to Analyser module for further processing


#### Prerequisites

* Linux (Ubuntu/ Redhat) 
* Python 2.7 or Above
* SQLite 3.0 or Above


#### Installing Dependencies

```
 cd Monitor/
 apt-get install python-pip
 pip install -r dependencies.txt
 
```

#### Code Directory Structure

```
.
`-- Monitor
    |-- dependency.txt
    |-- logs
    |   `-- monitor.log <Generated once application is started>
    |-- README.md
    |-- src
    |   |-- db
    |   |   |-- cpe-status.db <Generated once db-interface is initilized>
    |   |   |-- cpe_status.py
    |   |   `-- __init__.py
    |   |-- __init__.py
    |   |-- interface
    |   |   |-- analyser
    |   |   |   |-- analyser.py
    |   |   |   `-- __init__.py
    |   |   |-- http_request.py
    |   |   |-- __init__.py
    |   |   |-- logs_db
    |   |   |   |-- __init__.py
    |   |   |   `-- logs_db.py
    |   |   |-- ph_proxy
    |   |   |   |-- __init__.py
    |   |   |   |-- ph.cfg
    |   |   |   `-- ph_proxy.py
    |   |   `-- rule_engine
    |   |       |-- __init__.py
    |   |       |-- rule_engine.cfg
    |   |       `-- rule_engine.py
    |   |-- logger.conf
    |   |-- monitor.json
    |   `-- monitor_main.py
    `-- unit_tests
        `-- test_rules_engine.py

 
```


#### Starting Monitor
modify rule_engine_uri and port in monitor.json
This should be the server ip where rule engineis running
{
  "RULE_ENGINE": {
    "rule_engine_uri": "http://0.0.0.0",
    "rule_engine_port": "0000"
  },
```
cd Monitor/src
python monitor_main.py

```

#### TODO

* Remaining Use Cases
* Extensive error handling
* Run as a service
* Code cleanup and optimization
* More Pythonic Way
* More OOPs

#### Change LOG

* first draft v0.1

#### Known Bugs

* N/A
