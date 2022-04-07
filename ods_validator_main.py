import eventlet, os
from websocket_endpoints import dispatch
from eventlet import wsgi


execTimer = False		

if __name__ == '__main__':
    print(f"Hosting on port: {int(os.environ.get('PORT', 80))}")
    listener = eventlet.listen(('0.0.0.0', int(os.environ.get("PORT", 80))))
    print('\nVisit http://localhost:7000/ in your websocket-capable browser.\n')
    wsgi.server(listener, dispatch)
