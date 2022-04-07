import eventlet, os
from websocket_endpoints import dispatch
from eventlet import wsgi

execTimer = False		

if __name__ == '__main__':
    print(f"Hosting on port: {int(os.environ.get('PORT', 80))}")
    listener = eventlet.listen(('0.0.0.0', int(os.environ.get("PORT", 80))))
    wsgi.server(listener, dispatch)
