import logging.config
import sys
from time import sleep

sys.path.append("interface")
from http_request import HttpRequest

STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class RulesEngine(HttpRequest):
    def __init__(self, uri, port):
        self.rule_engine_uri = uri
        self.rule_engine_port = port
        HttpRequest.__init__(self, uri + ':' + port)

    def get_project_name(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/project')
        for key, value in json_response.items():
            if "error_code" == key:
                return 'error'
            elif "project" == key:
                return value
        logger.error("No project found in response")
        return 'error'
    # TODO: Recursive calls if connection errors and http error handling

    def get_proxy_agent_name(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/interface')
        for key, value in json_response.items():
            if "error_code" == key:
                return 'error'
            elif "interface" == key:
                return value
        logger.error("No interface found in response")
        return 'error'
    # TODO: Recursive calls if connection errors and http error handling

    def get_proxy_agent_uri(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/interface_uri')
        for key, value in json_response.items():
            if "error_code" == key:
                return 'error'
            elif "interface_uri" == key:
                return value
        logger.error("No interface uri found in response")
        return 'error'
    # TODO: Recursive calls if connection errors and http error handling

    def get_logs_db_uri(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/logdb_uri')
        if json_response['status_code'] == STATUS_HTTP_OK:
            for key, value in json_response.items():
                if "error_code" == key:
                    return 'error'
                elif "logdb_uri" == key:
                    return value
            logger.error("No logdb_uri found in response")
            return 'error'
        elif json_response['status_code'] == STATUS_CONNECTION_ERROR:
            logger.error("Connection Refused, Trying Again!!!")
            sleep(2)
            RulesEngine.get_logs_db_uri(self)
        else:
            logger.fatal("HTTP Error"+str(json_response['status_code']))
            return 'error'
            # TODO Handle all http error cases

    def get_analyser_uri(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/analyser_uri')
        for key, value in json_response.items():
            if "error_code" == key:
                return 'error'
            elif "analyser_uri" == key:
                return value
        logger.error("No analyser uri found in response")
        return 'error'
    # TODO: Recursive calls if connection errors and http error handling

    def get_cpe_ids(self):
        json_response = RulesEngine.make_request(self, 'GET', '/get/cpe_ids')
        for key, value in json_response.items():
            if "error_code" == key:
                return 'error'
            elif "cpe_ids" == key:
                return value
        logger.error("No cpe_ids found in response")
        return 'error'
    # TODO: Recursive calls if connection errors and http error handling

    def is_general_uc_supported(self):
        return True
    # TODO: GET call to RE. Recursive calls if connection errors and http error handling

