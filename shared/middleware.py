import uuid
import threading

_thread_locals = threading.local()

def get_current_trace_id():
    return getattr(_thread_locals, 'trace_id', None)

class TraceIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        trace_id = request.headers.get('X-Trace-Id')
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        _thread_locals.trace_id = trace_id
        
        response = self.get_response(request)
        response['X-Trace-Id'] = trace_id
        return response
