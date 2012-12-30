import httplib2
import json


class RestClient:
    ''' A JSON based REST client.

    '''

    def __init__(self, host="127.0.0.1"):
        self.conn = httplib2.Http()
        self.conn.force_exception_to_status_code = True
        self.system_url = "http://" + host

    def get(self, uri):
        ''' Retrieve the resource located at the URI.

            Keyword arguments:
            uri  -- the location of the resource being requested

            Return values:
            On success: a dictionary containing requested resource
            On failure: RestError object
        '''
        resp, cont = self._request(uri, "GET")

        if resp.status == 200 and resp['content-type'] == 'application/json':
            return json.loads(cont)
        else:
            return RestError(resp, uri)

    def post(self, uri, data):
        ''' Create a new resource at the given URI.

            Keyword arguments:
            uri  -- the location where the resource will be created
            data -- a dictionary containing the new resource

            Returns a dictionary containing the new resource
        '''
        formatted_data = json.dumps(data)
        resp, cont = self._request(uri, "POST", formatted_data)

        if resp.status == 200 and resp['content-type'] == 'application/json':
            return json.loads(cont)
        else:
            return RestError(resp, uri)

    def delete(self, uri):
        ''' Delete the resource at the given URI

            Keyword arguments:
            uri -- the location of the resourse to be updated

            Returns boolean value that indicate whether the resource was successfully deleted
        '''
        resp, cont = self._request(uri, "DELETE")

        if resp.status == 200:
            return True
        else:
            return False

    def _request(self, uri, method, data=None, headers=None):
        uri = self.system_url + uri
        headers = {'Content-Type': 'application/json'}
        return self.conn.request(uri, method, data, headers)


class RestError:

    def __init__(self, response, url):

        self.url = url
        self.status = response.status
        self.reason = response.reason
