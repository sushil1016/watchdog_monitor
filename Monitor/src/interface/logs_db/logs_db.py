import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class LogsDB:
    def __init__(self,uri):
        self.logdb_uri =uri

    def master_db_has_logs(self,cpe_id, processed_date):
        return True
    #TODO GET Rest API to logs db and http error handling