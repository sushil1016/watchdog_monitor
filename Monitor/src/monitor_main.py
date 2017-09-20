import json
from datetime import datetime
import logging.config
from time import sleep

from interface.rule_engine.rule_engine import *
from interface.ph_proxy.ph_proxy import *
from interface.analyser.analyser import *
from interface.logs_db.logs_db import *
from db.cpe_status import *

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False

global STATUS_HTTP_OK
STATUS_HTTP_OK = 200

def shutdown_monitor(err_msg, db=""):
    logger.fatal("** Unrecoverable Error **, shutting down monitor=> " + str(err_msg))
    if "" != db:
        try:
            db.close_db()
        except AttributeError:
            logger.fatal("Incorrect object to close DB")
    exit()


def convert_str_to_class(in_str):  # Convert string to class
    try:
        key_obj = getattr(sys.modules[__name__], in_str)
    except AttributeError:
        logger.error("%s doesn't exist." + in_str)
        return 'error'
    try:
        if isinstance(key_obj, type):
            return key_obj
    except TypeError:
        logger.error("%s is not a class." + in_str)
        return 'error'


def time_since_last_req(last_processed_time):

    datetime_object = datetime.strptime(last_processed_time, '%Y-%m-%d %H:%M:%S')
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    now_obj= datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

    diff_time = abs((now_obj - datetime_object).days)
    logger.info("Time since last query to PH= " + str(diff_time) + "Days")
    return diff_time

'''
sampling data set can be a list of dictionaries. example
[{'from_date': 121212, 'to_date': 87878, 'error': 1016}, {'from_date': 234444, 'to_date': 121212, 'error': 5666}]
'''


def process_sampling(cpe_id, sampling_data, logdb, r_engine, analyser, status_db):
    logger.debug("** Processing sampling use cases **")
    data = dict()
    data["cpeId"] = cpe_id
    data["project"] = _project
    data["jobMap"] = []
    err_list = []  # OSD list for book-keeping

    for item in sampling_data:
        indexes = logdb.get_indexes(cpe_id, item["from_date"], item["to_date"])
        use_cases = r_engine.get_cpe_usecases(item["error"])
        if indexes and use_cases:
            data["jobMap"].append({
                "index": indexes,
                "useCase": use_cases,
                "error": item["error"]
            })
            err_list.append(item["error"])
        else:
            logger.error("usecases/indexes not found for error_code " + str(item["error"]))
            break

    if data["jobMap"]:
        analyser.add_job_to_analyser(json.loads(data))
        status_db.update_cpe_state(cpe_id, "Processed", err_list)
    else:
        logger.error("No job map to add job")


def process_cpe(cpe_id, r_engine, logdb, analyser, agent, status_db):
    # Check the status of this CPE in state machine
    cpe_exist = status_db.is_cpe_processed(cpe_id)
    processed_date = 0
    db_osd_list = []

    if not cpe_exist:
        # if the cpe doesn't exists in DB, add it with a "" OSD and current processing time
        if not status_db.add_cpe_state(cpe_id, "Pending"):
            logger.fatal("Error while inserting cpe details to DB")
            shutdown_monitor('INSERT failed', status_db)
    else:
        status, processed_date, db_osd_list = status_db.get_cpe_info(cpe_id)
        logger.info("status= " + str(status) + " processed_date= " + str(processed_date)
                    + " db_osd_list= " + str(db_osd_list))

    if 0 != processed_date:
        # Calculate the daysBack parameter from here.
        days_back = time_since_last_req(processed_date)
        if days_back >= 0:#TODO testing only
            has_error, errors_from_server, error_timestamp_map = agent.get_err_timestamp_map(cpe_id, days_back)
            if has_error:
                logger.fatal("Error in OSD response")
                return
                # shutdown_monitor("error while fetching osd list", status_db)
        else:
            logger.info("This cpe was already processed today " + str(cpe_id))
            return
    else:  # Being processed for the first time
        has_error, errors_from_server, error_timestamp_map = agent.get_err_timestamp_map(cpe_id)
        if has_error:
            logger.fatal("Error in OSD response")
            return
            # shutdown_monitor("error while fetching osd list", status_db)

    if not error_timestamp_map:
        '''if general_uc_supported:
            #TODO use case to be decided
            #analyser.add_job_to_analyser(cpe_id, 'UC-General')
            #status_db.update_cpe_state(cpe_id, "Processed")
            #return
           else:
            status_db.update_cpe_state(cpe_id, "Pending")
            return
            '''
    else:
        if not error_timestamp_map:
            logger.info("after merging the osd lists, new osd list is empty")
            status_db.update_cpe_state(cpe_id, "Pending")
            return
        else:
            has_error, errors_from_server, sampling_data = r_engine.get_cpe_rules(cpe_id, errors_from_server)
            if has_error:
                logger.fatal("Error in rules response")
                return
                # shutdown_monitor("error fetching cpe sampling rules from server", status_db)

            if sampling_data:
                process_sampling(cpe_id, sampling_data, logdb, r_engine, analyser)
            # Process remaining osd's after sampling usecase is added to analyser.

            if errors_from_server:
                data = dict()
                data["cpeId"] = cpe_id
                data["project"] = _project
                data["jobMap"] = []
                for err_code in errors_from_server:
                    indexes = logdb.get_indexes(cpe_id, error_timestamp_map[err_code])
                    has_error, use_cases = r_engine.get_cpe_usecases(cpe_id, err_code)
                    if has_error:
                        logger.fatal("error fetching cpe use cases from server")
                        return
                        # shutdown_monitor("error fetching cpe use cases from server", status_db)
                    if indexes and use_cases:
                        data["jobMap"].append({
                            "index": indexes,
                            "useCase": use_cases,
                            "error": err_code
                        })
                    else:
                        logger.error("usecases/indexes not found for error_code " + str(err_code))
                        continue  # Process another error code
                if data["jobMap"]:
                    analyser.add_job_to_analyser(json.dumps(data))
                    status_db.update_cpe_state(cpe_id, "Processed", errors_from_server)
                else:
                    logger.error("No job map to add job")
                return


