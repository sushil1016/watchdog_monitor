import requests
import logging.config


logging.config.fileConfig("logger.conf")
logger = logging.getLogger("MONITOR")
logger.raiseExceptions = False

STATUS_HTTP_OK = 200
STATUS_CONNECTION_ERROR = 420


class HttpRequest(object):
    def __init__(self, uri):
        self.uri = uri
        logger.info("** HttpRequest is initialised with ** "+uri)

    def make_request(self, method, url_resource, *args, **kwargs):

            username = kwargs.get('username', None)
            password = kwargs.get('password', None)
            headers = kwargs.get('headers', {'content-type': 'text/plain'})
            body = kwargs.get('body', None)

            request_method = {'GET': requests.get, 'POST': requests.post, 'PUT': requests.put, 'DELETE': requests.delete}

            request_url = self.uri + url_resource

            req = request_method[method]
            logger.info("making a " + method + " call to " + request_url)

            try:
                res = req(request_url, data=body, headers=headers, auth=(username,password))
            except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                data = {'has_error': True, 'status_code': STATUS_CONNECTION_ERROR}
                logger.error("Request not processed, server down or incorrect url")
                return data

            logger.info("Request succeeded " + str(res.status_code))
            if STATUS_HTTP_OK == res.status_code:
                try:
                    data = {'has_error': False, 'status_code': res.status_code}
                    data.update(res.json())
                except:
                    data = {'has_error': True, 'status_code': res.status_code}
                    logger.error("Unable to read server response")
            else:
                data = {'has_error': True, 'status_code': res.status_code}
                logger.error("HTTP Error occurred " + str(res.status_code))

            return data
