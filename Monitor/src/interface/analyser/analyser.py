import requests

import logging, logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class Analyser:
    def __init__(self,uri):
        self.analyser_uri =uri

    def add_job_to_analyser(self, cpe_id, use_case="regular"):
        logger.info("Adding JOB to Analyser cpe_id=" + str(cpe_id) + "osd=" + str(use_case))
        # TODO POST request using HTTP base class also accept the
        return True
