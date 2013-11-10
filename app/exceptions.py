class HttpException(Exception):
    def __init__(self, message = "Internal Error", code = 500, http_headers = None):
        self._code = code
        ## Accepts dict of custom http headers
        if http_headers:
            self._headers = http_headers
        Exception.__init__(self, message)

    def getHttpCode(self):
        return self._code

class Http403(HttpException):
    def __init__(self, message = "Forbidden", http_headers = None):
        HttpException.__init__(self, message, code = 403, http_headers = http_headers)

class Http404(HttpException):
    def __init__(self, message = "Not found", http_headers = None, id = None):
        if id:
            message += ": " + id
        HttpException.__init__(self, message, code = 404, http_headers = http_headers)