def monitor_main():
    logger.info("monitor_main")

    # READ LOCAL CONFIGURATION SETTINGS
    try:
        with open("monitor.json") as jsonfile:
            config=json.load(jsonfile)
    except:
        raise IOError('Monitor Config file does not exists')
    try:
        for key, value in config['RULE_ENGINE'].items():
            logger.info(key + ',' + value + "\n")
            if 'rule_engine_uri' == key:
                rule_engine_uri=value
            elif 'rule_engine_port' == key:
                rule_engine_port=value
            else:
                logger.fatal("Check monitor configuration")
                shutdown_monitor('required parameters missing from cfg file')
    except KeyError:
        logger.fatal("Key not found")
        shutdown_monitor('KeyError: RULE_ENGINE not found in cfg')

    # INIT RULE ENGINE
    try:
        # Rule Engine All startup details to invoke the monitor. Get the project specific properties from rules engine
        r_engine = RulesEngine(rule_engine_uri, rule_engine_port)
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class RulesEngine()")

    # READ CONFIG INFO FROM RULE ENGINE
    try:
        has_error, json_config = r_engine.get_configuration()
    except AttributeError:
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class RulesEngine()")

    if has_error:
        shutdown_monitor("An error occurred with class configuration()")

    try:
        global _project
        _project = json_config["project"]
        alert_agent = json_config['alertType']
        # agent can be any interface which is responsible to respond with OSD or Error Codes, based upon project
        agent_cls = convert_str_to_class(alert_agent)
        if 'error' == agent_cls:
            logger.error("Can't convert str to class" + str(alert_agent))
            shutdown_monitor("Can't convert str to class")

        for item in json_config["serverMap"]:
            if "logsdb" == item["serverType"]:
                try:
                    logdb = LogsDB(item["hostname"], item["serverVersion"])
                except(RuntimeError, TypeError, NameError):
                    shutdown_monitor("An exception occurred with class LogsDB()")
            if 'analyser' == item["serverType"]:
                try:
                    analyser = Analyser(item['hostname'], item['serverVersion'], _project)
                except(RuntimeError, TypeError, NameError):
                    logger.error("An exception occurred")
                    shutdown_monitor("An exception occurred with class Analyser()")
            if alert_agent == item["serverType"]:
                # INIT OSD SERVER INTERFACE
                try:
                    agent = agent_cls(item["hostname"], item["serverVersion"], item["user"], item["password"])
                except(RuntimeError, TypeError, NameError):
                    logger.error("An exception occurred")
                    shutdown_monitor("An exception occurred with class agent class()")
    except:
        shutdown_monitor("an error occurred while reading json CONFIGURATION object")

    # INIT CPE STATE DATABASE
    # status db holds the cpe processing state and time
    try:
        status_db = CPEStatus()
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class CPEStatus()")
    while True:  # TODO, to define this better once rule engine is up
        cpe_id_list = []
        try:
            has_error, cpe_id_list = r_engine.get_cpe_ids()
        except (AttributeError, TypeError):
            shutdown_monitor("AttributeError/TypeError with get_cpe_ids")

        if has_error:
            shutdown_monitor("An error occurred with cpe id response")

        if not cpe_id_list:
            logger.error("RuleDB is not loaded with CPE IDS, Trying again")
            sleep(10)
            continue
        for cpe_id in cpe_id_list:
            logger.info("Processing CPE_ID  " + str(cpe_id))
            process_cpe(cpe_id, r_engine, logdb, analyser, agent, status_db)
        logger.info("All CPE's are processed, checking if any new CPE is added in rules engine")
        sleep(6)


if __name__ == '__main__':
    # Starting the monitor here
    logger.info("****** Monitor Init *******")
    monitor_main()
