import logging.config
from time import sleep
from http_request import *

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False

STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420


class Analyser(HttpRequest):
    def __init__(self, uri, version, project):
        self.analyser_uri = uri
        self.version = version
        self.project = project
        HttpRequest.__init__(self, uri)

    def add_job_to_analyser(self, data):
        ret_value = True, ''
        while True:
            logger.info("Adding JOB to Analyser" + str(data))
            json_response = Analyser.make_request(self, 'POST', '/job', body=data)
            if json_response['status_code'] == status_codes['STATUS_OK']:
                if not json_response['has_error']:
                    logger.info("Job has been Added server response= " + str(json_response))
                else:
                    logger.info("Invalid JSON response in configuration response, can be ignored")
                ret_value = False, json_response
                break
            elif json_response['status_code'] == status_codes['CONNECTION_REFUSED'] \
                    or json_response['status_code'] == status_codes['INTERNAL_SERVER_ERROR']:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(20)
                continue
            else:
                logger.fatal("HTTP Error" + str(json_response['status_code']))
                ret_value = True, json_response
                break
        return ret_value
