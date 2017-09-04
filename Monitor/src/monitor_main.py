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


def process_cpe(cpe_id, logdb, general_uc_supported, analyser, agent, status_db):
    # Check the status of this CPE in state machine
    # TODO: Sampling use case and OSD mapping
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
        logger.info("status= " + str(status) + " processed_date= " + str(processed_date) + " db_osd_list= " + str(db_osd_list))

    db_has_logs = logdb.master_db_has_logs(cpe_id, processed_date)
    if db_has_logs:
        if 0 != processed_date:
            # Calculate the daysBack parameter from here.
            days_back = time_since_last_req(processed_date)
            if days_back >= 1:
                server_osd_list = agent.get_osd_messages(cpe_id, days_back)
            else:
                return
        else:
            server_osd_list = agent.get_osd_messages(cpe_id)
        if not server_osd_list:
            if general_uc_supported:
                analyser.add_job_to_analyser(cpe_id, 'UC-General')
                status_db.update_cpe_state(cpe_id, "Processed")
                return
            else:
                status_db.update_cpe_state(cpe_id, "Pending")
                return
        else:
            if not db_osd_list:
                new_osd_list = server_osd_list
            else:
                logger.info(" server_osd_list= "+str(server_osd_list)+" db_osd_list= "+str(db_osd_list))
                new_osd_list = list((set(server_osd_list).difference(db_osd_list)))
                logger.info("difference in osd list(server) and osd_list(db) is " + str(new_osd_list))

            if not new_osd_list:
                logger.info("after merging the osd lists, new osd list is empty")
                status_db.update_cpe_state(cpe_id, "Pending")
                return
            else:
                analyser.add_job_to_analyser(cpe_id, new_osd_list)
                status_db.update_cpe_state(cpe_id, "Processed", new_osd_list)
                return
    else:
        status_db.update_cpe_state(cpe_id, "Pending")
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

    # READ INFO FROM RULE ENGINE
    logdb_uri = r_engine.get_logs_db_uri()
    try:
        logdb_uri = r_engine.get_logs_db_uri()
    except (AttributeError,TypeError):
        shutdown_monitor("AttributeError/TypeError with get_logs_db_uri")
    if 'error' == logdb_uri:
        shutdown_monitor("logdb uri not found")

    try:
        general_uc_supported = r_engine.is_general_uc_supported()
    except (AttributeError, TypeError):
        shutdown_monitor("AttributeError/TypeError with is_general_uc_supported")

    try:
        analyser_uri = r_engine.get_analyser_uri()
    except (AttributeError,TypeError):
        shutdown_monitor("AttributeError/TypeError with get_analyser_uri")
    if 'error' == analyser_uri:
        shutdown_monitor("analyser uri not found")

    try:
        agent_uri = r_engine.get_proxy_agent_uri()  # Retrieve PH/Alerter URI with port
    except (AttributeError,TypeError):
        shutdown_monitor("AttributeError/TypeError with get_proxy_agent_uri")
    if 'error' == agent_uri:
        shutdown_monitor("agent uri not found")

    try:
        i_face = r_engine.get_proxy_agent_name()
    except (AttributeError,TypeError):
        shutdown_monitor("AttributeError/TypeError with get_proxy_agent_name")
    if 'error' == i_face:
        shutdown_monitor("interface to retrieve OSD is not found")

    try:
        cpe_id_list = r_engine.get_cpe_ids()
    except (AttributeError,TypeError):
        shutdown_monitor("AttributeError/TypeError with get_cpe_ids")
    if not cpe_id_list:
        shutdown_monitor("RuleDB is not loaded with CPE IDS")

    # INIT LOGS DB
    # logdb is the master DB which holds all the logs as documents after first level processing
    try:
        logdb = LogsDB(logdb_uri)
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class LogsDB()")

    # INIT RABBITMQ/ANALYSER INTERFACE
    # analyser is RabbitMQ queue where jobs can be posted for further processing
    try:
        analyser = Analyser(analyser_uri)
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class Analyser()")

    # agent can be any interface which is responsible to respond with OSD or Error Codes, based upon project
    agent_cls = convert_str_to_class(i_face)
    if 'error' == agent_cls:
        logger.error("Can't convert str to class" + str(i_face))
        shutdown_monitor("Can't convert str to class")

    # INIT OSD SERVER INTERFACE
    try:
        agent = agent_cls(agent_uri)
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class agent class()")

    # INIT CPE STATE DATABASE
    # status db holds the cpe processing state and time
    try:
        status_db = CPEStatus()
    except(RuntimeError, TypeError, NameError):
        logger.error("An exception occurred")
        shutdown_monitor("An exception occurred with class CPEStatus()")
    while True:  # TODO, to define this better once rule engine is up
        for cpe_id in cpe_id_list:
            logger.info("Processing CPE_ID  " + str(cpe_id))
            process_cpe(cpe_id, logdb, general_uc_supported, analyser, agent, status_db)
        logger.info("All CPE's are processed, checking if any new CPE is added in rules engine")
        sleep(60)



if __name__ == '__main__':
    # Starting the monitor here
    logger.info("****** Monitor Init *******")
    monitor_main()
