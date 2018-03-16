import logging.config
import ConfigParser
import string
from util.Utility import *
import sys
import os
from interface.ftp.ftplogserver import *
from interface.yard.yardlogserver import *
from interface.ruleengine.RulesEngineClient import *
from  Decoder.Decoder import *
from subprocess import call
from db.PickleData import *
from time import sleep

WAIT_BEFORE_RETRY=20

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("Retriever")
logger.debug('successfully Loaded logger.conf')



def getConfigFileInfo():
    config = {}
    cp = ConfigParser.ConfigParser()
    cp.read("config.cfg")
    for sec in cp.sections():
        name = string.lower(sec)
        for opt in cp.options(sec):
            config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
            logger.debug('Section: %s,  Field: %s, Value: %s',name, string.lower(opt), string.strip(cp.get(sec, opt)))
    return config


if __name__ == '__main__':
    # called when standalone:
    rulesEngine = RulesEngineClient()
    configinfo = getConfigFileInfo()
    # The Diag_builds folder contains diag parsers which are downloaded from Build server.
    # User can manually copy it here.
    createDirectory('./Diag_builds')
    retriver_dir = os.getcwd()
    logger.info("Retriever Dir  %s", retriver_dir)

    ServerUrl = constructFullUri(configinfo.get('retriever.rulesengine'), configinfo.get('retriever.serverurl'))
    logger.info("ServerUrl  %s", ServerUrl)

    DeviceUrl = constructFullUri(configinfo.get('retriever.rulesengine'), configinfo.get('retriever.deviceurl'))
    logger.info("DeviceUrl  %s", DeviceUrl)

    if not DeviceUrl or not ServerUrl:
        logger.error("Do not start Retriever")

    decoder = Decoder()
    if 'yes' == configinfo.get('retriever.enable_logstash'):
        if decoder.run_logstash():
            logger.info("logstash triggered")
        else:
            logger.error("can't start logstash, please check logstash logs... still download logs..")

    # Monitor for logs
    while True:  # Master loop to keep the retriever alive
        CPE_info     = []
        CPE_ID_list  = []
        CPE_MAC_list = []
        os.chdir(retriver_dir)
        logger.info("Fetch CPE list to be monitor for logs from Rules Engine")
        CPE_info, CPE_ID_list,CPE_MAC_list = rulesEngine.get_CPE_list(DeviceUrl)

        logger.debug("CPE_ID list %s", CPE_ID_list)
        logger.debug("CPE_MAC list %s", CPE_MAC_list)

        if CPE_info:
            logger.info("Fetch all servers info from Rules Engine")
            if not rulesEngine.get_servers_info(ServerUrl):
                logger.error("Error fetching servers, trying again in 30 seconds")
                sleep(WAIT_BEFORE_RETRY)
                continue

            log_server_str = rulesEngine.get_project_log_server_name()
            logger.info("log server %s found ", log_server_str)

            # logServer can be any interface which is responsible to host log files, based upon project
            log_server_cls = eval(log_server_str)

            log_server_hostname = rulesEngine.get_project_log_server_hostname()
            log_server_user = rulesEngine.get_log_server_user()
            log_server_password = rulesEngine.get_project_log_server_password()

            if not log_server_hostname or not log_server_user or not log_server_password:
                logger.error("log server credentials missing... trying again")
                sleep(WAIT_BEFORE_RETRY)
                continue

            # Dynamically instantiate the class of log server...
            logServer = log_server_cls(log_server_hostname, log_server_user, log_server_password)

            # Establish a login session with the log server
            if not logServer.login():
                logger.error("Error logging into the logserver %s.. try again after some time", log_server_str)
                sleep(WAIT_BEFORE_RETRY)
                del logServer
                continue

            # Read local configuration settings of log server
            if not logServer.read_local_config():
                logger.error("Error reading local config settings of logserver %s.. try again after some time", log_server_hostname)
                sleep(WAIT_BEFORE_RETRY)
                logServer.logout()
                del logServer
                continue

            # Grab the already processed log file names, to avoid duplicates
            parsed_file_list = get_parsed_file_list()
            logger.info("already parsed files %s", parsed_file_list)

            # Construct the list of files which are to be downloaded from the remote server
            file_list = logServer.get_file_list(CPE_MAC_list, parsed_file_list)

            if file_list:
                logger.info("got total %s files",len(file_list))
                for filename in file_list:
                    print ("\n\n\n -------------------- \n\n\n")
                    logger.info("Start Processing the file %s ", filename)

                    # Create temporary directory or clean if already exist
                    make_empty_directory('./Logs_To_Parse')
                    createDirectory('./Logs_To_Parse')

                    os.chdir('./Logs_To_Parse')

                    if logServer.download_file(filename):
                        if not logServer.process_log_file(decoder, rulesEngine, filename, retriver_dir):
                            logger.error(" *** Can't process file [%s] trying next ***", filename)
                            break
                    else:
                        logger.error(" *** Can't download file [%s] trying next ***",filename)
                        break

                    os.chdir(retriver_dir)
                    if not store_parsed_file(filename):
                        logger.error("filename %s not stored in pickle data file.", filename)

            else:
                logger.info("Logs file list is empty. Sleep for 10 minutes")
                sleep(600)
                logServer.logout()
                del logServer
                continue
        else:
            logger.error("There is no project CPE IDs from Rules Engine. Try after 30 seconds")
            sleep(30)
            continue
        
	logger.info("Parsing completed for current files. Search for new list of files in FTP server")
        sleep(300)
        logServer.logout()
        del logServer
