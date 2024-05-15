from threading import Thread
import flask_handler
from datetime import datetime
import time
import threading
"""
This file contains some data structures for better implementation structure.
"""

class Config():
    # Describes the visuals of graphs
    def __init__(self, _id= 0, _type = 'scatter', _active_points = 10,
     _delay = 1, _name = "RealtimeGraph", _label=["Value"], _legend=["data"],
      _width = 200, _height = 100, backgroundColor = ["rgb(255, 99, 132)"],
       borderColor = ["rgb(255, 99, 132)"], fill = "false", 
       xmin = -1.0, xmax = 1.0, ymin = -1.0, ymax = 1.0):
        self.type = _type
        self.active_points = _active_points
        self.delay = _delay = 1
        self.id = _id
        self.name = _name
        self.label = _label
        self.legend = _legend
        self.width = _width
        self.height = _height
        self.backgroundColor = backgroundColor
        self.borderColor = borderColor
        self.fill = fill
        self.xmin = xmin
        self.xmax = xmax 
        self.ymin = ymin 
        self.ymax = ymax

class DataStream(Thread):
    def __init__(self, _config, data_queue):
        super(DataStream, self).__init__()
        self.data_queue = data_queue
        self.config = _config

    def run(self):
        print('Data stream running')
        while not flask_handler.thread_stop_event.isSet():
            if not self.data_queue.empty():
                timestamp,x, y, lon, lat, heigh, rtk, hrms, vhrms = self.data_queue.get()
                flask_handler.socketio.emit('server',{
                    'id':self.config.id,
                    'time': [timestamp],
                    'x': [x],
                    'y': [y],
                    'lon': [lon],
                    'lat': [lat],
                    'heigh': [heigh],
                    'rtk': [rtk],
                    'hrms': [hrms],
                    'vhrms': [vhrms],
                    'type': self.config.type,
                    'active_points': self.config.active_points,
                    'label': self.config.label,
                    'legend': self.config.legend,
                    'name': self.config.name,
                    'width': self.config.width,
                    'height': self.config.height,
                    "backgroundColor": self.config.backgroundColor,
                    "borderColor" : self.config.borderColor,
                    "fill" : self.config.fill,
                    'xmin': self.config.xmin,
                    'xmax': self.config.xmax,
                    'ymin': self.config.ymin,
                    'ymax': self.config.ymax
                })
            
            time.sleep(self.config.delay)


def def_param(vari, deff):
    if vari is None:
        return deff
    else:
        return vari

def send_request(id, data, type = 'line', active_points = 20, _label="Value", _legend="data", _width = 200, _height = 100, _name = "Graph", backgroundColor = "rgb(255, 99, 132)", borderColor = "rgb(255, 99, 132)", fill = "false"):
    type = def_param(type, 'line')
    active_points = def_param(active_points, 20)
    _label = def_param(_label, ['Value'])
    _legend = def_param(_legend, ['data'])
    _height = def_param(_height, 200)
    _width = def_param(_width, 100)
    _name = def_param(_name, 'Graph')
    fill = def_param(fill, "False")
    backgroundColor = def_param(backgroundColor, ["rgb(255, 99, 132)"])
    borderColor = def_param(borderColor, ["rgb(255, 99, 132)"])

    flask_handler.socketio.emit('server',
    {'id': id,
    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
     'value': data,
     'type': type,
     'active_points': active_points,
     'label': _label,
     'legend': _legend,
     'name': _name,
     'width': _width,
     'height': _height,
     "backgroundColor": backgroundColor,
     "borderColor" : borderColor,
     "fill" : fill})
