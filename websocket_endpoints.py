import os
from eventlet import websocket, greenthread
import traceback

@websocket.WebSocketWSGI
def startTimer(ws):
    n_cnt = 0
    global execTimer
    while execTimer:
        print('Timer fired! {}'.format(n_cnt))

        greenthread.sleep(1)
        n_cnt+=1

        try:
            ws.send('Timer fired! {}'.format(n_cnt))
        except Exception as e:
            print('Client websocket not available')
            ws.close()
            return

@websocket.WebSocketWSGI
def processMessage(ws):
    m = ws.wait()
    print('Message received: {}'.format(m))

       
@websocket.WebSocketWSGI
def saveData(ws):
    filename = ws.wait()
    print('Filename: {}'.format(filename))
    data = ws.wait()
    data_size = float(len(data)) / 1000 #kb
    print('Sizeof data: {:.1f} kb'.format(data_size))
    new_file = os.path.join(os.path.expanduser('~'), filename)
    print('Upload saved to: {}'.format(new_file))
    with open(new_file, 'wb') as file:
        file.write(data)


def dispatch(environ, start_response):

    """
        WEBSOCKETS
    """

    global execTimer

    try:
        if environ['PATH_INFO'] == '/data':
            print('PATH_INFO == \'/data\'')
            return saveData(environ, start_response)
        elif environ['PATH_INFO'] == '/message':
            print('PATH_INFO == \'/message\'')
            return processMessage(environ, start_response)
        elif environ['PATH_INFO'] == '/timer':
            print('PATH_INFO == \'/timer\'')
            if execTimer:
                execTimer = False
                start_response('200 OK', [])
                return []
            else:
                execTimer = True
                return startTimer(environ, start_response)

            """
                STANDARD HTML ENDPOINTS
            """

        elif environ['PATH_INFO'] == '/':
            print('PATH_INFO == \'/\'')
            start_response('200 OK', [('content-type', 'text/html')])
            return [open(os.path.join(os.path.dirname(__file__),
                'frontend-app/OdsValidatorFrontend.html')).read()]
    
        elif environ['PATH_INFO'] == '/qtloader.js':
            print('PATH_INFO == \'/qtloader.js\'')
            str_data = open(os.path.join(os.path.dirname(__file__),
                'static/qtloader.js')).read() 
            start_response('200 OK', [('content-type', 'application/javascript') ])

            return [str_data]

        elif environ['PATH_INFO'] == '/qtlogo.svg':
            print('PATH_INFO == \'/qtlogo.svg\'')
            img_data = open(os.path.join(os.path.dirname(__file__),
                'static/qtlogo.svg'), 'rb').read() 
            start_response('200 OK', [('content-type', 'image/svg+xml'),
                                    ('content-length', str(len(img_data)))])

            return [img_data]

        elif environ['PATH_INFO'] == '/favicon.ico':
            print('PATH_INFO == \'/favicon.ico\'')
            img_data = open(os.path.join(os.path.dirname(__file__),
                'static/qtlogo.svg'), 'rb').read() 
            start_response('200 OK', [('content-type', 'image/svg+xml'),
                                    ('content-length', str(len(img_data)))])

            return [img_data]

        elif environ['PATH_INFO'] == '/OdsValidatorFrontend.js':
            print('PATH_INFO == \'/OdsValidatorFrontend.js\'')
            str_data = open(os.path.join(os.path.dirname(__file__),
                'static/OdsValidatorFrontend.js')).read() 
            start_response('200 OK', [('content-type', 'application/javascript')])
            return [str_data]

        elif environ['PATH_INFO'] == '/OdsValidatorFrontend.wasm':
            print('PATH_INFO == \'/OdsValidatorFrontend.wasm\'')
            bin_data = open(os.path.join(os.path.dirname(__file__),
                'static/OdsValidatorFrontend.wasm'), 'rb').read() 
            start_response('200 OK', [('content-type', 'application/wasm')])
            return [bin_data]		

        else:
            path_info = environ['PATH_INFO']
            print('PATH_INFO = {}'.format(path_info))
            return None
    except Exception as _:
        print(str(traceback.format_exc()))