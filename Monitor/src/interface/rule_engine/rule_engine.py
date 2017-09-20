import logging.config
import sys
from time import sleep

sys.path.append("interface")
from http_request import HttpRequest

STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420
INTERNAL_SERVER_ERROR = 501

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class RulesEngine(HttpRequest):
    def __init__(self, uri, port):
        self.rule_engine_uri = uri
        self.rule_engine_port = port
        HttpRequest.__init__(self, uri + ':' + port)

    def get_configuration(self):
        ret_value = True, ''
        while True:
            json_response = RulesEngine.make_request(self, 'GET', '/smartmonitor/rules-engine/v1.0/configuration')
            if json_response['status_code'] == STATUS_HTTP_OK:
                if not json_response['has_error']:
                    logger.info("successful server response= " + str(json_response))
                    ret_value = False, json_response
                else:
                    logger.error("Invalid JSON response in configuration response")
                break
            elif json_response['status_code'] == STATUS_CONNECTION_ERROR \
                    or json_response['status_code'] == INTERNAL_SERVER_ERROR:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("HTTP Error" + str(json_response['status_code']))
                ret_value = True, json_response
                break
        return ret_value

    def get_cpe_ids(self):
        ret_value = True, []
        while True:
            json_response = RulesEngine.make_request(self, 'GET', '/smartmonitor/rules-engine/v1.0/devices')
            if json_response["status_code"] == STATUS_HTTP_OK:
                if not json_response["has_error"]:
                    logger.info("successful server response= " + str(json_response))
                    if json_response["cpe_ids"]:
                        cpe_id_list = json_response["cpe_ids"]
                        ret_value = False, cpe_id_list
                    else:
                        logger.error("No cpe_ids found in response")
                else:
                    logger.error("Invalid JSON response in configuration response")
            elif json_response['status_code'] == STATUS_CONNECTION_ERROR \
                    or json_response['status_code'] == INTERNAL_SERVER_ERROR:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("HTTP Error"+str(json_response['status_code']))
            break
        return ret_value

    def get_cpe_rules(self, cpe_id, server_err_list):
        ret_value = True, [], []  # True indicates error state
        while True:
            json_response = RulesEngine.make_request(self, 'GET', '/smartmonitor/rules-engine/v1.0/devices/' + str(cpe_id) + '/rules')
            if json_response['status_code'] == STATUS_HTTP_OK:
                if not json_response['has_error']:
                    logger.info("server response= " + str(json_response))

                    try:
                        #forced_sampling = json_response['enforceRule']
                        rules_map_err_list = []
                        for item in json_response['rulesMap']:
                            rules_map_err_list.append(item['error'])

                        logger.info("error list from rulesMap is "+str(rules_map_err_list))
                    except:
                        logger.fatal("Error reading data from json")
                        break

                    common_err_list = list((set(server_err_list).intersection(rules_map_err_list)))
                    uncommon_err_list = list((set(server_err_list).difference(common_err_list)))

                    logger.info("Sampling to be run on common errors from ruleMap and serverOSD I.e."
                                " "+str(common_err_list))
                    logger.info("Usual processing to be run on server OSD's which are not to be sampled"
                                " by ruleMap I.e. " + str(uncommon_err_list))

                    sampling_info_list = []  # Contains list of dictionary containing sampling information
                    if common_err_list:
                        try:
                            for osd in common_err_list:
                                for err in json_response['rulesMap']:
                                    if err['error'] == osd:
                                        info = dict()
                                        info['error'] = err['error']
                                        info['from_date'] = err['timeFrom']
                                        info['to_date'] = err['timeTo']
                                        sampling_info_list.append(info)
                        except:
                            logger.fatal("Error reading server response ")
                            break

                    if sampling_info_list:
                        logger.info("Sampling to be performed on "+str(sampling_info_list))
                    ret_value = False, uncommon_err_list, sampling_info_list
                else:
                    logger.error("Not a valid json as a response to get_cpe_rules api")
            elif json_response['status_code'] == STATUS_CONNECTION_ERROR \
                    or json_response['status_code'] == INTERNAL_SERVER_ERROR:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("HTTP Error" + str(json_response['status_code']))
            break
        return ret_value

    def get_cpe_usecases(self, cpe_id, err_code):
        ret_value = True, []
        while True:
            json_response = RulesEngine.make_request(self, 'GET', '/smartmonitor/rules-engine/v1.0/errors/'
                                                     + str(err_code))
            logger.info("server response= " + str(json_response))
            if json_response['status_code'] == STATUS_HTTP_OK:
                if not json_response['has_error']:
                        usecase_map_list = json_response['usecaseMap']
                        ret_value = False, usecase_map_list
                else:
                    logger.error("Not a valid json as a response to get_cpe_usecases api")
            elif json_response['status_code'] == STATUS_CONNECTION_ERROR \
                    or json_response['status_code'] == INTERNAL_SERVER_ERROR:
                logger.error("Connection Refused, Trying Again!!!")
                sleep(5)
                continue
            else:
                logger.fatal("HTTP Error" + str(json_response['status_code']))
            break
        return ret_value

    def is_general_uc_supported(self):
        return False
    # TODO: impliment this function based on rule engine

