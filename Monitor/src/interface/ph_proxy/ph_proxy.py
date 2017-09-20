# -*- coding: utf-8 -*-

import os
import sys
import logging.config
from time import sleep

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

sys.path.append("interface")
from http_request import *

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
    def __init__(self, uri, version, username, password):
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

    def get_err_timestamp_map(self, cpe_id, days_back=100):
        ph_uri='ph.com'
        logger.info("Fetching OSD errors from server, for cpe " + str(cpe_id) + "from last " +str(days_back) + " days")
        # [http://localhost:9090/panorama-ui/nbi/netmap/v1.1/json/device/{device-id}/osd?staleness={n}&daysBack={n}]
        # staleness=1d i.e.: If the required staleness level is 2 hours, then all parameters that were retrieved more
        # than 2 hours ago will be retrieved from device, and the others – from the database.
        # logger.info("Invoked PH proxy methods")

        get_osd_uri = ph_uri + '/' + 'panorama-ui' + '/nbi' + '/netmap' + '/v1.1' + '/json' + '/device/' + str(cpe_id) + '/osd' + '?staleness=' + '0' +'&daysBack=' + '1'
        logger.info('get osd uri' + str(get_osd_uri))
        ret_value = True, [], []
        while True:
            json_response = PHProxy.make_request(self, 'GET', '/v1.1/json/device/' + str(cpe_id) + '/osd?staleness=*&daysBack=*')
            if json_response['status_code'] == status_codes['STATUS_OK']:
                logger.info("successful server response "+str(json_response))
                if json_response['has_error']:
                    logger.fatal("error reading server response")
                else:
                    try:
                        err_to_time_map = dict()
                        err_list = []
                        for doc in json_response["osdMessages"]:
                            info = dict()
                            info[doc["code"]] = doc["timestamp"]
                            err_to_time_map.update(info)
                            err_list.append(doc["code"])
                        logger.info("osd error list=" + str(err_to_time_map))
                        ret_value = False, err_list, err_to_time_map
                    except:
                        logger.fatal("unable to read json doc")
                        ret_value = True, [], []
                break
            elif json_response['status_code'] == status_codes['CONNECTION_REFUSED']:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("Client Error in http response " + str(json_response['status_code']))
                break
        return ret_value
