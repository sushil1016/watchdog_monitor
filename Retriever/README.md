## Set-top Box Health Monitor

STB Health Monitor is an automated system to monitor the health of STB's installed in the field in the least intrusive way. It can generate an automatic alert system, which can detect anomalies in the logs and anticipate failures, remedies resulting great reduction in the feedback loop between field and Engineering teams.


### Retriever Module

Log Retriever is a component responsible for connecting to log server per project specification and retrieve logs periodically. The periodicity shall be configured in Rules Engine. As per the rules, Retriever may choose to decode the diag log retrieved from the project specific log server. Once a decoded log is available at Retriever it shall do first level parsing using the log stash and output the same to Master Logs DB. Optionally Retriever might do a clean up of logs from Master Logs DB based on rules retrieved by Rules Engine.


#### Prerequisites

* Linux (Ubuntu/ Redhat) 
* Python 2.7 or Above


#### Installing Dependencies

```
 cd Retriever
 apt-get install python-pip
 pip install -r dependencies.txt
 
```

#### Code Directory Structure

'''
.
|-- dependencies.txt
|-- logs
|-- README.md
`-- src
    |-- config.cfg
    |-- db
    |   |-- __init__.py
    |   `-- PickleData.py
    |-- Decoder
    |   |-- config.cfg
    |   |-- Decoder.py
    |   |-- __init__.py
    |   `-- test.py
    |-- __init__.py
    |-- interface
    |   |-- buildserver
    |   |   |-- BuildServer.py
    |   |   `-- __init__.py
    |   |-- ftp
    |   |   |-- ftplogserver.py
    |   |   `-- __init__.py
    |   |-- __init__.py
    |   |-- ruleengine
    |   |   |-- __init__.py
    |   |   `-- RulesEngineClient.py
    |   `-- yard
    |       |-- __init__.py
    |       |-- yard.cfg
    |       `-- yardlogserver.py
    |-- logger.conf
    |-- retriever_main.py
    `-- util
        |-- __init__.py
        `-- Utility.py

'''

#### Starting Retriever
modify rule_engine_uri and port in config.cfg
This should be the server ip where rule engine is running
[Retriever]
RulesEngine = http://localhost:3000<-- change ip and port here
enable_logstash = no <-- this will not start logstash, make it yes to start logstash
Also change the corresponding configs like yard,ftp for the log path, logstash config etc


```
cd Retriever\src
python retriever_main.py

```

#### TODO

* Extensive error handling
* Cleanup of logstash parsed logs
* Connection as a base class
* Run as a service
* Code cleanup and optimization
* More Pythonic Way

#### Change LOG

* draft v1.2

#### Known Bugs

* shutil.copytree sometimes doesn't copy last file of last dir
 
