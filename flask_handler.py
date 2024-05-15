#from gevent import monkey
#monkey.patch_all()

#import eventlet
#eventlet.monkey_patch()

import pandas as pd
import logging

from flask_socketio import SocketIO, emit
from flask import Flask,Response, render_template, url_for, copy_current_request_context, request, jsonify

from threading import Thread, Event
from scheduler import scheduler
from socket_server import SocketServer
from estimator import estimate
from data_stream import DataStream, Config
from queue import Queue

"""
Flask handler manages the start and connection to Flask website/server.
"""

app = Flask(__name__)
app.config['DEBUG'] = False # let this be false to only start one webbrowser
app.config['THREADED'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode="threading")

thread = Thread() # scheduler thread
thread_stop_event = Event()

csv_download_count = 0

data_queue = Queue()

#lock = threading.Lock()

def start_flask_application():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    from config_handler import ConfigHandler
    [HOST,PORT] = ConfigHandler().get_all("Flask") # pylint: disable=unbalanced-tuple-unpacking
    socketio.run(app, host=HOST, port=PORT) # SocketIOServer
    app.run(host=HOST, port=PORT) # Other Server

@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

# For camear
vcapture_list = []
def gen(device):
    import cv2
    try:
        if(device in vcapture_list):
            print("Device stream already streaming " + str(device))
        vcap = cv2.VideoCapture(device)
        vcapture_list.append(device)
        while True:
            ret, frame = vcap.read()
            if frame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')
    except Exception:
        print("Capture failed " + str(device))

@app.route('/video_feed/<device>')
def video_feed(device):
    # return the response generated along with the specific media
    # type (mime type)
    print(device)
    device = device.replace("skipableslash","/")
    print(device)
    try:
        return Response(gen(int(device)),mimetype = "multipart/x-mixed-replace; boundary=frame")
    except Exception:
        return Response(gen(device),mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/save_csv', methods=['POST'])
def save_csv():
    global csv_download_count
    csv_download_count += 1

    data = request.get_json()
    df = pd.DataFrame(data)
    df.to_csv('output/{}.csv'.format(csv_download_count))
    
    return jsonify(message='CSV file saved successfully')

@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    df = pd.DataFrame(data)
    displayed_df = df if len(df) < 10 else df.tail(10)

    try:
        bias, weight, xplot_min, yplot_min, xplot_max, yplot_max = estimate(displayed_df['x'].to_numpy(), displayed_df['y'].to_numpy()) # curve estimator is y = mx + b
    except Exception as e:
        return jsonify({'error': str(e)})
     
    return jsonify({
        'bias': bias,
        'weight': weight,
        'xplot_min': xplot_min,
        'yplot_min': yplot_min,
        'xplot_max': xplot_max,
        'yplot_max': xplot_max
    })

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    # Extract values from the incoming request
    timestamp = data.get('time')
    x = data.get('x')
    y = data.get('y')
    lon = data.get('lon')
    lat = data.get('lat')
    heigh = data.get('heigh')
    rtk = data.get('rtk')
    hrms = data.get('hrms')
    vrhms = data.get('vhrms')
    
    # Put data into the queue
    data_queue.put((timestamp, x, y, lon, lat, heigh, rtk, hrms, vrhms))
    
    return jsonify(message='Data received successfully')

@socketio.on('connect')
def connect():
    # need visibility of the global thread object
    global thread
    print('Flask Client connected')

    if not thread.is_alive():
        loc_config = Config(_name = "Location Stream", xmin = -2.0, xmax = 2.0, ymin = -2.0, ymax = 2.0)
        DataStream(loc_config, data_queue).start()

    #Start the generator threads only if the thread has not been started before.
    #if not thread.is_alive():
    #    scheduler()

@socketio.on('disconnect')
def disconnect():
    print('Flask Client disconnected')
