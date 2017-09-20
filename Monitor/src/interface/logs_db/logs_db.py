import logging.config
from http_request import *
from time import sleep

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False

STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420


class LogsDB(HttpRequest):
    def __init__(self,uri,version):
        self.logdb_uri = uri
        self.version = version
        HttpRequest.__init__(self, uri)

    def get_indexes(self, cpe_id, from_date, **kwargs):
        to_date = kwargs.get('to_date', None)
        ret_value = True, []
        while True:
            # http://10.197.54.164:9200/_cat/indices/1*?format=json
            json_response = LogsDB.make_request(self, 'GET', '/_cat/indices/' + str(1) + '*'+'?format=json')
            if json_response['status_code'] == status_codes['STATUS_OK']:
                if not json_response['has_error']:
                    logger.info("successful server response= " + str(json_response))
                    if json_response["indices"]:
                        index_list = json_response["indices"]
                        ret_value = False, index_list
                    else:
                        logger.error("No index found in response")
                else:
                    logger.error("Invalid JSON response in log db response")
            elif json_response['status_code'] == status_codes['CONNECTION_REFUSED']:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("HTTP Error"+str(json_response['status_code']))
            break
        return ret_value
        # TODO Handle all http error cases

