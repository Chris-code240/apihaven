import threading

_local = threading.local()

def get_current_request():
    return getattr(_local, 'request', None)

def set_current_project(project_id):
    _local.project_id = project_id

def get_current_project():
    return getattr(_local, 'project_id', None)

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.request = request
        _local.project_id = request.headers.get("X-Project-ID")  # for example
        return self.get_response(request)


"""
Everytime a request comes in, save it in _local.request

We can always use get_cuurent_request() to get it, so far as we are in the same thread.
"""