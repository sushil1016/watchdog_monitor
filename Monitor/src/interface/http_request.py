import requests
import logging.config
import json

status_codes = {
        'STATUS_OK': 200, 'CONNECTION_REFUSED': 420, 'BAD_REQUEST': 400,
        'INTERNAL_SERVER_ERROR': 501
    }

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False


class HttpRequest(object):

    def __init__(self, uri):
        self.uri = uri
        logger.info("** HttpRequest is initialised with ** "+uri)

    def make_request(self, method, url_resource, *args, **kwargs):

            username = kwargs.get('username', None)
            password = kwargs.get('password', None)
            headers = kwargs.get('headers', {'Content-Type': 'application/json'})
            body = kwargs.get('body', None)

            request_method = {'GET': requests.get, 'POST': requests.post, 'PUT': requests.put,
                              'DELETE': requests.delete}

            request_url = self.uri + url_resource

            req = request_method[method]
            logger.info("making a " + method + " request to " + request_url)

            try:
                res = req(request_url, data=body, headers=headers, auth=(username,password))
            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                data = {'has_error': True, 'status_code': status_codes['CONNECTION_REFUSED']}
                logger.error("Request not processed, server down or incorrect url")
                return data

            logger.info("Request succeeded: http status " + str(res.status_code))
            if status_codes['STATUS_OK'] == res.status_code:
                try:
                    data = {'has_error': False, 'status_code': res.status_code}
                    try:
                        data.update(res.json())
                    except:
                        # Some servers might report array of json objects
                        json_item_list = []
                        label = ""
                        for key in res.json():
                            try:
                                if key['cpeid']:
                                    json_item_list.append(key['cpeid'])
                                    label = "cpe_ids"
                            except:
                                if key['index']:
                                    json_item_list.append(key['index'])
                                    label = "indices"
                        data.update({label: json_item_list})
                except:
                    data = {'has_error': True, 'status_code': res.status_code}
                    logger.error("Unable to read server response, please check the json response")
            else:
                data = {'has_error': True, 'status_code': res.status_code}
                logger.error("HTTP Error occurred " + str(res.status_code))

            return data
