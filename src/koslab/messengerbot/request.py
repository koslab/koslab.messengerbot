
class WebObRequestAdapter(object):
    def __init__(self, request):
        self.request = request

    def get(self, key):
        return self.request.GET.get(key)

    @property
    def body(self):
        return self.request.body

    @property
    def method(self):
        return self.request.method

class Response(object):
    def __init__(self, body=None, status=None, headerlist=None,
            content_type=None):
        self.body = body
        self.status = status
        self.headerlist = headerlist
        self.content_type = content_type

    def params(self):
        return {
            'body': self.body,
            'status': self.status,
            'headerlist': self.headerlist,
            'content_type': self.content_type
        }
