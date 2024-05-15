#from gevent import monkey
#monkey.patch_all()

#import eventlet
#eventlet.monkey_patch()

import pandas as pd
import logging
import os

from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify

from threading import Thread, Event
from estimator import estimate
from data_stream import DataStream, Config
from queue import Queue
from datetime import datetime


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

csv_download_count = 0

data_queue = Queue()

@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@app.route('/save_csv', methods=['POST'])
def save_csv():
    data = request.get_json()
    df = pd.DataFrame(data)
    
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_path = os.path.join(output_dir, f'{timestamp}.csv')

    # Save DataFrame to CSV
    df.to_csv(file_path, index=False)
    
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
    print('Flask Client connected')
    loc_config = Config(_name = "Location Stream", xmin = -2.0, xmax = 2.0, ymin = -2.0, ymax = 2.0)
    DataStream(loc_config, data_queue, socketio).start()

@socketio.on('disconnect')
def disconnect():
    print('Flask Client disconnected')

if __name__ == '__main__':
    from config_handler import ConfigHandler
    [HOST,PORT] = ConfigHandler().get_all("Flask") # pylint: disable=unbalanced-tuple-unpacking
    socketio.run(app, host=HOST, port=PORT) # SocketIOServer
