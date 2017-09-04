# -*- coding: utf-8 -*-

import os
import sys
import logging.config

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

sys.path.append("interface")
from http_request import HttpRequest
STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False

parser = configparser.ConfigParser()

'''
PH Server response codes
200	OK	Operation completed successfully
400	Bad request	Missing arguments
404	Not found	Requested device not found
401	Unauthorized	Unauthorized
412	Precondition failed	Invalid arguments (e.g. wrong input format)
501	Internal server error	Internal error
'''


class PHProxy(HttpRequest):
    def __init__(self, uri):
        HttpRequest.__init__(self, uri)

    def read_config(self):
        logger.info("Invoked PH Proxy")
        config = 'interface/ph_proxy/ph.cfg'
        global USERNAME
        global PASSWORD
        if os.path.exists(config):
            parser.read(config)
        else:
            raise IOError('Ph Proxy Config File does not exists')
        try:
            USERNAME = parser.get('PH_PROXY', 'username')
            PASSWORD = parser.get('PH_PROXY', 'password')
        except:
            raise configparser.NoSectionError('No such section in config file')

    def get_osd_messages(self, cpe_id, days_back=100):
        ph_uri='ph.com'
        logger.info("Fetching OSD errors from server, for cpe " + str(cpe_id) + "from last " +str(days_back) + " days")
        # [http://localhost:9090/panorama-ui/nbi/netmap/v1.1/json/device/{device-id}/osd?staleness={n}&daysBack={n}]
        # staleness=1d i.e.: If the required staleness level is 2 hours, then all parameters that were retrieved more
        # than 2 hours ago will be retrieved from device, and the others – from the database.
        # logger.info("Invoked PH proxy methods")

        get_osd_uri = ph_uri + '/' + 'panorama-ui' + '/nbi' + '/netmap' + '/v1.1' + '/json' + '/device/' + str(cpe_id) + '/osd' + '?staleness=' + '0' +'&daysBack=' + '1'
        logger.info('get osd uri' + str(get_osd_uri))
        json_response = PHProxy.make_request(self, 'GET', '/get/osd')
        osd_err_code_list = []
        if json_response['status_code'] == STATUS_HTTP_OK:
            for doc in json_response['osdMessages']:
                osd_err_code_list.append(doc['code'])
                logger.info("osd error list=" + str(osd_err_code_list))
        return osd_err_code_list
